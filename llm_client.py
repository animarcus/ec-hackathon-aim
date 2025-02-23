import logging
import numpy as np
from typing import List, Dict, Any, Optional
from ollama import Client, ResponseError
from config import DEFAULT_MODEL, DEFAULT_EMBEDDER, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class CVAnalyzer:
    def __init__(self, embedding_model: str = DEFAULT_EMBEDDER, llm_model: str = DEFAULT_MODEL):
        """Initialize CV Analyzer with specified models."""
        self.ollama = Client(host='http://localhost:11434')
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self._embedding_dim = None

    def get_embedding(self, text: str) -> List[float]:
        """Get embeddings using Ollama."""
        response = self.ollama.embeddings(
            model=self.embedding_model,
            prompt=text
        )
        embedding = response['embedding']

        # Store dimension on first use
        if self._embedding_dim is None:
            self._embedding_dim = len(embedding)

        return embedding

    def validate_embeddings(self, embeddings: List[List[float]]) -> bool:
        """Validate embedding dimensions."""
        if not embeddings:
            return False

        # Get expected dimension from first embedding
        expected_dim = len(embeddings[0])

        # Check all embeddings have same dimension
        return all(len(emb) == expected_dim for emb in embeddings)

    def semantic_search(self, query: str, chunks: List[str], embeddings: List[List[float]], k: int = 3) -> List[str]:
        """Search through chunks using semantic similarity."""
        try:
            # Basic validation
            if not chunks or not embeddings:
                logger.warning("Empty chunks or embeddings provided")
                return []

            # Validate stored embeddings
            if not self.validate_embeddings(embeddings):
                logger.error(f"Invalid embeddings dimensions: got {len(embeddings)} embeddings")
                return chunks[:k]

            # Create query embedding
            query_embedding = self.get_embedding(query)

            # Verify dimension match
            if len(query_embedding) != len(embeddings[0]):
                logger.error(f"Embedding dimension mismatch: stored={len(embeddings[0])}, query={len(query_embedding)}")
                return chunks[:k]

            # Calculate similarities using numpy for efficiency
            query_embedding = np.array(query_embedding)
            chunk_embeddings = np.array(embeddings)

            # Calculate cosine similarity
            similarities = np.dot(chunk_embeddings, query_embedding) / (
                    np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(query_embedding)
            )

            # Get top k indices
            top_indices = np.argsort(similarities)[-k:][::-1]

            # Return corresponding chunks
            return [chunks[i] for i in top_indices]

        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return chunks[:k] if chunks else []

    def get_llm_response(self, user_message: str, cv_chunks: List[str], cv_embeddings: List[List[float]],
                         stream: bool = False, initial_context: Optional[Dict] = None):
        """Get response from Ollama LLM using semantically relevant context chunks."""
        try:
            # Get relevant context using semantic search
            doc_chunks = []
            if initial_context:
                doc_chunks = self.semantic_search(
                    user_message,
                    initial_context['chunks'],
                    initial_context['embeddings']
                )

            # Get background for adaptation (but not for content)
            background_chunks = self.semantic_search(user_message, cv_chunks, cv_embeddings)

            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"""[BACKGROUND INFORMATION ABOUT THE USER FOR ADAPTATION - DO NOT REFERENCE IN RESPONSE]
    ```
    {' '.join(background_chunks)}
    ```
    
    
    [DOCUMENTATION CONTENT]
    ```
    {' '.join(doc_chunks)}
    ```
    
    User question: {user_message}
    
    Please provide a response based only on the documentation content"""
                }
            ]

            # Get response from Ollama
            response = self.ollama.chat(
                model=self.llm_model,
                messages=messages,
                stream=stream
            )

            if stream:
                return response

            return response.message.content

        except Exception as e:
            logger.error(f"Error getting LLM response: {str(e)}")
            raise

    def stream_response(self, user_message: str, chunks: List[str], embeddings: List[List[float]]):
        """Stream response from Ollama."""
        try:
            stream = self.get_llm_response(user_message, chunks, embeddings, stream=True)
            for chunk in stream:
                yield chunk.message.content
        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}")
            raise


# Create default analyzer instance for backwards compatibility
default_analyzer = CVAnalyzer()


# Provide top-level functions that use default analyzer for backwards compatibility
def get_llm_response(user_message: str, chunks: List[str], embeddings: List[List[float]], stream: bool = False):
    """Backwards compatible get_llm_response using default analyzer."""
    return default_analyzer.get_llm_response(user_message, chunks, embeddings, stream)


def stream_response(user_message: str, chunks: List[str], embeddings: List[List[float]]):
    """Backwards compatible stream_response using default analyzer."""
    return default_analyzer.stream_response(user_message, chunks, embeddings)
