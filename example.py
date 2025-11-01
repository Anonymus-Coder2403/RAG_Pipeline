"""
Example Usage of RAG Pipeline

This script demonstrates how to use the modular RAG pipeline.
"""

from src import (
    PDFDocumentLoader,
    EmbeddingManager,
    VectorStore,
    RAGRetriever,
    GeminiLLM,
    RAGPipeline
)


def main():
    """Main function demonstrating RAG pipeline usage"""

    print("=" * 80)
    print("RAG PIPELINE EXAMPLE")
    print("=" * 80)

    # Step 1: Load and process PDF documents
    print("\n[1/6] Loading PDF documents...")
    loader = PDFDocumentLoader(chunk_size=1000, chunk_overlap=200)
    chunks = loader.load_and_split("data/pdf")

    # Step 2: Initialize embedding model
    print("\n[2/6] Initializing embedding model...")
    embedding_manager = EmbeddingManager(model_name="all-MiniLM-L6-v2")

    # Step 3: Generate embeddings
    print("\n[3/6] Generating embeddings...")
    texts = [doc.page_content for doc in chunks]
    embeddings = embedding_manager.generate_embeddings(texts)

    # Step 4: Store in vector database
    print("\n[4/6] Storing in vector database...")
    vector_store = VectorStore(
        collection_name="pdf_documents",
        persist_directory="data/vector_store"
    )
    vector_store.add_documents(chunks, embeddings)

    # Step 5: Initialize retriever and LLM
    print("\n[5/6] Initializing retriever and LLM...")
    retriever = RAGRetriever(vector_store, embedding_manager)
    llm = GeminiLLM(
        model_name="gemini-2.5-flash",
        temperature=0.1,
        max_output_tokens=500
    )

    # Step 6: Create RAG pipeline and ask questions
    print("\n[6/6] Creating RAG pipeline...")
    rag = RAGPipeline(retriever, llm)

    # Example queries
    queries = [
        "What are news values?",
        "What is the definition of news?",
    ]

    for query in queries:
        print("\n" + "=" * 80)
        result = rag.answer(query, top_k=3)
        rag.display_result(result)
        print()


def quick_query_example():
    """
    Quick example for querying an existing vector store
    (use this if you've already processed documents)
    """
    print("=" * 80)
    print("QUICK QUERY EXAMPLE (Using existing vector store)")
    print("=" * 80)

    # Initialize components
    print("\n[1/3] Initializing components...")
    embedding_manager = EmbeddingManager(model_name="all-MiniLM-L6-v2")
    vector_store = VectorStore(
        collection_name="pdf_documents",
        persist_directory="data/vector_store"
    )

    print("\n[2/3] Setting up RAG pipeline...")
    retriever = RAGRetriever(vector_store, embedding_manager)
    llm = GeminiLLM(model_name="gemini-2.5-flash", temperature=0.1)
    rag = RAGPipeline(retriever, llm)

    print("\n[3/3] Asking question...")
    result = rag.answer("What are news values?", top_k=3)
    rag.display_result(result)


if __name__ == "__main__":
    # Uncomment the example you want to run:

    # Full pipeline (loads documents, creates embeddings, stores in DB)
    # main()

    # Quick query (uses existing vector store)
    quick_query_example()
