# %% import all the packages
import os, json

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = config["LangChainAPIKey"]
os.environ['OPENAI_API_KEY'] = config["OpenAIAPIKey"]

import bs4
from langchain_classic import hub  # 2025/12/27 updated
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, DirectoryLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# Index: documents preprocessing, loading, spliting and vectorizing
# use deeplearning course pdfs as an example
# %%
loader = DirectoryLoader(
    "CourseMaterials/deep_learning",
    glob="*.pdf",
    loader_cls=PyPDFLoader
)

docs = loader.load()

# Split Documents
from langchain_text_splitters import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size = 300,
    chunk_overlap = 50
)

doc_splits = text_splitter.split_documents(docs)
len(doc_splits)

# Index(Vectorize)
vectorstore = Chroma.from_documents(
    documents=doc_splits,
    embedding=OpenAIEmbeddings()
)

retriever = vectorstore.as_retriever(search_kwargs={'k':3})
retriever

# %%
# Retrieval
question = "Can you list some of the hyperparameters in the FFN?"
relevant_docs = retriever.invoke(question)
print(relevant_docs)

# %%
# Prompt Generation
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

prompt_template = """You are a helpful assistant.
Answer the question using ONLY the Context below.
If the answer is not in the Context, say "I don't know based on the provided context."
Context:
{context}

Question:
{question}
"""

prompt = ChatPromptTemplate.from_template(prompt_template)

# Select LLM for answer generation
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

# Config Chain
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

def format_docs(docs):
    parts = []
    for i, d in enumerate(docs, 1):
        src = d.metadata.get("source", "unknown_source")
        page = d.metadata.get("page_label", d.metadata.get("page", "unknown_page"))
        text = (d.page_content or "").strip()
        parts.append(f"[{i}] ({src}, p.{page})\n{text}")
    return "\n\n".join(parts)

rag_chain = (
    {
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
)

resp = rag_chain.invoke(question)
print(resp)

