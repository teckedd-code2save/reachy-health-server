import asyncio
from langchain_core.vectorstores import InMemoryVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_core.embeddings import Embeddings
from app.schemas.agentic import VectorStoreConfig
from typing import Union

class VectorStoreFactory:
    @staticmethod
    async def create_vector_store(config: VectorStoreConfig, embeddings: Embeddings):
        """
        Create a vector store based on the provided configuration and embeddings.
        """
        if config.type == "memory":
            return InMemoryVectorStore(embeddings)

        elif config.type == "pinecone":
            if not config.pineconeConfig:
                raise ValueError("Pinecone config required for Pinecone store")
            
            pinecone = Pinecone(api_key=...)  # Assumes API key is set via environment variable PINECONE_API_KEY
            existing_indexes = [index_info["name"] for index_info in pinecone.list_indexes()]
            if config.pineconeConfig.indexName not in existing_indexes:
                pinecone.create_index(
                    config.pineconeConfig.indexName,
                    dimension=embeddings.dimension,
                    # serverless_spec=ServerlessSpec(
                    #     auto_scaling_enabled=True,
                    #     min_replica_count=1,
                    #     max_replica_count=5
                    # )
                )
                while not pinecone.describe_index(config.pineconeConfig.indexName).status["ready"]:
                    await asyncio.sleep(1)

            pinecone_index = pinecone.Index(config.pineconeConfig.indexName)
            
            return PineconeVectorStore(
                embedding=embeddings,
                index=pinecone_index,
                max_concurrency=config.pineconeConfig.maxConcurrency or 5
            )

        else:
            raise ValueError(f"Unsupported vector store type: {config.type}")