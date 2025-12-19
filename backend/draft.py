from google import genai
import os
from dotenv import load_dotenv
from schemas import ContractDraft

load_dotenv()

def prepare_contract_draft(documentos: dict):
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        raise RuntimeError("AI_API_KEY não encontrada")

    client = genai.Client(api_key=api_key) 

    prompt = f"""
    A partir dos DOCUMENTOS abaixo (já extraídos),
    consolide os dados necessários para um CONTRATO DE COMPRA E VENDA.

    Regras obrigatórias:
    - Use SOMENTE os dados fornecidos
    - NÃO invente informações
    - Se houver conflito entre documentos, liste em "pendencias"
    - Se faltar dado essencial, liste em "pendencias"
    - Retorne JSON conforme o schema ContractDraft

    Documentos:
    {documentos}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ContractDraft,
        },
    )

    return response.parsed
