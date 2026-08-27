from rag_demo.knowledge_base import KnowledgeBase


def test_retriever_finds_ada_lovelace_document():
    # build a knowledge base using the local embedding model
    knowledge_base = KnowledgeBase()
    knowledge_base.build_index("data")

    # Create a  retriever that returns the three closest chunks
    retriever = knowledge_base.as_retriever(k=3)

    # Search the vector store using a question about Ada Lovelace
    documents = retriever.invoke("Who was Ada Lovelace?")

    # Extract the source filename from each retrieved document 
    sources = [document.metadata["source"] for document in documents]

    # At least one retrieved chunk should come from Ada's document
    assert "adalovelace.txt" in sources

