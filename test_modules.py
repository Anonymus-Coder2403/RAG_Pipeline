"""
Simple test script to verify all modules are working
"""

def test_imports():
    """Test 1: Verify all modules can be imported"""
    print("\n[TEST 1] Testing imports...")
    try:
        from src import (
            PDFDocumentLoader,
            EmbeddingManager,
            VectorStore,
            RAGRetriever,
            GeminiLLM,
            RAGPipeline
        )
        print("✅ All modules imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_vector_store():
    """Test 2: Check existing vector store"""
    print("\n[TEST 2] Testing vector store connection...")
    try:
        from src import VectorStore
        vector_store = VectorStore()
        stats = vector_store.get_collection_stats()
        print(f"✅ Vector store connected!")
        print(f"   Collection: {stats['name']}")
        print(f"   Documents: {stats['count']}")
        return True
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False


def test_embedding_manager():
    """Test 3: Test embedding generation"""
    print("\n[TEST 3] Testing embedding generation...")
    try:
        from src import EmbeddingManager
        embedding_manager = EmbeddingManager()

        # Test with a simple sentence
        test_text = ["This is a test sentence for embeddings."]
        embeddings = embedding_manager.generate_embeddings(test_text, show_progress=False)

        print(f"✅ Embeddings generated!")
        print(f"   Shape: {embeddings.shape}")
        print(f"   Dimension: {embedding_manager.get_embedding_dimension()}")
        return True
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False


def test_retriever():
    """Test 4: Test document retrieval"""
    print("\n[TEST 4] Testing document retrieval...")
    try:
        from src import VectorStore, EmbeddingManager, RAGRetriever

        vector_store = VectorStore()
        embedding_manager = EmbeddingManager()
        retriever = RAGRetriever(vector_store, embedding_manager)

        # Test retrieval
        results = retriever.retrieve("What is news?", top_k=2)

        print(f"✅ Retrieval working!")
        print(f"   Retrieved {len(results)} documents")
        if results:
            print(f"   Top similarity: {results[0]['similarity_score']:.1%}")
        return True
    except Exception as e:
        print(f"❌ Retrieval test failed: {e}")
        return False


def test_llm():
    """Test 5: Test Gemini LLM"""
    print("\n[TEST 5] Testing Gemini LLM...")
    try:
        from src import GeminiLLM

        llm = GeminiLLM()

        # Simple test prompt
        response = llm.generate("Say 'Hello, RAG pipeline is working!' in one sentence.")

        print(f"✅ LLM working!")
        print(f"   Response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        print(f"   Make sure your .env file has GEMINI_API_KEY set")
        return False


def test_full_pipeline():
    """Test 6: Test complete RAG pipeline"""
    print("\n[TEST 6] Testing complete RAG pipeline...")
    try:
        from src import (
            VectorStore,
            EmbeddingManager,
            RAGRetriever,
            GeminiLLM,
            RAGPipeline
        )

        # Initialize components
        vector_store = VectorStore()
        embedding_manager = EmbeddingManager()
        retriever = RAGRetriever(vector_store, embedding_manager)
        llm = GeminiLLM()
        rag = RAGPipeline(retriever, llm)

        # Test query
        result = rag.answer("What is news?", top_k=2)

        print(f"✅ Full RAG pipeline working!")
        print(f"   Answer length: {len(result['answer'])} characters")
        print(f"   Sources: {len(result['sources'])}")
        print(f"\n   Preview: {result['answer'][:150]}...")
        return True
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("RAG PIPELINE MODULE TESTS")
    print("=" * 80)

    tests = [
        test_imports,
        test_vector_store,
        test_embedding_manager,
        test_retriever,
        test_llm,
        test_full_pipeline
    ]

    results = []
    for test in tests:
        results.append(test())

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed! Your modular code is working perfectly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")

    print("=" * 80)


if __name__ == "__main__":
    main()
