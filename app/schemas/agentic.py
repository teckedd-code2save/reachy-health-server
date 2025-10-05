from typing import Literal, Optional, Union, List
from pydantic import BaseModel

class PineconeConfig(BaseModel):
    indexName: str
    maxConcurrency: Optional[int] = None

class VectorStoreConfig(BaseModel):
    type: Union[Literal['memory'], Literal['pinecone']]
    pineconeConfig: Optional[PineconeConfig] = None

class WebConfig(BaseModel):
    url: str
    selector: Optional[str] = None

class FileConfig(BaseModel):
    path: str
    type: Union[Literal['pdf'], Literal['txt'], Literal['json']]

class TextConfig(BaseModel):
    content: str

class DocumentLoaderConfig(BaseModel):
    type: Union[Literal['web'], Literal['file'], Literal['text'],Literal['image']]
    webConfig: Optional[WebConfig] = None
    fileConfig: Optional[FileConfig] = None
    textConfig: Optional[TextConfig] = None

class LLMConfig(BaseModel):
    model: str
    temperature: float

class EmbeddingsConfig(BaseModel):
    provider: Literal['mistralai', 'openai', 'huggingface']
    model: str

class ChunkingConfig(BaseModel):
    chunkSize: int
    chunkOverlap: int

class RAGConfig(BaseModel):
    llm: LLMConfig
    embeddings: EmbeddingsConfig
    chunking: ChunkingConfig
    vectorStore: VectorStoreConfig
    documentLoader: DocumentLoaderConfig

class Metadata(BaseModel):
    retrievedDocs: int
    processingTime: float

class RAGResponse(BaseModel):
    answer: str
    context: List[str]
    metadata: Metadata