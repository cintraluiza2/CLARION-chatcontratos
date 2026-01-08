from google import genai
from dotenv import load_dotenv
import json
import re

load_dotenv()


def chat_with_context(
    api_key: str,
    model_name: str,
    chat_history: list,
    extracted_documents: dict,
    user_message: str,
):
    client = genai.Client(api_key=api_key)

    contexto_docs = ""
    if extracted_documents:
        contexto_docs += "<documentos>\n"
        for nome, dados in extracted_documents.items():
            contexto_docs += f"<doc nome='{nome}'>\n{dados}\n</doc>\n"
        contexto_docs += "</documentos>"

    system_prompt = f"""
Você é um assistente jurídico sênior altamente preciso e amigável.

REGRAS OBRIGATÓRIAS:
1. Sempre responda em JSON válido seguindo estritamente o formato abaixo.
2. Se o usuário pedir alteração de dado:
   - Nunca gere paths técnicos (ex: partes[0].nome).
   - Nunca use índices.
   - Se a alteração envolver pessoas e houver mais de uma pessoa com o mesmo nome ou o nome estiver incompleto, peça esclarecimento amigavelmente: "Identifiquei mais de uma pessoa com este nome. A qual delas você se refere?"
   - Se a instrução for clara para uma única pessoa ou campo, use o nome completo como alvo.
3. Se não houver alteração ou a instrução for apenas uma dúvida, use: "instruction": null.

FORMATO OBRIGATÓRIO:
{{
  "response": "texto em linguagem natural (explicação ou resposta direta)",
  "instruction": {{
    "action": "rename_party | update_imovel | update_valor | none",
    "target": "descrição do alvo (ex: nome completo da pessoa)",
    "field": "campo a ser alterado (se aplicável)",
    "value": "novo valor"
  }}
}}

Contexto dos documentos:
{contexto_docs}
"""

    history = [
        {
            "role": "user",
            "parts": [
                {
                    "text": f"{system_prompt}\nMensagem do usuário:\n{user_message}"
                }
            ],
        }
    ]

    response = client.models.generate_content(
        model=model_name,
        contents=history,
    )

    raw_text = response.text.strip()

    # =========================
    # LIMPEZA DE MARKDOWN
    # =========================
    raw_text = re.sub(r"^```json", "", raw_text)
    raw_text = re.sub(r"```$", "", raw_text)
    raw_text = raw_text.strip()

    # =========================
    # PARSE JSON
    # =========================
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        parsed = {
            "response": raw_text,
            "updates": []
        }

    return {
    "response": parsed.get("response", ""),
    "instruction": parsed.get("instruction"),
}

