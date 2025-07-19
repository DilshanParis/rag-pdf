import os
import PyPDF2
import faiss
import openai
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def read_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def create_vector_store(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    docs = [Document(page_content=chunk) for chunk in chunks]

    embeddings = OpenAIEmbeddings()
    vectordb = FAISS.from_documents(docs, embeddings)
    return vectordb

def run_rag():
    pdf_path = input("Enter the full path to your PDF file: ").strip()

    if not os.path.exists(pdf_path):
        print("❌ File not found. Please check the path and try again.")
        return

    print("[*] Reading and processing PDF...")
    text = read_pdf(pdf_path)
    vectordb = create_vector_store(text)

    print("[*] Ready for questions! Type 'exit' to quit.")
    qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0), retriever=vectordb.as_retriever())

    while True:
        question = input("You: ")
        if question.lower() in ["exit", "quit"]:
            break
        answer = qa.invoke(question)
        print("AI:", answer)

if __name__ == "__main__":
    run_rag()
