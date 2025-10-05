from typing import List, Dict, Any, Optional
from elasticsearch import AsyncElasticsearch
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.es = AsyncElasticsearch([settings.ELASTICSEARCH_URL])
        self.index = settings.ELASTICSEARCH_INDEX

    async def index_file(self, file_data: Dict[str, Any]) -> bool:
        """
        Index a file in Elasticsearch
        """
        try:
            await self.es.index(
                index=self.index,
                document=file_data,
                id=file_data.get('id')
            )
            return True
        except Exception as e:
            logger.error(f"Error indexing file: {str(e)}")
            return False

    async def search_files(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Search files with advanced filtering
        """
        try:
            # Build search query
            search_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": [
                                        "filename^3",
                                        "content",
                                        "metadata.*",
                                        "ocr_text"
                                    ],
                                    "fuzziness": "AUTO"
                                }
                            }
                        ]
                    }
                },
                "from": (page - 1) * size,
                "size": size,
                "sort": [
                    {"_score": {"order": "desc"}},
                    {"created_at": {"order": "desc"}}
                ]
            }

            # Add filters if provided
            if filters:
                filter_conditions = []
                for field, value in filters.items():
                    if isinstance(value, list):
                        filter_conditions.append({"terms": {field: value}})
                    else:
                        filter_conditions.append({"term": {field: value}})
                
                search_query["query"]["bool"]["filter"] = filter_conditions

            # Execute search
            response = await self.es.search(
                index=self.index,
                body=search_query
            )

            # Process results
            hits = response["hits"]["hits"]
            total = response["hits"]["total"]["value"]

            return {
                "results": [hit["_source"] for hit in hits],
                "total": total,
                "page": page,
                "size": size
            }

        except Exception as e:
            logger.error(f"Error searching files: {str(e)}")
            return {
                "results": [],
                "total": 0,
                "page": page,
                "size": size
            }

    async def delete_index(self, file_id: str) -> bool:
        """
        Delete a file from the index
        """
        try:
            await self.es.delete(
                index=self.index,
                id=file_id
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting file from index: {str(e)}")
            return False

    async def update_index(self, file_id: str, file_data: Dict[str, Any]) -> bool:
        """
        Update a file in the index
        """
        try:
            await self.es.update(
                index=self.index,
                id=file_id,
                body={"doc": file_data}
            )
            return True
        except Exception as e:
            logger.error(f"Error updating file in index: {str(e)}")
            return False 