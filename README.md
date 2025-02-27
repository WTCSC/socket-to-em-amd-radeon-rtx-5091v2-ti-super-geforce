[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/nSbtKKg7)
[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=18275181)
Here's a README file for your project:  

---

# Graph-Based Retrieval Augmented Generation (RAG) System

## Overview
The **Graph-Based Retrieval Augmented Generation (RAG) System** is designed to perform semantic search and answer generation for book-related queries. Using a combination of **LangGraph, LangChain, and ChromaDB**, the system **enhances** user questions, **retrieves** the most relevant book content using cosine similarity search on **SentenceTransformer embeddings**, and **generates** contextual responses using **GPT-4o-mini**. This approach **leverages** graph-based workflows to create a **structured**, **efficient**, and **scalable retrieval mechanism**.
---

## Features

### Graph-Based Workflow:
Utilizes **LangGraph** to **implement** a **structured flow of information**, ensuring that **data retrieval** and **response generation** occur in a logical and traceable manner.

### Query Enhancement:
**Automatically rewrites** user queries to **improve the quality** of similarity searches, making it easier to find the **best matching content**.

### Collection Routing:
**Determines** whether a **given query** pertains to an **indexed book collection** and **routes the query accordingly**.

### Vector Similarity Search:
Uses **SentenceTransformer embeddings** to perform a **cosine similarity search** on **stored document chunks**, enabling **precise retrieval of relevant content**.

### Response Generation:
**Synthesizes answers** using **GPT-4o-mini** by **combining retrieved document chunks** with **enhanced query context**.
---

## Installation

### Prerequisites
1. **Python 3.8 or higher**

2. A **reliable** internet connection for API access

### Dependencies
**Install** the **required libraries** by running the following command:
```
pip install langchain langgraph chromadb pydantic sentence-transformers langchain-openai python-dotenv
```

### Environment Variables
```
Create a .env file in the root directory of the project and add your API key:
```

OPENAI_API_KEY = your_api_key_here
Alternatively, you can enter the API key when prompted during runtime.
---

### Usage

To start the interactive session, follow these steps:

Start the server component:
```
python Server.py
```

In another terminal, start the client component:
```
python Client.py
```

1. Open **PowerShell or your preferred **command line interface**.

2. Run **ipconfig /all** (or the equivalent command on your OS) to obtain the **IPV4 address** of the computer running the server.

3. Connect to the **server** using the **retrieved IPV4 address**.
---

## User Input Format

Enter **queries** that **relate** to the **indexed books**.

To **exit** the program, type any of the following: **"quit", "exit", or "q"**.
---

## System Workflow

### Determine Query Type:
The **system** first checks if the **query** is **related** to an **indexed book**. **If** the **query** does not **pertain** to a book, the **process exits** gracefully.

### Query Enhancement:
The **original user query** is reformulated to **improve retrieval performance** by the **similarity search engine**.

### Collection Routing:
The system **identifies** the **relevant book collection** based on the **enhanced query**. If the queried book is not indexed, the process terminates.

### Vector Similarity Search:
Using **cosine similarity search**, the system finds the **most relevant** document chunks from **stored embeddings**.

### Answer Generation:
**Retrieved documents** and the **enhanced query** are fed into **GPT-4o-mini** to generate a **coherent** and **contextually** accurate answer.

### Response Display:
The final answer is then **displayed** to the user.

---

## Customization

### Adding More Books
To expand the collection, update the **ChromaDB** storage and **indexing process** to include additional books. Modify the data ingestion scripts as needed to handle new collections.

### Modifying the Prompt
Adjust the **PromptTemplate** within the generate function to tailor the answer format. This allows you to fine-tune the style and content of the generated responses.

---

## Future Enhancements

### Database Expansion:
Incorporate more book collections to improve the breadth of content retrieval.

### Advanced Reranking:
Integrate more sophisticated reranking models to further refine search results.

### Enhanced UI:
Develop a chat-based user interface to improve overall user interaction and accessibility.

---

## Troubleshooting

### API Issues:
Ensure your OPENAI_API_KEY is valid and that you have a stable internet connection.

### Installation Problems:
Verify that all dependencies are installed correctly. Running pip install -r requirements.txt (if a requirements file is provided) may help.

### Runtime Errors:
Check for error messages in the terminal. Common issues may involve network connectivity or missing environment variables.

### Data Indexing:
If queries yield no results, ensure that the book collection has been properly indexed in ChromaDB.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Author's
Developed by Jacob Casey, Cristian Holmes, and Marcus Quach.
