from langchain_core.documents import Document

from rag_demo.formatting import format_docs


def test_format_docs_joins_page_content():
    documents = [
        Document(page_content="First document"),
        Document(page_content="Second document"),
    ]

    result = format_docs(documents)

    assert result == "First document\n\nSecond document"

