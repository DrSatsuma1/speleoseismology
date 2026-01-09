#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) system for paleoseismic research.

This indexes your papers, notes, and documents so Claude can search them.

Setup:
    pip install chromadb sentence-transformers pymupdf

Usage:
    # Index a PDF
    python rag.py index /path/to/paper.pdf

    # Index all PDFs in a directory
    python rag.py index /path/to/papers/ --recursive

    # Index markdown files
    python rag.py index ../methodology/

    # Search for relevant content
    python rag.py search "Chiodini CO2 flux model earthquake"

    # Search with more results
    python rag.py search "Motagua fault paleoseismic" --top 10

    # List indexed documents
    python rag.py list

    # Clear the index
    python rag.py clear
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re

# Lazy imports to allow --help without dependencies
def get_chromadb():
    import chromadb
    return chromadb

def get_sentence_transformer():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer

def get_fitz():
    import fitz  # pymupdf
    return fitz


# =============================================================================
# CONFIGURATION
# =============================================================================

# Where to store the vector database
DB_PATH = Path(__file__).parent.parent / "data" / "rag_db"

# Embedding model (small, fast, good quality)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Chunk size for splitting documents
CHUNK_SIZE = 500  # characters
CHUNK_OVERLAP = 50


# =============================================================================
# TEXT EXTRACTION
# =============================================================================

def extract_pdf_text(pdf_path: Path) -> List[Tuple[str, int]]:
    """
    Extract text from PDF, returning list of (text, page_number) tuples.
    """
    fitz = get_fitz()
    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc, 1):
        text = page.get_text()
        if text.strip():
            pages.append((text, page_num))

    doc.close()
    return pages


