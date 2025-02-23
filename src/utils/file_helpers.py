import os
from pathlib import Path
from typing import Set, Tuple, Dict
from src.services.document_processor import DocumentProcessor
from src.storage.storage import Storage

ALLOWED_EXTENSIONS = {'pdf', 'txt'}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_initial_documents(storage: Storage, doc_processor: DocumentProcessor, base_dir: Path) -> Tuple[str, Dict]:
    """Process all documents in the uploads folder at startup."""
    uploads_dir = base_dir / 'uploads'
    uploads_dir.mkdir(exist_ok=True)

    # Create a special session for initial documents
    initial_session = storage.create_session()
    all_chunks = []
    all_embeddings = []

    # Process all supported files
    for ext in ALLOWED_EXTENSIONS:
        for file in uploads_dir.glob(f'*.{ext}'):
            try:
                if file.suffix == '.pdf':
                    result = doc_processor.process_pdf(str(file))
                else:
                    result = doc_processor.process_text(str(file))

                all_chunks.extend(result['chunks'])
                all_embeddings.extend(result['embeddings'])
            except Exception as e:
                continue

    # Store combined results
    data = {
        'chunks': all_chunks,
        'embeddings': all_embeddings,
        'source': 'initial_documents'
    }
    storage.store_data(initial_session, data)

    return initial_session, data
