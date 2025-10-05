from langchain_mistralai import MistralAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from app.schemas.agentic import EmbeddingsConfig
from typing import Union

class EmbeddingsFactory:
    @staticmethod
    async def create_embeddings(config: EmbeddingsConfig) -> Embeddings:
        """
        Create an embeddings instance based on the provided configuration.
        """
        if config.provider.startswith("mistral"):
            return MistralAIEmbeddings(model=config.model)
        elif config.provider.startswith("openai"):
           
            return OpenAIEmbeddings(model=config.model)
        elif config.provider.startswith("huggingface"):
            return HuggingFaceEmbeddings(model_name=config.model)
        else:
            raise ValueError(f"Unsupported embeddings model: {config.model}")