"""
RAG Tool for retrieving content summaries from PDF documents.
"""

import logging
import os
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings

logger = logging.getLogger(__name__)


class RAGTool:
    """Tool for RAG (Retrieval-Augmented Generation) using ChromaDB and PDFs."""
    
    def __init__(self, summaries_dir: str, ollama_base_url: str, embedding_model: str, chroma_db_dir: str):
        """
        Initialize the RAG Tool.
        
        Args:
            summaries_dir: Path to directory containing PDF summaries
            ollama_base_url: Base URL for Ollama API
            embedding_model: Name of the embedding model (e.g., nomic-embed-text)
            chroma_db_dir: Path to ChromaDB persistent storage
        """
        self.summaries_dir = summaries_dir
        self.embedding_model = embedding_model
        
        logger.info(f"Initializing RAGTool with summaries from: {summaries_dir}")
        
        # Initialize Ollama embeddings
        self.embeddings = OllamaEmbeddings(
            model=embedding_model,
            base_url=ollama_base_url
        )
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=chroma_db_dir)
        self.collection = self.client.get_or_create_collection(
            name="content_summaries",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Auto-initialize vector store if empty
        self._initialize_if_needed()
        
        logger.info(f"RAGTool initialized with {self.collection.count()} documents in vector store")
    
    def _initialize_if_needed(self):
        """Initialize vector store if it's empty."""
        if self.collection.count() > 0:
            logger.info("Vector store already populated, skipping initialization")
            return
        
        logger.info("Vector store is empty, initializing with PDFs...")
        self.initialize_vector_store()
    
    def initialize_vector_store(self):
        """Load all PDFs from summaries directory and create embeddings."""
        if not os.path.exists(self.summaries_dir):
            logger.error(f"Summaries directory not found: {self.summaries_dir}")
            return
        
        pdf_files = [f for f in os.listdir(self.summaries_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.summaries_dir}")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files, processing...")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            try:
                pdf_path = os.path.join(self.summaries_dir, pdf_file)
                logger.info(f"[{i}/{len(pdf_files)}] Loading {pdf_file}...")
                
                # Load PDF
                loader = PyPDFLoader(pdf_path)
                pages = loader.load()
                
                # Combine all pages into one document
                text = "\n".join([page.page_content for page in pages])
                
                # Skip empty documents
                if not text.strip():
                    logger.warning(f"Skipping empty PDF: {pdf_file}")
                    continue
                
                # Generate embedding
                logger.info(f"[{i}/{len(pdf_files)}] Generating embedding for {pdf_file}...")
                embedding = self.embeddings.embed_query(text)
                
                # Store in ChromaDB
                # Use filename without extension as ID for easy lookup
                doc_id = os.path.splitext(pdf_file)[0]
                
                self.collection.add(
                    documents=[text],
                    embeddings=[embedding],
                    ids=[doc_id],
                    metadatas=[{"filename": pdf_file, "title": doc_id}]
                )
                
                logger.info(f"[{i}/{len(pdf_files)}] Successfully added {pdf_file} to vector store")
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {e}", exc_info=True)
                continue
        
        logger.info(f"Vector store initialization complete! Total documents: {self.collection.count()}")
    
    def search(self, query: str, top_k: int = 3) -> dict:
        """
        Search for relevant documents based on query.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            Dictionary with success status, documents, and metadata
        """
        try:
            logger.info(f"Searching for: '{query}' (top_k={top_k})")
            
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            distances = results['distances'][0] if results['distances'] else []
            
            # Convert distances to similarity scores (1 - cosine distance)
            similarities = [1 - dist for dist in distances]
            
            logger.info(f"Found {len(documents)} relevant documents")
            for i, (meta, sim) in enumerate(zip(metadatas, similarities)):
                logger.info(f"  [{i+1}] {meta.get('title', 'Unknown')} (similarity: {sim:.3f})")
            
            return {
                "success": True,
                "documents": documents,
                "metadatas": metadatas,
                "similarities": similarities,
                "count": len(documents)
            }
            
        except Exception as e:
            error_msg = f"Error searching documents: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg,
                "documents": [],
                "metadatas": [],
                "similarities": [],
                "count": 0
            }
    
    def get_document_by_title(self, title: str) -> dict:
        """
        Retrieve a specific document by title.
        
        Args:
            title: Title of the document (without .pdf extension)
            
        Returns:
            Dictionary with success status and document content
        """
        try:
            logger.info(f"Retrieving document by title: '{title}'")
            
            # Normalize title (replace spaces with underscores)
            normalized_title = title.replace(" ", "_")
            
            # Try to get document by ID
            results = self.collection.get(
                ids=[normalized_title],
                include=["documents", "metadatas"]
            )
            
            if results['documents']:
                logger.info(f"Found document: {normalized_title}")
                return {
                    "success": True,
                    "document": results['documents'][0],
                    "metadata": results['metadatas'][0] if results['metadatas'] else {}
                }
            else:
                logger.warning(f"Document not found: {normalized_title}")
                return {
                    "success": False,
                    "error": f"Document '{title}' not found in vector store"
                }
                
        except Exception as e:
            error_msg = f"Error retrieving document: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg
            }
