"""
RAG Pipeline Module

This module orchestrates the complete RAG pipeline: retrieval + generation.
"""

from typing import Dict, List


class RAGPipeline:
    """Complete RAG pipeline combining retrieval and generation"""

    def __init__(self, retriever, llm):
        """
        Initialize the RAG pipeline

        Args:
            retriever: RAGRetriever instance for document retrieval
            llm: GeminiLLM instance for answer generation
        """
        self.retriever = retriever
        self.llm = llm

    def answer(self, query: str, top_k: int = 3) -> Dict:
        """
        Complete RAG pipeline: Retrieve relevant context + Generate answer

        Args:
            query: User's question
            top_k: Number of relevant chunks to retrieve

        Returns:
            Dictionary with answer, sources, and metadata
        """
        print(f"📝 Query: {query}")
        print(f"🔍 Retrieving top {top_k} relevant chunks...\n")

        # Step 1: Retrieve relevant documents
        results = self.retriever.retrieve(query, top_k=top_k)

        if not results:
            return {
                "answer": "I couldn't find relevant information to answer this question.",
                "sources": [],
                "context_used": ""
            }

        # Step 2: Build context from retrieved chunks
        context_parts = []
        for i, doc_dict in enumerate(results, 1):
            content = doc_dict['content']
            metadata = doc_dict['metadata']
            source = metadata.get('source', 'Unknown')
            page = metadata.get('page', 'N/A')
            similarity = doc_dict['similarity_score']

            context_parts.append(f"[Source {i}: {source}, Page {page}]\n{content}")
            print(f"📄 Source {i}: {source} (Page {page}) - Similarity: {similarity:.1%}")

        context = "\n\n".join(context_parts)

        # Step 3: Build RAG prompt
        prompt = self._build_prompt(context, query)

        # Step 4: Generate answer
        print(f"\n🤖 Generating answer with Gemini...\n")
        answer = self.llm.generate(prompt)

        return {
            "answer": answer,
            "sources": [
                {
                    "source": doc_dict['metadata'].get('source', 'Unknown'),
                    "page": doc_dict['metadata'].get('page', 'N/A'),
                    "similarity": doc_dict['similarity_score'],
                    "content": doc_dict['content'][:200] + "..."  # Preview
                }
                for doc_dict in results
            ],
            "context_used": context
        }

    def _build_prompt(self, context: str, query: str) -> str:
        """
        Build the RAG prompt with context and query

        Args:
            context: Retrieved context from documents
            query: User's question

        Returns:
            Formatted prompt string
        """
        return f"""You are an expert AI assistant analyzing documents to provide accurate, comprehensive answers.

DOCUMENT CONTEXT:
{context}

USER QUESTION: {query}

INSTRUCTIONS FOR YOUR RESPONSE:
1. Carefully analyze all the provided document context above
2. Provide a clear, well-structured answer that directly addresses the user's question
3. If multiple sources contain relevant information, synthesize them into a coherent response
4. Use natural, conversational language while maintaining accuracy
5. Explain concepts clearly - don't just extract text, but help the user understand
6. After your answer, cite the specific sources you used in the format: (Source 1, Source 2, etc.)
7. If the context doesn't contain sufficient information to fully answer the question, acknowledge this honestly
8. Focus on being helpful and informative rather than overly brief

Please provide your comprehensive answer now:"""

    def display_result(self, result: Dict):
        """
        Display RAG pipeline result in a formatted way

        Args:
            result: Result dictionary from answer() method
        """
        print("=" * 80)
        print("ANSWER:")
        print("=" * 80)
        print(result['answer'])
        print("\n" + "=" * 80)
        print("SOURCES USED:")
        print("=" * 80)
        for i, source in enumerate(result['sources'], 1):
            print(f"\n{i}. {source['source']} (Page {source['page']}) - "
                  f"Similarity: {source['similarity']:.1%}")
            print(f"   Preview: {source['content']}")
