from langchain_mistralai import ChatMistralAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.hub import pull
from langgraph.graph import StateGraph, START
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chat_models import init_chat_model
from app.services.agentic.document_loader import DocumentLoaderFactory
from app.services.agentic.vector_store import VectorStoreFactory
from app.services.agentic.embeddings_factory import EmbeddingsFactory
from app.schemas.agentic import RAGConfig, RAGResponse, DocumentLoaderConfig
from typing import List, TypedDict
import time
import asyncio

class RAGPipeline:
    def __init__(self, config: RAGConfig):
        """
        Initialize the RAG pipeline with the given configuration.
        """
        self.config = config
        # Corrected to use llm config fields
        self.llm = init_chat_model(
            model=self.config.llm.model,
            model_provider="mistralai"
        )
        self.embeddings = None
        self.vector_store = None
        self.prompt_template = None
        self.graph = None

    async def initialize(self) -> None:
        """
        Initialize the vector store, load documents, and build the graph.
        """
        # Initialize embeddings
        self.embeddings = await EmbeddingsFactory.create_embeddings(self.config.embeddings)

        # Initialize vector store
        self.vector_store = await VectorStoreFactory.create_vector_store(
            self.config.vectorStore, self.embeddings
        )

        # Load and process documents
        await self.load_and_index_documents()

        # Load prompt template asynchronously
        self.prompt_template =  pull("rlm/rag-prompt")

        # Build the graph
        self._build_graph()

    async def load_and_index_documents(self) -> None:
        """
        Load and index documents into the vector store.
        """
        docs = await DocumentLoaderFactory.load_documents(self.config.documentLoader)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunking.chunkSize,
            chunk_overlap=self.config.chunking.chunkOverlap
        )
        all_splits = splitter.split_documents(docs)  # Synchronous call
        await self.add_split_documents(all_splits)
        print(f"✅ Indexed {len(all_splits)} document chunks")

    def _build_graph(self) -> None:
        """
        Build the LangGraph for the RAG pipeline.
        """
        class State(TypedDict):
            question: str
            context: List[Document]
            answer: str

        # Define application steps
        async def retrieve(state: State) -> dict:
            retrieved_docs =  self.vector_store.similarity_search(state["question"], k=4)
            return {"context": retrieved_docs}

        async def generate(state: State) -> dict:
            docs_content = "\n\n".join(doc.page_content for doc in state["context"])
            messages =  self.prompt_template.invoke({
                "question": state["question"],
                "context": docs_content
            })
            response = await self.llm.ainvoke(messages)
            return {"answer": response.content}

        # Compile the graph
        graph_builder = StateGraph(State).add_sequence([retrieve, generate])
        graph_builder.add_edge(START, "retrieve")
        self.graph = graph_builder.compile()
        print("✅ RAG pipeline graph built successfully")

    async def query(self, question: str) -> RAGResponse:
        """
        Execute a query through the RAG pipeline and return the response.
        """
        start_time = time.time()
        try:
            # Use ainvoke for async graph execution
            result = await self.graph.ainvoke({"question": question})
            processing_time = time.time() - start_time
            return RAGResponse(
                answer=result["answer"],
                context=[doc.page_content for doc in result["context"]],
                metadata={
                    "retrievedDocs": len(result["context"]),
                    "processingTime": processing_time
                }
            )
        except Exception as e:
            raise RuntimeError(f"RAG query failed: {str(e)}")

    async def add_split_documents(self, docs: List[Document]) -> None:
        """
        Add split documents to the vector store.
        """
        # Run synchronous add_documents in a thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: self.vector_store.add_documents(docs))
        print(f"✅ Added {len(docs)} new document chunks")

    async def add_new_documents(self, config: DocumentLoaderConfig) -> None:
        """
        Load and index new documents into the vector store.
        """
        docs = await DocumentLoaderFactory.load_documents(config)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunking.chunkSize,
            chunk_overlap=self.config.chunking.chunkOverlap
        )
        all_splits = splitter.split_documents(docs)  # Synchronous call
        await self.add_split_documents(all_splits)
        print(f"✅ Added {len(all_splits)} new document chunks")