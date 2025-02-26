[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/nSbtKKg7)
[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=18275181)
Here's a README file for your project:  

---

## **Graph-Based Retrieval Augmented Generation (RAG) System**  

### **Overview**  
This project implements a **Graph-Based Retrieval Augmented Generation (RAG) System** using **LangGraph, LangChain, and ChromaDB** to perform **semantic search and answer generation** for book-related queries. The system enhances user questions, retrieves relevant book content using **cosine similarity search**, and generates responses using **GPT-4o-mini**.  

### **Features**  
- **Graph-Based Workflow:** Implements a structured flow of information using **LangGraph**.  
- **Query Enhancement:** Rewrites user queries for better similarity search results.  
- **Collection Routing:** Determines if the query pertains to an indexed book.  
- **Vector Search:** Uses **SentenceTransformer embeddings** to find relevant document chunks.  
- **Response Generation:** Provides contextual answers using **GPT-4o-mini**.  

---

## **Installation**  

### **Prerequisites**  
Ensure you have Python **3.8+** installed.  

### **Dependencies**  
Install the required libraries using:  

```bash
pip install langchain langgraph chromadb pydantic sentence-transformers langchain-openai python-dotenv
```

---

## **Setup**  

### **Environment Variables**  
Create a `.env` file and add your API key:  

```bash
OPENAI_API_KEY=your_api_key_here
```

Alternatively, enter the key when prompted.  

---

## **Usage**  

### **Running the System**  
Execute the script to start the interactive session:  

```bash
1. python Server.py
2. python Client.py
3. Open Powershell or Command Line
4. ipconfig /all
5. Connect to server with IPV4 Address
```

### **User Input Format**  
- Enter queries related to indexed books.  
- Type **"quit"**, **"exit"**, or **"q"** to stop the program.  

---

## **System Workflow**  

1. **Determine Query Type:**  
   - Checks if the query relates to a book.  
   - If not, exits.  

2. **Query Enhancement:**  
   - Reformulates the query for better retrieval.  

3. **Collection Routing:**  
   - Identifies the relevant book collection.  
   - If the book is **not indexed**, exits.  

4. **Vector Similarity Search:**  
   - Performs **cosine similarity search** on stored embeddings.  

5. **Answer Generation:**  
   - Synthesizes an answer using retrieved documents and **GPT-4o-mini**.  

6. **Response Display:**  
   - Outputs the generated answer.  

---

## **Customization**  

### **Adding More Books**  
To expand the collection, modify the **ChromaDB storage** and indexing process to include additional books.  

### **Modifying the Prompt**  
Update the `PromptTemplate` in the **generate** function to adjust the response format.  

---

## **Future Enhancements**  
- Expand the book database with more collections.  
- Integrate more sophisticated reranking models.  
- Improve user interaction with **chat-based UI**.  

---

## **Author**  
Developed by Jacob Casey and Cristian Holmes
