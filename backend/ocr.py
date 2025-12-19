import os
import uuid
from google import genai
from docx import Document
from dotenv import load_dotenv
from schemas import DocumentoUnificado  # mesmo schema do Streamlit

load_dotenv()

def ler_docx(file_obj):
    doc = Document(file_obj)
    texto = []

    for para in doc.paragraphs:
        if para.text.strip():
            texto.append(para.text)

    for table in doc.tables:
        for row in table.rows:
            linha = " | ".join(cell.text for cell in row.cells if cell.text.strip())
            if linha:
                texto.append(f"[Tabela]: {linha}")

    return "\n".join(texto)


def analisar_documento(uploaded_file, model_name="gemini-2.5-flash"):
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        raise RuntimeError("AI_API_KEY não configurada")

    client = genai.Client(api_key=api_key)

    filename = uploaded_file.filename
    ext = os.path.splitext(filename)[1].lower()

    conteudo_envio = []

    if ext == ".docx":
        texto = ler_docx(uploaded_file.file)
        conteudo_envio = [texto, "Analise o texto completo deste documento."]
    else:
        temp_name = f"temp_{uuid.uuid4().hex}{ext}"
        with open(temp_name, "wb") as f:
            f.write(uploaded_file.file.read())

        try:
            file_ref = client.files.upload(
                file=temp_name,
                config={"display_name": filename}
            )
            conteudo_envio = [file_ref, "Analise este documento visualmente."]
        finally:
            if os.path.exists(temp_name):
                os.remove(temp_name)

    conteudo_envio.append("""
    Analise cuidadosamente este documento.
    Identifique o TIPO de documento.
    Extraia partes, CPFs, RGs, papéis.
    Extraia dados do imóvel se houver.
    Retorne JSON conforme o schema.
    """)

    response = client.models.generate_content(
    model=model_name,
    contents=conteudo_envio,
    config={
        "response_mime_type": "application/json",
        "response_schema": DocumentoUnificado,
    }
)

    # 🔹 TEXTO EM LINGUAGEM NATURAL
    texto_humano = f"""
    Tipo de documento: {response.parsed.tipo_documento}

    Resumo:
    {response.parsed.resumo_conteudo}

    """

    return {
        "text": texto_humano.strip(),
        "data": response.parsed
    }
