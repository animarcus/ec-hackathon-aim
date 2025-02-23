import logging
import pdfplumber
import re
from llm_client import CVAnalyzer
from config import DEFAULT_MODEL, DEFAULT_EMBEDDER

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, embedding_model: str = DEFAULT_EMBEDDER, llm_model: str = DEFAULT_MODEL):
        """Initialize DocumentProcessor with configurable models."""
        self.analyzer = CVAnalyzer(
            embedding_model=embedding_model,
            llm_model=llm_model
        )

    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess extracted text."""
        # Replace the section delimiter
        text = text.replace('ㅡ', '\n---\n')

        # Fix merged words by adding space before capital letters
        text = re.sub(r'(?<!^)(?<![\W\d])([A-Z])', r' \1', text)

        # Normalize spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Clean up extra spaces
        text = '\n'.join(line.strip() for line in text.split('\n'))

        return text.strip()

    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF using pdfplumber."""
        try:
            print(f"\n=== Processing PDF: {file_path} ===")
            with pdfplumber.open(file_path) as pdf:
                print(f"Number of pages: {len(pdf.pages)}")
                all_text = []
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    processed_text = self.preprocess_text(text)
                    print(f"\n--- Page {i+1} Content ---")
                    print(processed_text)
                    print("-" * 50)
                    all_text.append(processed_text)

                full_text = "\n\n".join(all_text)
                print("\n=== Full Extracted Text ===")
                print(full_text)
                print("=" * 50)
                return full_text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def create_chunks(self, text: str, min_length: int = 100, max_length: int = 1000) -> list:
        """Split text into meaningful chunks by sections."""
        print("\n=== Creating Chunks ===")

        # Split by section markers
        sections = text.split('---')
        chunks = []

        current_chunk = ""

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # If section is too large, split it further
            if len(section) > max_length:
                # Split by double newlines first
                subsections = section.split('\n\n')
                for subsection in subsections:
                    if len(subsection) > min_length:
                        chunks.append(subsection.strip())
                    elif current_chunk:
                        if len(current_chunk) + len(subsection) < max_length:
                            current_chunk = f"{current_chunk}\n\n{subsection}".strip()
                        else:
                            chunks.append(current_chunk)
                            current_chunk = subsection
                    else:
                        current_chunk = subsection
            else:
                chunks.append(section)

        if current_chunk:
            chunks.append(current_chunk)

        print(f"Created {len(chunks)} chunks")
        print("\n--- Chunks Created ---")
        for i, chunk in enumerate(chunks, 1):
            print(f"\nChunk {i} (length: {len(chunk)}):")
            print(chunk)
            print("-" * 30)

        return chunks

    def process_text(self, file_path: str):
        """Process text file and return chunks with embeddings."""
        try:
            # Read text file
            with open(file_path, 'r') as f:
                full_text = f.read()

            # Create chunks
            chunks = self.create_chunks(full_text)

            # Generate embeddings
            embeddings = [self.analyzer.get_embedding(chunk) for chunk in chunks]

            return {
                'chunks': chunks,
                'embeddings': embeddings,
                'full_text': full_text
            }
        except Exception as e:
            logger.error(f"Error processing text file: {str(e)}")
            raise

    def process_pdf(self, file_path: str):
        """Process PDF file and return chunks with embeddings."""
        try:
            print("\n========== Starting PDF Processing ==========")

            # Extract and preprocess text
            full_text = self.extract_text(file_path)
            print(f"\nExtracted text length: {len(full_text)} characters")

            # Create chunks
            chunks = self.create_chunks(full_text)

            # Generate embeddings
            print("\n=== Generating Embeddings ===")
            embeddings = []
            for i, chunk in enumerate(chunks, 1):
                print(f"Generating embedding for chunk {i}/{len(chunks)}")
                embedding = self.analyzer.get_embedding(chunk)
                print(f"Embedding dimension: {len(embedding)}")
                embeddings.append(embedding)

            print("\n=== Processing Complete ===")
            print(f"Total chunks: {len(chunks)}")
            print(f"Total embeddings: {len(embeddings)}")
            print("=" * 50)

            return {
                'chunks': chunks,
                'embeddings': embeddings,
                'full_text': full_text
            }

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            print(f"\nERROR: {str(e)}")
            raise