def extract_markdown_text(md_path: Path) -> str:
    """Extract text from markdown file."""
    return md_path.read_text(encoding='utf-8')


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks.

    Uses sentence boundaries when possible.
    """
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    # Split by sentences (rough heuristic)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # If adding this sentence would exceed chunk size
        if len(current_chunk) + len(sentence) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                # Keep overlap from end of current chunk
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                # Sentence itself is too long, force split
                for i in range(0, len(sentence), chunk_size - overlap):
                    chunks.append(sentence[i:i + chunk_size].strip())
                current_chunk = ""
        else:
            current_chunk += " " + sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def compute_hash(text: str) -> str:
    """Compute hash of text for deduplication."""
    return hashlib.md5(text.encode()).hexdigest()[:12]


# =============================================================================
# RAG DATABASE
# =============================================================================

class RAGDatabase:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.mkdir(parents=True, exist_ok=True)

        chromadb = get_chromadb()
        self.client = chromadb.PersistentClient(path=str(db_path))
        self.collection = self.client.get_or_create_collection(
            name="paleoseismic_papers",
            metadata={"hnsw:space": "cosine"}
        )

        # Load embedding model
        SentenceTransformer = get_sentence_transformer()
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def index_document(self, file_path: Path, force: bool = False) -> int:
        """
        Index a document (PDF or markdown).

        Returns number of chunks indexed.
        """
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check if already indexed (unless force)
        if not force:
            existing = self.collection.get(
                where={"source_file": str(file_path)},
                limit=1
            )
            if existing['ids']:
                print(f"Already indexed: {file_path.name} (use --force to reindex)")
                return 0

        # Extract text based on file type
        suffix = file_path.suffix.lower()

        if suffix == '.pdf':
            pages = extract_pdf_text(file_path)
            all_chunks = []
            for text, page_num in pages:
                chunks = chunk_text(text)
                for chunk in chunks:
                    all_chunks.append({
                        'text': chunk,
                        'page': page_num,
                        'source': str(file_path),
                        'filename': file_path.name
                    })

        elif suffix in ['.md', '.txt']:
            text = extract_markdown_text(file_path)
            chunks = chunk_text(text)
            all_chunks = [{
                'text': chunk,
                'page': 1,
                'source': str(file_path),
                'filename': file_path.name
            } for chunk in chunks]

        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        if not all_chunks:
            print(f"No text extracted from: {file_path.name}")
            return 0

        # Delete existing entries for this file (for reindexing)
        try:
            self.collection.delete(where={"source_file": str(file_path)})
        except Exception:
            pass

        # Generate embeddings
        texts = [c['text'] for c in all_chunks]
        embeddings = self.model.encode(texts, show_progress_bar=False)

        # Prepare for ChromaDB
        ids = [f"{file_path.stem}_{i}_{compute_hash(c['text'])}"
               for i, c in enumerate(all_chunks)]

        metadatas = [{
            'source_file': c['source'],
            'filename': c['filename'],
            'page': c['page'],
            'chunk_index': i
        } for i, c in enumerate(all_chunks)]

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas
        )

        print(f"Indexed: {file_path.name} ({len(all_chunks)} chunks)")
        return len(all_chunks)

    def index_directory(self, dir_path: Path, recursive: bool = True,
                        force: bool = False) -> int:
        """Index all supported files in a directory."""
        dir_path = Path(dir_path).resolve()

        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {dir_path}")

        pattern = "**/*" if recursive else "*"
        extensions = ['.pdf', '.md', '.txt']

        total_chunks = 0
        for ext in extensions:
            for file_path in dir_path.glob(pattern + ext):
                try:
                    total_chunks += self.index_document(file_path, force=force)
                except Exception as e:
                    print(f"Error indexing {file_path.name}: {e}")

        return total_chunks

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for relevant document chunks.

        Returns list of results with text, source, and similarity score.
        """
        # Generate query embedding
        query_embedding = self.model.encode([query])[0]

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )

        # Format results
        formatted = []
        for i in range(len(results['ids'][0])):
            formatted.append({
                'text': results['documents'][0][i],
                'source': results['metadatas'][0][i]['filename'],
                'page': results['metadatas'][0][i]['page'],
                'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                'source_path': results['metadatas'][0][i]['source_file']
            })

        return formatted

    def list_documents(self) -> List[Dict]:
        """List all indexed documents with chunk counts."""
        # Get all unique source files
        all_items = self.collection.get(include=['metadatas'])

        doc_counts = {}
        for meta in all_items['metadatas']:
            filename = meta['filename']
            if filename not in doc_counts:
                doc_counts[filename] = {
                    'filename': filename,
                    'path': meta['source_file'],
                    'chunks': 0
                }
            doc_counts[filename]['chunks'] += 1

        return list(doc_counts.values())

    def clear(self):
        """Clear all indexed documents."""
        chromadb = get_chromadb()
        self.client.delete_collection("paleoseismic_papers")
        self.collection = self.client.get_or_create_collection(
            name="paleoseismic_papers",
            metadata={"hnsw:space": "cosine"}
        )
        print("Index cleared.")

    def stats(self) -> Dict:
        """Get database statistics."""
        count = self.collection.count()
        docs = self.list_documents()
        return {
            'total_chunks': count,
            'total_documents': len(docs),
            'db_path': str(self.db_path)
        }


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="RAG system for paleoseismic research papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Index command
    index_parser = subparsers.add_parser("index", help="Index documents")
    index_parser.add_argument("path", help="File or directory to index")
    index_parser.add_argument("--recursive", "-r", action="store_true",
                             help="Recursively index directories")
    index_parser.add_argument("--force", "-f", action="store_true",
                             help="Force reindex existing documents")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search indexed documents")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--top", "-n", type=int, default=5,
                              help="Number of results")

    # List command
    subparsers.add_parser("list", help="List indexed documents")

    # Stats command
    subparsers.add_parser("stats", help="Show database statistics")

    # Clear command
    subparsers.add_parser("clear", help="Clear all indexed documents")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize database
    db = RAGDatabase()

    if args.command == "index":
        path = Path(args.path)
        if path.is_file():
            db.index_document(path, force=args.force)
        else:
            db.index_directory(path, recursive=args.recursive, force=args.force)

    elif args.command == "search":
        results = db.search(args.query, top_k=args.top)

        if not results:
            print("No results found.")
            return

        print(f"\nSearch: \"{args.query}\"\n")
        print("=" * 60)

        for i, r in enumerate(results, 1):
            print(f"\n[{i}] {r['source']} (p.{r['page']}) - {r['similarity']:.2f}")
            print("-" * 40)
            # Truncate long text
            text = r['text']
            if len(text) > 300:
                text = text[:300] + "..."
            print(text)

    elif args.command == "list":
        docs = db.list_documents()
        if not docs:
            print("No documents indexed.")
            return

        print(f"\nIndexed Documents ({len(docs)}):\n")
        for doc in sorted(docs, key=lambda x: x['filename']):
            print(f"  {doc['filename']:40} ({doc['chunks']} chunks)")

    elif args.command == "stats":
        stats = db.stats()
        print(f"\nRAG Database Statistics:")
        print(f"  Documents:  {stats['total_documents']}")
        print(f"  Chunks:     {stats['total_chunks']}")
        print(f"  Location:   {stats['db_path']}")

    elif args.command == "clear":
        confirm = input("Clear all indexed documents? [y/N] ")
        if confirm.lower() == 'y':
            db.clear()
        else:
            print("Cancelled.")


if __name__ == "__main__":
    main()
