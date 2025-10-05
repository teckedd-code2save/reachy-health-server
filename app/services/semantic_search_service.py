from typing import List, Dict, Any
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import os
from elasticsearch import AsyncElasticsearch
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SemanticSearchService:
    def __init__(self):
        self.model = HuggingFaceEmbeddings(
            model_name=settings.SEMANTIC_SEARCH_MODEL)
        
        self.es = AsyncElasticsearch([settings.ELASTICSEARCH_URL])
        self.index = settings.ELASTICSEARCH_INDEX

    async def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a given text using HuggingFaceHubEmbeddings
        """
        # HuggingFaceHubEmbeddings expects a list of texts
        return self.model.embed_documents([text])[0]

    async def index_file(self, file_data: Dict[str, Any]) -> bool:
        """
        Index a file with its embedding
        """
        try:
            # Generate embedding for the file content
            content = file_data.get("content", "")
            ocr_text = file_data.get("ocr_text", "")
            text_to_embed = f"{file_data.get('filename', '')} {content} {ocr_text}"
            embedding = await self.get_embedding(text_to_embed)

            # Add embedding to the file data
            file_data["embedding"] = embedding

            # Index the file
            await self.es.index(
                index=self.index,
                document=file_data,
                id=file_data.get("id")
            )
            return True
        except Exception as e:
            logger.error(f"Error indexing file with embedding: {str(e)}")
            return False

    async def semantic_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Perform semantic search
        """
        try:
            # Get embedding for the query
            query_embedding = await self.get_embedding(query)

            # Build search query
            search_query = {
                "knn": {
                    "field": "embedding",
                    "query_vector": query_embedding,
                    "k": top_k,
                    "num_candidates": 100
                }
            }

            # Execute search
            response = await self.es.search(
                index=self.index,
                body={"knn": search_query}
            )

            # Process results
            return [hit["_source"] for hit in response["hits"]["hits"]]

        except Exception as e:
            logger.error(f"Error performing semantic search: {str(e)}")
            return []