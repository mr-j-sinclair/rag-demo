from langchain_core.documents import Document


def format_docs(docs: list[Document]) -> str:
    """
    Turn retrieved Documents into a single string for the prompt's {context}
    """
    page_contents = [doc.page_content for doc in docs]

    return "\n\n".join(page_contents)


if __name__ == "__main__":
    from rag_demo.knowledge_base import KnowledgeBase

    kb = KnowledgeBase()

    kb.build_index("data")

    retriever = kb.as_retriever(k=3)

    docs = retriever.invoke("Tell me about Jupiter")

    context = format_docs(docs)

    print(type(context))

    print(len(context))

    print(context)
