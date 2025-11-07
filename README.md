⚡ Help Desk AI — Extração Inteligente de Dados em Documentos

Desafio Fellowship — Solução entregue por Andre Joas

🧩 Visão Geral

Este projeto implementa um sistema de extração inteligente de informações estruturadas a partir de documentos corporativos (PDFs), utilizando modelos LLM (Llama 3.3 70B) combinados com uma base vetorial FAISS para busca semântica otimizada.

A solução é composta por:
```
🧠 Agente Autônomo de Extração — decide quando e como usar busca semântica FAISS.

⚙️ API REST (/extract) — recebe texto OCR, schema e label, e retorna JSON estruturado.

💾 Pipeline de Ingestão FAISS (/upload) — indexa PDFs e cria embeddings otimizados.

💻 Interface Web Minimalista — permite testar a extração diretamente no navegador.
```

<img width="907" height="409" alt="image" src="https://github.com/user-attachments/assets/802c0b1b-d76c-439b-aaa7-0f9179c48794" />


<img width="929" height="441" alt="image" src="https://github.com/user-attachments/assets/7536a8dd-0496-47db-abd8-24deab3abaa7" />



🔹 Fluxo resumido:
```
Upload de PDFs → /upload

PDFs são convertidos em texto, divididos em chunks e salvos na FAISS.

Extração de dados → /extract

Usuário fornece:

label → tipo de documento (ex: "carteira_oab")

schema → estrutura esperada em JSON

pdf_text → texto OCR extraído

O agente decide quando consultar FAISS e retorna somente o JSON final.
```
INTERFACE
<img width="1035" height="714" alt="image" src="https://github.com/user-attachments/assets/a4b3dfb0-a0cd-4aa9-9052-d477287b70c1" />
<img width="998" height="687" alt="image" src="https://github.com/user-attachments/assets/83722907-25e3-4250-847a-74f76167ace8" />


COMO RODAR (lembre-se de usar uma chave do groq no arquivo .env)

<img width="815" height="764" alt="image" src="https://github.com/user-attachments/assets/2324317b-99d2-4e39-a9b4-335b60c7d452" />

