from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_openai import ChatOpenAI

from rag_demo.formatting import format_docs


class RAGPipeline: 
    def __init__(self, retriever, llm: ChatOpenAI):
        """Assemble the query-time RAG Chain"""
        # Build the prompt you already tested

        prompt = ChatPromptTemplate.from_template(

            """
            only answer the question from the retrieved context. 
            If the answer is not contained, simply state that you don't know.
            Don't use any outside knowledge.


            Context:
            {context}


            Question:
            {question}
            """ 
        )

        # Build:
        # retriever -> format_docs
        self.context_chain = retriever | RunnableLambda(format_docs)

        # Build
        # {
        #   "context": formatted retrieval branch,
        #   "question": unchanged question branch
        # }
        # connect:
        #parallel -> prompt -> llm -> string parser

        self.chain = RunnableParallel(
            context = self.context_chain,
            question = RunnablePassthrough()
        ) | prompt | llm | StrOutputParser()

        

    def ask(self, question: str) -> str:
        """Run one question through the assembled chain."""
        #Invoke self.chain using question

        answer_from_ai = self.chain.invoke(question)

        return answer_from_ai

if __name__ == "__main__":
    # Test running everything end to end

    from pprint import pprint

    from dotenv import load_dotenv

    from rag_demo.knowledge_base import KnowledgeBase

    load_dotenv()
        
    kb = KnowledgeBase()

    kb.build_index("data")

    retriever = kb.as_retriever(k=3)

    llm_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    rag_pipeline = RAGPipeline(
        retriever = retriever,
        llm = llm_model,
    )


    ai_response = rag_pipeline.ask("Who was Ada Lovelace?")

    print(f"type(ai_response) = {type(ai_response)} \n")

    print("ai_response = ")
    print(ai_response)

    print("="*50, "\n")

    steps = rag_pipeline.chain.steps

    print(f"len(steps) = {len(steps)}")

    pprint(f"type of each step = \n{ [type(step) for step in steps] }")

    question_2 = "What is Crispr?"

    ## Stage 1 - create a parallel - 
    # get context retriever
    # pass through question as a standalone by itself
    stage1 = steps[0].invoke(question_2)
    print(type(stage1))
    print(stage1.keys())
    print(type(stage1["context"]))
    print(type(stage1["question"]))

    # pass the retrieved context & original question into a ChatPromptTemplate
    # which contains {question} & {context}
    stage2 = steps[1].invoke(stage1)
    print(type(stage2))
    print(stage2)

    ## Pass in the full prompt (question & context) to the LLM
    stage3 = steps[2].invoke(stage2)
    print(type(stage3))
    print(stage3)
    print(stage3.content)

    ## Pass the AI's returned message through the String Outut Parser
    stage4 = steps[3].invoke(stage3)
    print(type(stage4))
    print(stage4)
    print(stage3.content == stage4)

    ## Check the response metadata
    pprint(stage3.response_metadata)