from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
import getpass
import os
from IPython.display import Image, display
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
import chromadb
from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from dotenv import load_dotenv
import socket
from threading import Thread
import tkinter as tk
from tkinter import messagebox
import logging


#Configure logging for detailed debug output
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=".env")

def _set_env(key: str):
    if not os.environ.get(key):  # This checks for None or an empty string
        os.environ[key] = getpass.getpass(f"{key}: ")

_set_env("OPENAI_API_KEY")

model = ChatOpenAI(
    model="gpt-4o-mini",
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# State config
class State(TypedDict):

    # Messages the flow of the nodes
    messages: Annotated[list, add_messages]

    # The collection determined by the collection node
    collection_name: str

    # Retreaved docs from cosin similarity search
    docs: str

    # The final answer to the question
    final_summary: str

# Persist client for collections and local collection storage
persistent_client = chromadb.PersistentClient(path = "my_local_data")


                            ##AGENTS AND NODES##

def send_summary(state: State):


    final_summary = state.get("final_summary")

    if not final_summary:
        logger.error("No summary found")
        return ""
    
    logger.info("Sending summary")

    client.send(bytes(final_summary, "utf8"))

    #print(f"Server says: {response}")

    return {"final_summary": [final_summary]}

# Node for enhancing question for similarity search
def query_rewrite(state: State):

    logger.info("Current node: query_rewrite\n")

    # Fetch question for state
    messages = state["messages"]
    question = messages[0].content

    # Promt for the enhanced question
    msg = [
        HumanMessage(
            content=f"""
            
    Look at the input and try to reason about the underlying semantic intent / meaning. \n 
    Here is the initial question:
    \n ------- \n
    {question} 
    \n ------- \n
    Formulate an improved question: """,
        )
    ]
    
    # Sending the message to the model defined above
    response = model.invoke(msg)

    logger.info("Rewriten query: ", response.content)

    #print("Rewriten query: ", response.content)
    
    # Adding the response question to message flow in state
    return {"messages": [response]}


    

# Node responsible for finding the correct collection to query
def collection(state: State):
    

    logger.info("Current node: collection\n")

    # Class for forcing the output to be specific so that routing can be more consistant
    class collection(BaseModel):

        #Binary choice to use the rag model or not
        collection_name: str = Field(description="The collection to query 'great_gatsby' or")

    # Adding the structured output to the LLM
    llm_with_tool = model.with_structured_output(collection)
    
    # Special promtp for the specific output using PromptTemplate
    prompt = PromptTemplate(
        template=""" your goal is to analize the question given then determine what book the question is asking about
        here is the list of books to chose from:
        "'great_gatsby',
        "
        pick a book from this list and only return the books name as written in the list above thing else
        if the book being referenced in the question is not in the above list say 'END' and nothing else
        """,
        input_variables=["question"],
        )
    
    # Chain for invoking the model so it can use the structured output and the prompt
    chain = prompt | llm_with_tool

    # Fetch question from state
    messages = state["messages"]
    question = messages[0].content
    
    # Defines the correct collection and sends all info to the LLM including the question
    collection_result = chain.invoke({"question": question})

    # Defines the collection specifyed by the output schema
    collection = collection_result.collection_name

    logger.info(f"Collection: {collection}")

    # Adds the collection name to state so it can be called through conventional edges
    state_update = {
            "collection_name": collection,
    }

    # Command for updating the state
    return Command(update=state_update)



    
# preforms the cosin similarity
def similarity_search(state: State):
    
    logger.info("Current node: similarity_search\n")

    # fetch REWRIT question (better for similarity search)
    messages = state["messages"]
    question = messages[1].content

    # Pulls the collection name var from the state
    collection_name = state.get("collection_name")

    logger.info(f"Searching collection: {collection_name}")
    
    # Defines how many dimentions the embeddings should be formatted into
    dimensions = 384

    # Defines the embedding model used for future embeddings
    model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1", truncate_dim=dimensions,)

    logger.info(f"Embedding query: {question}")

    # Creates the call for the embedding model and defines embedding list 
    query_embed = model.encode(question)

    # Defines what collection will be queried 
    collection = persistent_client.get_or_create_collection(name=collection_name)

    # Similarity search
    results = collection.query(

    # Defines the embeddings used to be compaired to the collection of embeddings 
    query_embeddings = query_embed,

    # Defines the number of results from the collection
    n_results=5
    )
    
    # Doc string for the generate node
    docs = ""
    
    # Pulls documents out of weird dict structre for ease of accesess
    for x in results["documents"][0]:
        docs += x

    # State update for the docs
    state_update = {
            "docs": docs,
    }

    logger.info(f"Docs retrieved: {docs}")

    # Command for the state update
    return Command(update=state_update)



# Generate node for final summary
def generate(state: State):

    logger.info("Current node: generate\n")
    
    # fetch original question and docs
    messages = state["messages"]
    question = messages[0].content
    docs = state.get("docs")

    if not docs:
        logger.error("No documents found to summarize.")
        return ""

    if not question:
        logger.error("No question found to summarize.")
        return ""

    logger.info(f"Question for generation: {question} docs to pull from: {docs}")
    # Prompt used for summarisation
    msg = [
        HumanMessage(
            content=f"""
            
            You are an expert at answering questions using retrieved context chunks from a RAG system.
            Your role is to synthesize information from the chunks to provide accurate, well-supported answers.
        
            output_instructions=
                provide a clear, direct answer based on the context
                If context is insufficient, state this in your reasoning
                Never make up information not present in the chunks
                Focus on being accurate and concise
                do not say anythin else than your answer

            here is the question: {question}

            here are the chunks {docs}
            """,
        )
    ]

    # Invoking the model
    response = model.invoke(msg)

    final_summary = response.content

    logger.info("Summary:", response.content)

    state_update = {
            "final_summary": final_summary,
    }

    # Command for updating the state
    return Command(update=state_update)

                            ##CONVENTIONAL EDGES##

# Desitionary edge for if the chat pretains to a book or not
def route_RAG(state: State):

    # Class for forcing the output to be specific so that routing can be more consistant
    class evaluate(BaseModel):

        #Binary choice to use the rag model or not
        eval_score: str = Field(description="Use RAG or not, 'RAG' or 'END'")

    llm_with_tool = model.with_structured_output(evaluate)
    

    prompt = PromptTemplate(
        template="""you are a grader assesing a question to see if useful information could be derived from
        A list of books. if the question asked has any details or information from a book example the book 1984 
        by george orwell you would say 'RAG' DONT SAY ANYTHING ELSE and if the question has nothing to
        do with books you would say 'END' DONT SAY ANYTHING ESLE.
        
        ---steps---
        1. evaluate the users question in detail
        2. determin if the users question has anything to do with a book
        3. if the users output has to do with a book return 'RAG' AND NOTHING ELSE or if the users question
        does not pretain to a book return 'END' AND NOTHING ELSE
        
        ---output instructions---
        1.once a desition is made on a questions relivence for a book return either 'RAG if relivent or 'END' if not relivent
        
        here is the users question: {question}""",
        input_variables=["question"],
        )
    
    # Chain
    chain = prompt | llm_with_tool

    # Fetch
    messages = state["messages"]
    question = messages[0].content
    
    # Invoke
    route_result = chain.invoke({"question": question})

    # Output Schema 
    route = route_result.eval_score

    # based on the LLM's output what node to go to (query_rewrite or END)
    if route == 'RAG':
        logger.info("ROUTE: query_rewrite\n")
        return "query_rewrite"
    elif route == 'END':
        logger.info("ROUTE: END\n")
        return END
    else:
        logger.error("LLM response does not match edge conditions")
        return END


# Seeing if the question about a book asked is in the collection of books
def route_collection(state: State):
    
    # Fetch
    collection = state.get("collection_name")

    # Not in collection
    if collection == 'END':
        logger.info("Book not in collection")
        logger.info("ROUTE: END\n")
        return END
    
    # In Collection
    else:
        logger.info("Collection name:", collection)
        logger.info("ROUTE: similarity_search\n")
        return "similarity_search"


                        ##Building the state and graph

# Defines the graph builder so that all of the edges and nodes can be mapped out and handle information correctly
graph_builder = StateGraph(State)

    ## ADDING NODES
graph_builder.add_node("query_rewrite", query_rewrite)

graph_builder.add_node("similarity_search", similarity_search)

graph_builder.add_node("collection", collection)

graph_builder.add_node("generate", generate)

graph_builder.add_node("send_summary", send_summary)

    ## EDGES AND CONDITIONAL EDGES

# Start and figure out if the question is about a book
graph_builder.add_conditional_edges(START, route_RAG,{"query_rewrite": "query_rewrite", "__end__": "__end__"})

# Chat is talking about a book and the question is being rewriten
graph_builder.add_edge("query_rewrite", "collection")

# Finds the collection desides if the book the question is about is in the collection 
graph_builder.add_conditional_edges("collection", route_collection, {"similarity_search": "similarity_search", "__end__": "__end__"})

# Preforms cosin similarity search and moves to generate
graph_builder.add_edge("similarity_search", "generate")

# Generate to end
graph_builder.add_edge("generate", "send_summary")

graph_builder.add_edge("send_summary", END)


                        ##COMPILE THE GRAPH
logger.info("Building the graph")
graph = graph_builder.compile()

# Image for structure of the graph of nodes and edges
#display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# Activates the graph and updates the stream
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        #stream_mode = "debug"
        x = 1
        #for value in event.values():
            #print("Assistant:", value["messages"][-1].content)
            #message += value["messages"][-1].content

#Function used to receive messages.
def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            message_list.insert(tk.END, message)
        except Exception:
            logger.error("An error occured while receiving the message.")

#Function used to send messages.
def send():
    message = my_message.get()
    my_message.set("")
    
    print(f"sending {message} to graph:")

    client.send(bytes(message, "utf8"))

    stream_graph_updates(message)


# Creates the tkinter application.
window = tk.Tk()

# Names the application.
window.title("Chat room")

# Color scheme.
window.configure(bg="white")

# This creates the box where the messages will exist and update.
message_frame = tk.Frame(window, height=100, width=100, bg="white")
message_frame.pack()

# Creates a string variable for the user's message.
my_message = tk.StringVar()
my_message.set("")

# Adds a scroll bar to view older messages in chat room. 
scroll_bar = tk.Scrollbar(message_frame)

# Merges the frame and scroll bar together. 
message_list = tk.Listbox(message_frame, height=15, width=100, bg="white", yscrollcommand=scroll_bar.set)

# Puts the scroll bar on the right side of the frame.
scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
message_list.pack(side=tk.LEFT, fill=tk.BOTH)
message_list.pack()

# Adds a box where the user can type messages that will be sent. 
entry_field = tk.Entry(window, textvariable=my_message, fg="black", width=50)
entry_field.pack()

# Creates a button that will be used to send messages into the chat room. 
send_button = tk.Button(window, text="Send", font="Aerial", fg="white", bg="black", command=send)
send_button.pack()



# Run the GUI event loop
#window.mainloop()

# IP address and port used to connect clients to the server. 
host = "localhost"
port = 2000

# Create a socket object.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server. 
client.connect((host, port))
logger.info("connected to server")

# Thread used to allow multiple client requests to the server at the same time. 
receive_thread = Thread(target=receive)
receive_thread.start()

#This function is used to keep the tkinter function running until the application window is closed.
tk.mainloop()