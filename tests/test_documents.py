from rag_demo.documents import load_documents


def test_load_documents_from_data_folder():
    # Call the real function using the project's real data folder
    documents = load_documents("data")

    # assert how many documents are in the data folder
    assert len(documents) == 4

    # collect every source filename stored in the document metadata
    sources = [document.metadata["source"] for document in documents]

    # Confirm that the know data file was loaded correctly
    assert "adalovelace.txt" in sources
