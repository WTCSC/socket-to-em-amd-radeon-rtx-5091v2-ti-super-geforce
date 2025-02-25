from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
#from langchain_google_vertexai import ChatVertexAI
from langchain_openai import ChatOpenAI
import getpass
import os
from IPython.display import Image, display
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
#from pypdf import PdfReader
import chromadb
#from langchain_core.documents import Document
from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from dotenv import load_dotenv
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
print("attempting to connect to server")
client.connect(('localhost', 5000))
print("Connected to server")

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

    #print("sending AI response to server")

    final_summary = state.get("final_summary")
    client.send(final_summary.encode())
    response = client.recv(1024).decode()

    print(f"Server says: {response}")

    return {"final_summary": [final_summary]}

# Node for enhancing question for similarity search
def query_rewrite(state: State):
    
    #print("\n---REWRITING QUERY---\n")
    
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
    #print("Rewriten query: " + response.content)
    
    # Adding the response question to message flow in state
    return {"messages": [response]}


    

# Node responsible for finding the correct collection to query
def collection(state: State):
    
    #print("\n---FINDING CORRECT COLLECTION---\n")

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

    # Adds the collection name to state so it can be called through conventional edges
    state_update = {
            "collection_name": collection,
    }

    # Command for updating the state
    return Command(update=state_update)



    
# preforms the cosin similarity
def similarity_search(state: State):

    # fetch REWRIT question (better for similarity search)
    messages = state["messages"]
    question = messages[1].content

    #print("\n---PREFORMING SIMILARITY SEARCH---\n")

    # Pulls the collection name var from the state
    collection_name = state.get("collection_name")

    #print(f"\nSearching collection: {collection_name}\n")
    
    # Defines how many dimentions the embeddings should be formatted into
    dimensions = 384

    # Defines the embedding model used for future embeddings
    model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1", truncate_dim=dimensions,)

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

    # Command for the state update
    return Command(update=state_update)



# Generate node for final summary
def generate(state: State):

    #print("\n---GENERATING INFORMATION---\n")
    
    # fetch original question and docs
    messages = state["messages"]
    question = messages[0].content
    docs = state.get("docs")

    #print(f"question for gen: {question} docs to pull from: {docs}")

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

    #print("\n---SUMMARY---\n")

    #print("summary:", response.content)

    final_summary = response.content

    state_update = {
            "final_summary": final_summary,
    }

    # Command for updating the state
    return Command(update=state_update)


    # Adds summary into the messages cadigory in the state
    #return {"messages": [response]}

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
        #print("\nROUTE: query_rewrite\n")
        return "query_rewrite"
    elif route == 'END':
        #print("\nROUTE: END\n")
        return END
    else:
        #print("Error route not valid")
        return END


# Seeing if the question about a book asked is in the collection of books
def route_collection(state: State):
    
    # Fetch
    collection = state.get("collection_name")

    # Not in collection
    if collection == 'END':
        #print("\nbook not in collection\n")
        #print("\n ROUTE: END\n")
        return END
    
    # In Collection
    else:
        #print("Collection name:", collection)
        #print("\n ROUTE: similarity_search\n")
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
graph = graph_builder.compile()

# Image for structure of the graph of nodes and edges
#display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# Activates the graph and updates the stream
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        stream_mode = "debug"
        #for value in event.values():
            #print("Assistant:", value["messages"][-1].content)
            #message += value["messages"][-1].content


# User interaction loop
def main():
    while True:
        print("\nEnter a query (or type 'q' to quit)\n")
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            return
        if not user_input:
            break
        client.send(user_input.encode())
        response = client.recv(1024).decode()
        print(f"\nServer says: {response}\n")

        stream_graph_updates(user_input)


if __name__ == "__main__":
    main()
        
#user_input = "where does gatsby describe his cars and their colors"
#user_input = "test"
#user_input = "why is george orwells 1984 seen as weird"

#stream_graph_updates(user_input)
