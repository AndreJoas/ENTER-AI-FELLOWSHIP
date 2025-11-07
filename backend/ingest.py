import os
import numpy as np
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

PDF_DIR = "../data"
INDEX_DIR = "../vectordb/faiss_index_pdfs"
os.makedirs(INDEX_DIR, exist_ok=True)

# ============================================================
# Funções auxiliares
# ============================================================

def extract_text_from_pdf(pdf_path):
    """Extrai texto do PDF."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip().replace("\n", " ")
    except Exception as e:
        print(f"❌ Erro ao ler {pdf_path}: {e}")
        return ""

def chunk_text(text, chunk_size=150):
    """Divide texto em chunks menores."""
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# ============================================================
# Função principal de ingestão
# ============================================================

def ingest_faiss(pdf_path: str = None):
    """
    Cria ou atualiza a base FAISS com PDFs de ../data ou com um PDF específico.
    Retorna informações sobre o índice criado.
    """
    docs, metadatas = [], []

    # Se for um único arquivo
    if pdf_path:
        files = [pdf_path]
    else:
        files = [os.path.join(PDF_DIR, f) for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]

    for path in files:
        file = os.path.basename(path)
        print(f"📄 Extraindo texto de: {file}")
        text = extract_text_from_pdf(path)
        if not text:
            continue
        chunks = chunk_text(text)
        docs.extend(chunks)
        metadatas.extend([{"source": file}] * len(chunks))

    if not docs:
        return {"status": "error", "message": "Nenhum texto extraído."}

    print(f"✅ {len(docs)} chunks extraídos de {len(files)} PDF(s).")

    emb = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1")

    embeddings = [np.array(emb.embed_query(doc), dtype="float32") for doc in docs]
    embeddings = [vec / np.linalg.norm(vec) for vec in embeddings]

    vs = FAISS.from_texts(docs, emb, metadatas=metadatas)
    vs.save_local(INDEX_DIR)

    print("✅ Base FAISS criada e normalizada com sucesso em:", INDEX_DIR)

    return {
        "status": "ok",
        "index_path": INDEX_DIR,
        "num_docs": len(docs),
        "files_indexed": [os.path.basename(f) for f in files]
    }

# ============================================================
# Execução direta (CLI)
# ============================================================

if __name__ == "__main__":
    result = ingest_faiss()
    print(result)
