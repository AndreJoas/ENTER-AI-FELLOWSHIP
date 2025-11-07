# tools/tool_faiss.py
import re
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

INDEX_DIR = "../vectordb/faiss_index_pdfs"

emb = HuggingFaceEmbeddings(
    model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
)

db = FAISS.load_local(INDEX_DIR, emb, allow_dangerous_deserialization=True)

def busca_faiss(query: str, k: int = 5, min_score: float = 0.7, boost_factor: float = 1.2):
    """
    Busca semântica + boost por correspondência exata de números.
    """
    print(f"\n🔎 Query recebida: {query}")
    
    results_with_score = db.similarity_search_with_score(query, k=k)
    print(f"\n📌 Resultados brutos encontrados: {len(results_with_score)}")
    
    numbers_in_query = re.findall(r"\d+[.,]?\d*", query)
    boosted_results = []
    for res, score in results_with_score:
        score = float(score)
        content_lower = res.page_content.lower()
        for num in numbers_in_query:
            if num in content_lower:
                score *= boost_factor
        boosted_results.append((res, score))
    
    filtered = [(res, score) for res, score in boosted_results if score >= min_score]
    filtered.sort(key=lambda x: x[1], reverse=True)
    
    output = []
    for res, score in filtered:
        output.append({
            "source": res.metadata.get("source", "unknown"),
            "content": res.page_content[:500] + "...",
            "score": score
        })
    
    if not output:
        return "Nenhum resultado atingiu o score mínimo definido."
    
    return output
