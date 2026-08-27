from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI

from rag_demo.knowledge_base import KnowledgeBase
from rag_demo.pipeline import RAGPipeline


def main():
    # 1.load_dotenv()
    load_dotenv(find_dotenv(usecwd=True))

    # 2. build a KnowledgeBase and build_index("data")
    kb = KnowledgeBase()
    kb.build_index("data")

    # 3. get a retriever
    retriever = kb.as_retriever(k=3)

    # 4. construct a ChatOpenAI llm
    ai_model = ChatOpenAI(model="gpt-4o-mini", temperature=0) 

    # 5. construct a RAGPipleine(retriever, llm)
    rag_pipeline = RAGPipeline(
        retriever = retriever,
        llm = ai_model
    ) 

    # 6. loop: prompt the user for a question, print pipeline.ask(question), repeat

    while True:
        users_question = input("\nask a question to AI: \n\n")
                               
        if users_question.lower() in ["bye", "exit", "quit"]:
            print("\nexiting session. Bye...\n")
            break
        else:
            ai_response = rag_pipeline.ask(users_question)
            print("\n"+ai_response)
        


if __name__ == "__main__":
    main()