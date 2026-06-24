import os
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader,
)
import pandas as pd
import pdfplumber
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DocumentLoader:
    """Loads various document types for RAG system"""
    
    SUPPORTED_EXTENSIONS = {
        '.pdf': 'pdf',
        '.txt': 'text',
        '.csv': 'csv',
        '.docx': 'docx',
        '.doc': 'docx',
        '.xlsx': 'excel',
        '.xls': 'excel',
        '.json': 'json'
    }
    
    def __init__(self, upload_dir: str = "./data/uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    def load_document(self, file_path: str) -> List[Document]:
        """Load a single document based on file type"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                return self._load_pdf(file_path)
            elif file_extension == '.txt':
                loader = TextLoader(file_path)
                return loader.load()
            elif file_extension == '.csv':
                loader = CSVLoader(file_path)
                return loader.load()
            elif file_extension in ['.docx', '.doc']:
                loader = Docx2txtLoader(file_path)
                return loader.load()
            elif file_extension in ['.xlsx', '.xls']:
                loader = UnstructuredExcelLoader(file_path)
                return loader.load()
            elif file_extension == '.json':
                return self._load_json(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            raise
    
    def _load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF with metadata extraction"""
        documents = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                
                if text and text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": os.path.basename(file_path),
                            "page": page_num,
                            "file_type": "pdf",
                            "total_pages": len(pdf.pages),
                            "loaded_at": datetime.now().isoformat()
                        }
                    )
                    documents.append(doc)
        
        return documents
    
    def _load_json(self, file_path: str) -> List[Document]:
        """Load JSON documents"""
        import json
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        documents = []
        
        def process_dict(data_dict: Dict, parent_key: str = "") -> str:
            """Convert dictionary to text"""
            lines = []
            for key, value in data_dict.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                if isinstance(value, dict):
                    lines.append(f"{key}:")
                    lines.append(process_dict(value, full_key))
                elif isinstance(value, list):
                    lines.append(f"{key}:")
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            lines.append(f"  Item {i+1}:")
                            lines.append(process_dict(item, f"{full_key}[{i}]"))
                        else:
                            lines.append(f"  - {item}")
                else:
                    lines.append(f"{key}: {value}")
            return "\n".join(lines)
        
        if isinstance(data, dict):
            content = process_dict(data)
            doc = Document(
                page_content=content,
                metadata={
                    "source": os.path.basename(file_path),
                    "file_type": "json",
                    "loaded_at": datetime.now().isoformat()
                }
            )
            documents.append(doc)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    content = process_dict(item)
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": os.path.basename(file_path),
                            "item_index": i,
                            "file_type": "json",
                            "loaded_at": datetime.now().isoformat()
                        }
                    )
                    documents.append(doc)
        
        return documents
    
    def load_directory(self, directory_path: str) -> List[Document]:
        """Load all supported documents from a directory"""
        all_documents = []
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_extension = os.path.splitext(file)[1].lower()
                if file_extension in self.SUPPORTED_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    try:
                        documents = self.load_document(file_path)
                        all_documents.extend(documents)
                        logger.info(f"Loaded {len(documents)} documents from {file}")
                    except Exception as e:
                        logger.error(f"Failed to load {file}: {e}")
        
        return all_documents
    
    def extract_financial_documents(self, documents: List[Document]) -> Dict[str, List[Document]]:
        """Categorize documents by type for financial analysis"""
        categorized = {
            "invoices": [],
            "contracts": [],
            "approvals": [],
            "reports": [],
            "other": []
        }
        
        financial_keywords = {
            "invoices": ["invoice", "bill", "payment", "amount due", "total", "tax"],
            "contracts": ["contract", "agreement", "terms", "effective date", "termination"],
            "approvals": ["approved", "approval", "authorized", "signed", "signature"],
            "reports": ["report", "analysis", "summary", "quarterly", "monthly", "financial"]
        }
        
        for doc in documents:
            content_lower = doc.page_content.lower()
            doc_metadata = doc.metadata.copy()
            
            # Check for document type based on content and metadata
            doc_type = "other"
            max_matches = 0
            
            for doc_category, keywords in financial_keywords.items():
                matches = sum(1 for keyword in keywords if keyword in content_lower)
                if matches > max_matches:
                    max_matches = matches
                    doc_type = doc_category
            
            # Add type to metadata
            doc_metadata["document_type"] = doc_type
            doc.metadata = doc_metadata
            
            categorized[doc_type].append(doc)
        
        return categorized
