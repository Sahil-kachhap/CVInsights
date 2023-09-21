from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import Replicate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import pinecone
import os
from dotenv import load_dotenv
load_dotenv('.env')

def load_documents(folder_name):
    loader = PyPDFDirectoryLoader(folder_name)
    docs = loader.load()
    return docs

def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 20)
    docs = text_splitter.split_documents(documents=documents)
    return docs

def embed_chunks(folder_path):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"),  # find at app.pinecone.io
        environment=os.getenv("PINECONE_ENV"), 
    )

    index_name = "resume-insights-index"

    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            name=index_name,
            metric='cosine',
            dimension=384
        )
    
    documents = load_documents(folder_path)
    chunks = split_documents(documents)
    db = Pinecone.from_documents(chunks, embedding=embeddings, index_name=index_name)
    return embeddings

def retrieve_response_from_llm(query, embeddings):
    llm = Replicate(
    streaming = True,
    model = "replicate/llama-2-70b-chat:58d078176e02c219e11eb4da5a02a7830a283b14cf8f94537af893ccff5ee781", 
    callbacks=[StreamingStdOutCallbackHandler()],
    input = {"temperature": 0.01, "max_length":500,"top_p":1})
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    vector_store = Pinecone.from_existing_index("resume-insights-index", embeddings)
    chain = ConversationalRetrievalChain.from_llm(llm=llm, chain_type='stuff',
                                                 retriever=vector_store.as_retriever(),
                                                 memory=memory)
    result = chain({"question": query})
    return result["answer"]

def init_llm_response(prompt):
    embeddings = embed_chunks("resume_files/")
    #response = retrieve_response_from_llm(prompt, embeddings)
    return embeddings