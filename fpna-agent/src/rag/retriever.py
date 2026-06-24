from typing import Dict, List, Any, Optional
import logging
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class RAGRetriever:
    """RAG retriever that works with the fixed VectorStore"""
    
    def __init__(self, vector_store, monitor_agent=None):
        self.vector_store = vector_store
        self.monitor_agent = monitor_agent
        
    def find_evidence_for_variance(self, variance: Dict, department: str) -> Dict[str, Any]:
        """Find relevant evidence for a variance"""
        try:
            # Create search queries
            queries = self._generate_search_queries(variance, department)
            
            all_documents = []
            for query in queries:
                try:
                    # Use the vector_store's search method
                    docs = self._perform_search(query)
                    if docs:
                        all_documents.extend(docs)
                except Exception as e:
                    logger.warning(f"Search failed for '{query}': {e}")
            
            # Remove duplicates
            unique_documents = self._remove_duplicates(all_documents)
            
            # Organize by type
            organized_docs = self._organize_documents(unique_documents)
            
            summary = f"Found {len(unique_documents)} relevant documents"
            if unique_documents:
                doc_types = [t for t, d in organized_docs.items() if d]
                summary += f" ({', '.join(doc_types)})"
            
            return {
                "total_found": len(unique_documents),
                "documents": unique_documents,
                "organized_documents": organized_docs,
                "summary": summary,
                "queries_used": queries
            }
            
        except Exception as e:
            logger.error(f"Error finding evidence: {e}")
            return {
                "total_found": 0,
                "documents": [],
                "organized_documents": {},
                "summary": f"No documents found: {str(e)}",
                "queries_used": []
            }
    
    def _perform_search(self, query: str, k: int = 5) -> List[Document]:
        """Perform similarity search using VectorStore"""
        try:
            # Method 1: Use vector_store.search() if available
            if hasattr(self.vector_store, 'search'):
                return self.vector_store.search(query, k=k)
            
            # Method 2: Use vector_store.similarity_search()
            elif hasattr(self.vector_store, 'similarity_search'):
                return self.vector_store.similarity_search(query, k=k)
            
            # Method 3: Use vector_store.store.similarity_search()
            elif hasattr(self.vector_store, 'store') and hasattr(self.vector_store.store, 'similarity_search'):
                return self.vector_store.store.similarity_search(query, k=k)
            
            # Method 4: Try to get store and search
            else:
                # Try to access the underlying store
                store = self.vector_store.get_store() if hasattr(self.vector_store, 'get_store') else None
                if store and hasattr(store, 'similarity_search'):
                    return store.similarity_search(query, k=k)
                
                logger.warning("No search method available in vector store")
                return []
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _generate_search_queries(self, variance: Dict, department: str) -> List[str]:
        """Generate search queries based on variance"""
        account = variance.get('account_name', '').lower()
        dept = department.lower()
        amount = abs(variance.get('variance_amount', 0))
        
        queries = []
        
        # Basic queries
        queries.append(f"{dept} {account}")
        queries.append(f"{account} {dept}")
        queries.append(f"{account} expense")
        queries.append(f"{dept} department {account}")
        
        # Specific queries based on account type
        if "advertising" in account:
            queries.append(f"{dept} marketing campaign")
            queries.append(f"digital ads {dept}")
            queries.append(f"social media advertising {dept}")
        
        if "software" in account or "license" in account:
            queries.append(f"{dept} software subscription")
            queries.append(f"technology license {dept}")
            queries.append(f"SaaS {dept}")
        
        if "consulting" in account or "fees" in account:
            queries.append(f"{dept} professional services")
            queries.append(f"consultant {dept}")
            queries.append(f"advisor {dept}")
        
        if "travel" in account:
            queries.append(f"{dept} business trip")
            queries.append(f"travel expense {dept}")
            queries.append(f"flight hotel {dept}")
        
        # Add amount for significant variances
        if amount > 10000:
            queries.append(f"${amount:,.0f} {account} {dept}")
        
        return queries
    
    def _remove_duplicates(self, documents: List[Document]) -> List[Document]:
        """Remove duplicate documents"""
        unique = []
        seen = set()
        
        for doc in documents:
            # Create identifier from content and metadata
            content_hash = hash(doc.page_content[:500])
            source = doc.metadata.get('source', '')
            doc_id = f"{content_hash}_{source}"
            
            if doc_id not in seen:
                seen.add(doc_id)
                unique.append(doc)
        
        return unique
    
    def _organize_documents(self, documents: List[Document]) -> Dict[str, List[Document]]:
        """Organize documents by type"""
        organized = {
            "invoices": [],
            "contracts": [],
            "approvals": [],
            "reports": [],
            "emails": [],
            "other": []
        }
        
        for doc in documents:
            content = doc.page_content.lower()
            source = doc.metadata.get('source', '').lower()
            
            # Check for document types
            if any(word in content or word in source for word in ['invoice', 'bill', 'receipt', 'payment']):
                organized['invoices'].append(doc)
            elif any(word in content or word in source for word in ['contract', 'agreement', 'terms', 'license']):
                organized['contracts'].append(doc)
            elif any(word in content or word in source for word in ['approval', 'authorization', 'signed', 'approved', 'signature']):
                organized['approvals'].append(doc)
            elif any(word in content or word in source for word in ['report', 'analysis', 'summary', 'review']):
                organized['reports'].append(doc)
            elif any(word in content or word in source for word in ['email', 'message', 'memo', 'note']):
                organized['emails'].append(doc)
            else:
                organized['other'].append(doc)
        
        return organized
    
    def retrieve_relevant_documents(self, query: str, k: int = 5) -> Dict[str, Any]:
        """Retrieve relevant documents for a query"""
        try:
            docs = self._perform_search(query, k)
            organized = self._organize_documents(docs)
            
            # Create summary
            summary_parts = []
            for doc_type, doc_list in organized.items():
                if doc_list:
                    summary_parts.append(f"{len(doc_list)} {doc_type}")
            
            summary = f"Found {len(docs)} documents"
            if summary_parts:
                summary += f" ({', '.join(summary_parts)})"
            
            return {
                "total_found": len(docs),
                "documents": docs,
                "organized_documents": organized,
                "summary": summary,
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return {
                "total_found": 0,
                "documents": [],
                "organized_documents": {},
                "summary": f"Error: {str(e)}",
                "query": query
            }
    
    # For backward compatibility
    def retrieve_relevant_documents_with_filter(self, query: str, document_types: Optional[List[str]] = None, k: int = 5) -> Dict[str, Any]:
        """Retrieve with type filtering"""
        result = self.retrieve_relevant_documents(query, k)
        
        if document_types and result['organized_documents']:
            filtered = []
            for doc_type in document_types:
                if doc_type in result['organized_documents']:
                    filtered.extend(result['organized_documents'][doc_type])
            
            result['documents'] = filtered
            result['total_found'] = len(filtered)
        
        return result
