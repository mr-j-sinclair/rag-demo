import pytest

from rag_demo.knowledge_base import KnowledgeBase


def test_dense_retriever_finds_ada_lovelace_document():
    # build a knowledge base using the local embedding model
    knowledge_base = KnowledgeBase()
    knowledge_base.build_index("data")

    # Create a  retriever that returns the three closest chunks
    retriever = knowledge_base.as_retriever(k=3, mode="dense")

    # Search the vector store using a question about Ada Lovelace
    documents = retriever.invoke("Who was Ada Lovelace?")

    # Extract the source filename from each retrieved document 
    sources = [document.metadata["source"] for document in documents]

    # At least one retrieved chunk should come from Ada's document
    assert "adalovelace.txt" in sources


def test_sparse_retriever_finds_exact_distinctive_term():
    # Integration test using the real documents and BM25 implementation
    knowledge_base = KnowledgeBase()
    knowledge_base.build_index("data")

    # Create a  retriever that returns the three closest chunks
    retriever = knowledge_base.as_retriever(k=3, mode="sparse")

    # Search BM25 using an exact term from the Ada Lovelace document.
    documents = retriever.invoke("Flyology")

    # Extract the source filename from each retrieved document
    sources = [document.metadata["source"] for document in documents]

    # At least one retrieved chunk should come from Ada's document
    assert "adalovelace.txt" in sources


def test_hybrid_retriever_finds_jupiter_document():
    # Integration test using both real dense and sparse retrieval
    knowledge_base = KnowledgeBase()
    knowledge_base.build_index("data")

    # Hybrid Retriever
    retriever = knowledge_base.as_retriever(k=3, mode="hybrid")

    # Search a distinctive phrase from the Jupiter document.
    documents = retriever.invoke("Great Red Spot")

    # Extract the source filename from each retrieved document
    sources = [document.metadata["source"] for document in documents]

    # The retrieved chunks should include the Jupiter document.
    assert "jupiter.txt" in sources


def test_retriever_rejects_invalid_mode():
    # Unit test: verify unsupported configuration fails clearly.
    knowledge_base = KnowledgeBase()

    with pytest.raises(
        ValueError, match="Invalid retrieval mode 'wrong'"
    ):
        knowledge_base.as_retriever(mode="wrong")
