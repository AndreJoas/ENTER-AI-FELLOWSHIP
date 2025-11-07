import os
import re
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

INDEX_DIR = "../vectordb/faiss_index_pdfs"

# Embeddings (recomendado langchain-huggingface)
emb = HuggingFaceEmbeddings(
    model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
)

# Carregar índice FAISS
db = FAISS.load_local(INDEX_DIR, emb, allow_dangerous_deserialization=True)

def search_faiss(query: str, k: int = 5, min_score: float = 0.7, boost_factor: float = 1.2):
    """
    Busca semântica + boost por correspondência exata de números.
    """
    print(f"\n🔎 Query recebida: {query}")
    
    # Busca FAISS bruta
    results_with_score = db.similarity_search_with_score(query, k=k)
    print(f"\n📌 Resultados brutos (FAISS) encontrados: {len(results_with_score)}")
    
    for i, (res, score) in enumerate(results_with_score):
        print(f"  - Resultado {i+1}:")
        print(f"    Fonte: {res.metadata.get('source', 'unknown')}")
        print(f"    Score bruto: {score}")
        print(f"    Conteúdo (primeiros 100 chars): {res.page_content[:100]}...\n")
    
    # Detecta números na query
    numbers_in_query = re.findall(r"\d+[.,]?\d*", query)
    
    # Aplica boost se chunk contiver número da query
    boosted_results = []
    for res, score in results_with_score:
        score = float(score)
        content_lower = res.page_content.lower()
        for num in numbers_in_query:
            if num in content_lower:
                score *= boost_factor  # aumenta score
        boosted_results.append((res, score))
    
    # Filtra por score mínimo
    filtered = [(res, score) for res, score in boosted_results if score >= min_score]
    filtered.sort(key=lambda x: x[1], reverse=True)
    
    print(f"✅ Resultados após filtro min_score={min_score}: {len(filtered)}")
    
    # Formata saída JSON
    output = []
    for res, score in filtered:
        output.append({
            "source": res.metadata.get("source", "unknown"),
            "content": res.page_content,
            "score": score
        })
    
    return output

if __name__ == "__main__":
    query = "total geral 76.871,20 "
    results = search_faiss(query, k=3, min_score=0.7)

    print("\n🔹 Resultados finais formatados JSON:\n")
    print(json.dumps(results, indent=4, ensure_ascii=False))
