from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.tools import tool
from tools import busca_faiss
from ingest import ingest_faiss
import os, json, time

load_dotenv()

# ==========================================================
# CONFIG FLASK
# ==========================================================
app = Flask(__name__, static_folder="static", static_url_path="/static")

# ==========================================================
# LLM CONFIG (rápido e barato)
# ==========================================================
model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

# ==========================================================
# TOOL: Busca semântica com FAISS
# ==========================================================
@tool
def search_pdf(query: str) -> str:
    """Busca semântica por conteúdo relevante no índice FAISS."""
    print(f"\n🔎 [FAISS] Query recebida: {query}")
    result = busca_faiss(query)
    if not result:
        return "Nenhum resultado encontrado no índice FAISS."

    formatted = "\n\n".join(
        [f"📄 Fonte: {r.get('source','?')}\n{r.get('content','')}" for r in result]
    )
    return formatted

tools = [search_pdf]

# ==========================================================
# PROMPT PRINCIPAL
# ==========================================================
system_prompt = """
Você é um agente de extração de informações estruturadas a partir de textos de PDFs (OCR já feito).

Objetivo:
- Extrair informações de forma precisa e consistente.
- Usar a ferramenta 'search_pdf' quando precisar buscar informações complementares.
- Retornar **apenas** o JSON com os campos do schema solicitado.

Exemplo de campos esperados:
{
  "nome": "Nome completo do profissional",
  "inscricao": "Número de inscrição na OAB",
  "seccional": "Seccional do profissional",
  "subsecao": "Subseção à qual o profissional faz parte",
  "categoria": "Categoria (ADVOGADO, ADVOGADA, ESTAGIARIO, etc.)",
  "telefone_profissional": "Telefone profissional",
  "situacao": "Situação do profissional"
}

Regras:
1. Utilize a ferramenta 'search_pdf' para encontrar trechos relevantes, quando necessário.
2. Se algum campo não existir no texto, retorne null.
3. Retorne **apenas o JSON final**, sem explicações adicionais.
"""

# ==========================================================
# CRIAÇÃO DO AGENTE
# ==========================================================
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt
)

# ==========================================================
# MEMÓRIA DE CONTEXTO
# ==========================================================
memory = {}

# ==========================================================
# ROTA PRINCIPAL
# ==========================================================
@app.route("/")
def home():
    return send_from_directory("../frontend", "index.html")

# ==========================================================
# ROTA DE UPLOAD PARA INDEXAÇÃO
# ==========================================================
@app.post("/upload")
def upload_pdf():
    file = request.files["file"]
    filename = file.filename

    save_path = os.path.join("uploads", filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(save_path)

    result = ingest_faiss(save_path)

    return jsonify({
        "status": "ok",
        "message": f"Arquivo '{filename}' indexado com sucesso!",
        "faiss_result": result
    })

# ==========================================================
# ROTA DE EXTRAÇÃO (AUTÔNOMA)
# ==========================================================
@app.post("/extract")
def extract():
    start = time.time()
    data = request.json

    label = data.get("label", "documento_desconhecido")
    extraction_schema = data.get("extraction_schema", {})
    pdf_text = data.get("pdf_text", "")

    query_fields = ", ".join(extraction_schema.keys())

    print(f"\n📄 [REQ EXTRACT] Label: {label}, Campos: {query_fields}")

    # ✅ O agente decide sozinho quando usar FAISS
    user_prompt = f"""
Label: {label}
Campos solicitados: {json.dumps(extraction_schema, ensure_ascii=False, indent=2)}

Texto OCR extraído do PDF:
{pdf_text}

Retorne **somente o JSON** com os campos solicitados.
"""

    # Invocar agente
    result = agent.invoke({"messages": [{"role": "user", "content": user_prompt}]})
    resposta = result["messages"][-1].content.strip()

    # Validar JSON
    try:
        parsed = json.loads(resposta)
    except Exception:
        parsed = {"error": "Falha ao gerar JSON válido", "raw": resposta}

    elapsed = round(time.time() - start, 2)
    print(f"✅ [EXTRACT OK] Tempo total: {elapsed}s")

    return jsonify({
        "label": label,
        "schema_fields": list(extraction_schema.keys()),
        "response": parsed,
        "tempo_execucao": elapsed
    })

# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    app.run(port=5000, debug=True)
