import logging
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from chatbot.llm import get_llm
from chatbot.retriever import get_retriever, get_vectorstore
from chatbot.prompts import qa_prompt

logger = logging.getLogger("ab-chatbot.chain")

class MergedRetriever:
    def __init__(self, default_col, uploaded_col):
        self.default_retriever = get_retriever(default_col)
        self.uploaded_col = uploaded_col
        self.uploaded_retriever = None
        
        try:
            vectorstore = get_vectorstore(uploaded_col)
            info = vectorstore.client.get_collection(uploaded_col)
            if info.points_count > 0:
                self.uploaded_retriever = get_retriever(uploaded_col)
                logger.info(f"Initialized retriever for uploaded collection '{uploaded_col}' with {info.points_count} items.")
            else:
                logger.debug(f"Uploaded collection '{uploaded_col}' is empty.")
        except Exception as e:
            logger.debug(f"Uploaded collection '{uploaded_col}' not ready or empty: {e}")

    def get_relevant_documents(self, query):
        logger.info(f"Retrieving documents for query: '{query}'")
        try:
            docs = self.default_retriever.invoke(query)
            logger.info(f"Retrieved {len(docs)} documents from default collection.")
        except Exception as e:
            logger.error(f"Error retrieving from default collection: {e}", exc_info=True)
            docs = []

        if self.uploaded_retriever:
            try:
                uploaded_docs = self.uploaded_retriever.invoke(query)
                logger.info(f"Retrieved {len(uploaded_docs)} documents from uploaded collection.")
                docs.extend(uploaded_docs)
            except Exception as e:
                logger.error(f"Error retrieving from uploaded collection: {e}", exc_info=True)
        return docs

def ask_question(question: str):
    logger.info(f"Processing question: {question}")
    llm = get_llm()
    retriever = MergedRetriever("default_docs", "uploaded_docs")
    
    combine_docs_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    docs = retriever.get_relevant_documents(question)
    
    logger.info("Invoking QA combining chain...")
    response = combine_docs_chain.invoke({
        "context": docs,
        "question": question
    })
    
    sources = [doc.metadata.get('source', 'Unknown') for doc in docs]
    sources = list(set(sources))
    
    logger.info(f"QA response generated. Sources: {sources}")
    return {
        "answer": response,
        "sources": sources
    }
