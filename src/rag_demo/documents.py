from pathlib import Path

from langchain_core.documents import Document


def load_documents(folder_path: str) -> list[Document]:
    """
    - Finds all the .txt files in the /data folder.
    - Reads each file and constructs exactly one Document
    - the metadata["source"] should be the filename
    """

    folder = Path(folder_path)

    documents = []

    # print(f"loading files from /{folder}")

    files = folder.glob("*.txt")

    for file in files:
        documents.append(
            Document(
                page_content=file.read_text(),
                metadata={"source": file.name}
            )
        )

    return documents

if __name__ == "__main__":
    docs = load_documents("data")

    print(f"type(docs) = {type(docs)}")

    print(f"len(docs) = {len(docs)}")

    print(f"type(docs[0]) = {type(docs[0])}")

    print(f"docs[0].metadata = {docs[0].metadata}")

    print(f"len(docs[0].page_content) = {len(docs[0].page_content)}")