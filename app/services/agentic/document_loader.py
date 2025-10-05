from typing import List, Union
from pydantic import ValidationError
from langchain_community.document_loaders import WebBaseLoader, TextLoader, PyPDFLoader
from langchain_community.document_loaders.parsers import TesseractBlobParser
from langchain_core.documents import Document
import bs4
from io import BytesIO
from app.schemas.agentic import DocumentLoaderConfig, WebConfig, FileConfig, TextConfig
from typing import Literal

class DocumentLoaderFactory:
    @staticmethod
    async def create_loader(config: DocumentLoaderConfig):
        """
        Create a document loader based on the provided configuration.
        """
        if config.type == "web":
            if not config.webConfig:
                raise ValueError("Web config required for web loader")
            return WebBaseLoader(
                web_path=config.webConfig.url
            )

        elif config.type == "file":
            if not config.fileConfig:
                raise ValueError("File config required for file loader")
            
            # verify file path exists
            file_path = config.fileConfig.path
            try:
                with open(file_path, 'rb') as f:
                    file_like = BytesIO(f.read())
            except FileNotFoundError:
                raise ValueError(f"File not found: {file_path}")
            
            if config.fileConfig.type == "pdf":
                return PyPDFLoader(config.fileConfig.path,
                                   mode="page",
                                    images_inner_format="html-img",
                                    images_parser=TesseractBlobParser()
                                   )
            elif config.fileConfig.type == "txt":
                return TextLoader(config.fileConfig.path)
            else:
                raise ValueError(f"Unsupported file type: {config.fileConfig.type}")

        elif config.type == "text":
            if not config.textConfig:
                raise ValueError("Text config required for text loader")
            
            class TextContentLoader:
                async def load(self) -> List[Document]:
                    return [
                        Document(
                            page_content=config.textConfig.content,
                            metadata={"source": "text-input"}
                        )
                    ]
            
            return TextContentLoader()

        else:
            raise ValueError(f"Unsupported loader type: {config.type}")

    @staticmethod
    async def load_documents(config: DocumentLoaderConfig) -> List[Document]:
        """
        Load documents using the appropriate loader based on configuration.
        """
        loader = await DocumentLoaderFactory.create_loader(config)
        return  loader.load()