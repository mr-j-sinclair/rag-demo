from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from rag_demo.pipeline import RAGPipeline


def test_ask_uses_context_and_returns_llm_response():
    # Store the prompt received by the stub LLM so we can inspect it later
    received_prompts = []

    def retrieve_documents(question):
        # Return predictable dummy data instead of searching a real vector store
        return [
            Document(page_content="Ada Lovelace was an early computing pioneer.")
        ]

    def return_stub_response(prompt):
        # Record the real prompt constructed by RAG Pipleline
        received_prompts.append(prompt.to_string())

        # Return a fixed response instead of calling the OpenAI API
        return AIMessage(content="Ada Lovelace was a computing pioneer")

    # Create an .invoke() interface for the functions using RunnableLambda
    stub_retriever = RunnableLambda(retrieve_documents)
    stub_llm = RunnableLambda(return_stub_response)

    ## Create a RAGPipeline object using the stub calls
    pipeline = RAGPipeline(
        retriever = stub_retriever,
        llm = stub_llm,
    )

    result = pipeline.ask("Who was Ada Lovelace?")

    # Confirm the output parser returned the sub message as a string 
    assert result == "Ada Lovelace was a computing pioneer"

    # Confirm the prompt contained both the context and question

        # Context
    assert "Ada Lovelace was an early computing pioneer." in received_prompts[0]

        # (users) Question
    assert "Who was Ada Lovelace?" in received_prompts[0]

     
