from pprint import pprint

from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_demo.documents import load_documents


class KnowledgeBase:
    def __init__(
        self,
        # Public Hugging Face Model ID.
        model_path="sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ):

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # construct HuggingFaceEmbeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=model_path)

    def split_documents(self, documents: list[Document]) -> list[Document]:

        return self.text_splitter.split_documents(documents)

    def build_index(self, folder_path: str) -> None:
        # 1. load documents (reuse your Step A function)
        # 2. split them (reuse split_documents)
        # 3. build self.vector_store from the chunks + self.embeddings

        documents = load_documents(folder_path)

        if not documents:
            return

        # Keep the chunks on this KnowledgeBase instance so both the
        # dense vector store and the sparse BM25 retriever can use them.
        self.chunks = self.split_documents(documents)

        self.vector_store = InMemoryVectorStore.from_documents(
            documents=self.chunks,
            embedding=self.embeddings,
        )

    def as_retriever(self, k: int = 5, mode: str = "hybrid"):
        """Return a dense, sparse, or hybrid retriever."""

        # Reject unsupported modes before constructing any retrievers
        valid_modes = {"dense", "sparse", "hybrid"}

        if mode not in valid_modes:
            raise ValueError(  # noqa: TRY003
                f"Invalid retrieval mode {mode!r}. Expected one of: 'dense', 'sparse', or 'hybrid'."
            )

        # Dense retrieval embeds the query and compares it with chunk embeddings.
        if mode in {"dense", "hybrid"}:
            dense_retriever = self.vector_store.as_retriever(search_kwargs={"k": k})

        # Sparse retrieval indexes and matches literal terms using BM25.
        if mode in {"sparse", "hybrid"}:
            sparse_retriever = BM25Retriever.from_documents(self.chunks)
            sparse_retriever.k = k

        if mode == "dense":
            return dense_retriever

        if mode == "sparse":
            return sparse_retriever

        # Hybrid mode combines both ranked lists using equal starting weights.
        return EnsembleRetriever(
            retrievers=[dense_retriever, sparse_retriever],
            weights=[0.5, 0.5],
        )


if __name__ == "__main__":
    kb = KnowledgeBase()
    kb.build_index("data")

    retriever = kb.as_retriever(k=3)
    print("\n")
    print(f"type(retriever) = {type(retriever)}")

    docs = retriever.invoke("Tell me about Jupiter")

    print(f"len(docs) = {len(docs)}")

    print(f"type(docs[0]) = {type(docs[0])}")

    print(f"docs[0].metadata = {docs[0].metadata}")

    ## Compare againt the manual way of doing it
    manual_docs = kb.vector_store.similarity_search(
        "Tell me about Jupiter",
        k=3,
    )

    print(f"""using the retriever
{[doc.metadata for doc in docs]}

manual way (call kb.vector_store.similarity_search() direct)
{[doc.metadata for doc in manual_docs]}""")

    ## Try the runnables interface
    results = retriever.batch(["Tell me about Jupiter", "What is Crispr?", "Who was Ada Lovelace?"])

    print()
    print(f"type(results) = {type(results)}")
    print(f"len(results) = {len(results)}")
    print()
    print(f"[len(group) for group in results] = \n{[len(group) for group in results]}")
    print()
    print("[[doc.metadata for doc in group] for group in results]")
    pprint([[doc.metadata for doc in group] for group in results])
    print()
