"""
Query Classification Module

Determines whether a query should use RAG (document-based) or general LLM response.
LLM is default, RAG is activated by trigger phrases.
"""

import re
from typing import Literal

QueryType = Literal["rag", "llm"]


class QueryClassifier:
    """Classifies user queries to route them appropriately"""

    # RAG trigger phrases - when user explicitly wants to search documents
    RAG_TRIGGERS = [
        # Direct search requests
        "search from pdf", "search from document", "search the pdf",
        "search in document", "search in pdf", "search this document",

        # Reference to sources
        "from this source", "from the source", "from this pdf",
        "from the document", "from this document", "in this pdf",
        "in the document", "in this document",

        # Document-specific queries
        "according to the document", "according to the pdf",
        "what does the document say", "what does the pdf say",
        "check the pdf", "check the document", "check this document",
        "look in the document", "look in the pdf",

        # Find/retrieve requests
        "find in document", "find in pdf", "retrieve from document",
        "get from document", "extract from document",

        # Contextual references
        "based on the document", "based on this pdf",
        "as per the document", "as mentioned in",

        # Natural variations (FIX-3)
        "tell me from the document", "what's in the document",
        "document says", "pdf says", "source material",
        "uploaded file", "my document", "the file",
        "from uploaded", "in uploaded", "what's in my pdf",
        "information from document", "data from pdf",
    ]

    def __init__(self):
        """Initialize the query classifier"""
        pass

    def classify(self, query: str) -> QueryType:
        """
        Classify the query type

        Args:
            query: User's input query

        Returns:
            QueryType: "rag" if trigger detected, "llm" otherwise
        """
        query_lower = query.lower().strip()

        # Check if query contains any RAG trigger phrases
        for trigger in self.RAG_TRIGGERS:
            if trigger in query_lower:
                return "rag"

        # Default to LLM (normal conversational AI)
        return "llm"

    def should_use_rag(self, query: str) -> bool:
        """
        Convenience method to check if RAG should be used

        Args:
            query: User's input query

        Returns:
            bool: True if RAG should be used, False otherwise
        """
        return self.classify(query) == "rag"
