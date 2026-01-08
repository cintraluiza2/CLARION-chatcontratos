import os
import uuid
from google import genai
from docx import Document
from dotenv import load_dotenv
from schemas import DocumentoUnificado  # Certifique-se que o schema atualizado está aqui

load_dotenv()

def ler_docx(file_obj):
    doc = Document(file_obj)
    texto = []
    for para in doc.paragraphs:
        if para.text.strip(): texto.append(para.text)
    for table in doc.tables:
        for row in table.rows:
            linha = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if linha: texto.append(f"[Tabela]: {linha}")
    return "\n".join(texto)

def analisar_documento(uploaded_file, model_name="gemini-2.0-flash"):
    api_key = os.getenv("AI_API_KEY")
    client = genai.Client(api_key=api_key)

    filename = uploaded_file.filename
    ext = os.path.splitext(filename)[1].lower()
    conteudo_envio = []

    if ext == ".docx":
        texto = ler_docx(uploaded_file.file)
        conteudo_envio = [texto]
    else:
        temp_name = f"temp_{uuid.uuid4().hex}{ext}"
        try:
            with open(temp_name, "wb") as f:
                f.write(uploaded_file.file.read())
            file_ref = client.files.upload(file=temp_name, config={"display_name": filename})
            conteudo_envio = [file_ref]
        finally:
            if os.path.exists(temp_name): os.remove(temp_name)

    # PROMPT COM LIMITAÇÃO PARA NÃO ESTOURAR O JSON
    conteudo_envio.append("""
    Analise este arquivo integralmente. Identifique cada documento individual.
    
    IMPORTANTE PARA O CRONOGRAMA FINANCEIRO:
    O arquivo contém centenas de parcelas. Para evitar erros de limite de texto:
    1. Extraia os dados das primeiras 20 parcelas.
    2. Extraia os dados das últimas 10 parcelas.
    3. No resumo_conteudo, mencione o total de parcelas encontradas (ex: 360 parcelas).
    
    Para cada documento, preencha o schema DocumentoUnificado.
    Retorne uma LISTA de objetos JSON.
    """)

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=conteudo_envio,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[DocumentoUnificado],
            }
        )

        lista_documentos = response.parsed

        # 🔹 TRATAMENTO DO ERRO QUE VOCÊ ESTÁ TENDO
        if lista_documentos is None:
            # Tenta recuperar o texto bruto se o parse falhou
            return {
                "text": "Erro: O modelo não conseguiu estruturar os dados. O documento pode ser muito complexo ou longo.",
                "data": []
            }

        resumo_geral = []
        for i, doc in enumerate(lista_documentos, 1):
            bloco = (
                f"--- DOCUMENTO {i} ---\n"
                f"Tipo: {doc.tipo_documento}\n"
                f"Resumo: {doc.resumo_conteudo}\n"
                f"Parcelas extraídas: {len(doc.cronograma_financeiro)}\n"
            )
            resumo_geral.append(bloco)

        return {
            "text": "\n".join(resumo_geral).strip(),
            "data": lista_documentos
        }

    except Exception as e:
        print(f"Erro na chamada da API: {e}")
        return {"text": f"Erro técnico: {str(e)}", "data": []}
