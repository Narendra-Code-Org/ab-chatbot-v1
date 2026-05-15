from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from chatbot.llm import get_llm
from chatbot.retriever import get_retriever, get_vectorstore
from chatbot.prompts import qa_prompt

class MergedRetriever:
    def __init__(self, default_col, uploaded_col):
        self.default_retriever = get_retriever(default_col)
        self.uploaded_col = uploaded_col
        self.uploaded_retriever = None
        
        try:
            get_vectorstore(uploaded_col).client.get_collection(uploaded_col)
            self.uploaded_retriever = get_retriever(uploaded_col)
        except:
            pass

    def get_relevant_documents(self, query):
        docs = self.default_retriever.invoke(query)
        if self.uploaded_retriever:
            try:
                uploaded_docs = self.uploaded_retriever.invoke(query)
                docs.extend(uploaded_docs)
            except:
                pass
        return docs

def ask_question(question: str):
    llm = get_llm()
    retriever = MergedRetriever("default_docs", "uploaded_docs")
    
    combine_docs_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    docs = retriever.get_relevant_documents(question)
    
    response = combine_docs_chain.invoke({
        "context": docs,
        "question": question
    })
    
    sources = [doc.metadata.get('source', 'Unknown') for doc in docs]
    sources = list(set(sources))
    
    return {
        "answer": response,
        "sources": sources
    }
