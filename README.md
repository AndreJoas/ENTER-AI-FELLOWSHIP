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



<img width="929" height="441" alt="image" src="https://github.com/user-attachments/assets/7536a8dd-0496-47db-abd8-24deab3abaa7" />

