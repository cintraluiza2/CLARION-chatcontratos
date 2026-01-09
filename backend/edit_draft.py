# edit_draft.py

from google import genai
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Optional, Any
import json

load_dotenv()

# =========================
# SCHEMA UNIVERSAL DE INSTRUÇÃO
# =========================

class UniversalInstruction(BaseModel):
    """Instrução universal que funciona para QUALQUER campo"""
    path: str  # Ex: "partes[0].nome", "imovel.endereco_completo", "valor_monetario"
    new_value: Any  # Pode ser string, número, lista, objeto, etc
    description: str  # Descrição legível da mudança


# =========================
# DETECTAR INSTRUÇÃO DE EDIÇÃO (UNIVERSAL)
# =========================

def detect_edit_instruction(user_message: str, documents: dict) -> dict:
    """
    Detecta se a mensagem é uma instrução de edição para QUALQUER campo do contrato.
    Funciona ANTES do draft ser criado.
    """
    print(f"\n🔍 Detectando instrução de edição...")
    print(f"   Mensagem: {user_message}")
    
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        raise RuntimeError("AI_API_KEY não encontrada")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Você é um assistente que detecta se o usuário está pedindo para EDITAR informações de um contrato.

Mensagem do usuário: "{user_message}"

Documentos disponíveis (resumo):
{json.dumps(documents, indent=2, ensure_ascii=False)[:1000]}...

ESTRUTURA DO CONTRATO:
{{
  "partes": [
    {{
      "nome": "string",
      "cpf_cnpj": "string",
      "rg": "string",
      "papel": "Vendedor/Comprador/etc",
      "data_nascimento": "string",
      "filiacao": ["pai", "mãe"]
    }}
  ],
  "imovel": {{
    "endereco_completo": "string",
    "matricula": "string",
    "cidade": "string",
    "area_total": "string",
    "inscricao_municipal": "string"
  }},
  "valor_monetario": 123.45,
  "forma_pagamento": "string",
  "documentos_utilizados": ["doc1.pdf"],
  "pendencias": ["string"],
  "observacoes": "string"
}}

EXEMPLOS DE INSTRUÇÕES DE EDIÇÃO:

1. "Muda o nome do primeiro vendedor para João Silva"
   → path: "partes[0].nome"
   → new_value: "João Silva"
   → description: "Alterar nome da primeira parte para João Silva"

2. "Altera o CPF do segundo comprador para 123.456.789-00"
   → path: "partes[1].cpf_cnpj"
   → new_value: "123.456.789-00"
   → description: "Alterar CPF da segunda parte para 123.456.789-00"

3. "Corrige o endereço do imóvel para Rua das Flores, 123"
   → path: "imovel.endereco_completo"
   → new_value: "Rua das Flores, 123"
   → description: "Alterar endereço do imóvel para Rua das Flores, 123"

4. "Atualiza o valor para R$ 500.000"
   → path: "valor_monetario"
   → new_value: 500000.0
   → description: "Alterar valor monetário para R$ 500.000,00"

5. "Muda a matrícula para 12345"
   → path: "imovel.matricula"
   → new_value: "12345"
   → description: "Alterar matrícula do imóvel para 12345"

6. "Define a forma de pagamento como à vista"
   → path: "forma_pagamento"
   → new_value: "À vista"
   → description: "Definir forma de pagamento como à vista"

7. "Adiciona observação: Contrato sujeito a aprovação"
   → path: "observacoes"
   → new_value: "Contrato sujeito a aprovação"
   → description: "Adicionar observação ao contrato"

8. "Troca o papel da primeira pessoa para Vendedor"
   → path: "partes[0].papel"
   → new_value: "Vendedor"
   → description: "Alterar papel da primeira parte para Vendedor"

EXEMPLOS DE MENSAGENS QUE NÃO SÃO INSTRUÇÕES DE EDIÇÃO:
- "Quais são os dados do vendedor?"
- "Me explica o contrato"
- "Obrigado"
- "Quanto está o imóvel?"
- "Quem são as partes?"

REGRAS:
- Se for uma instrução clara de ALTERAR/MUDAR/CORRIGIR/ATUALIZAR/DEFINIR dados, é uma instrução de edição
- Identifique qual campo deve ser alterado e monte o path correto
- Use índices [0], [1], etc para acessar itens de arrays
- new_value deve ter o tipo correto (string, número, etc)
- description deve ser uma frase clara do que será alterado

Se for uma instrução de edição, retorne:
{{
  "is_edit_instruction": true,
  "instruction": {{
    "path": "campo.aninhado[indice].subcampo",
    "new_value": "valor ou número",
    "description": "Descrição clara da alteração"
  }}
}}

Se NÃO for uma instrução de edição, retorne:
{{
  "is_edit_instruction": false
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )

        result = json.loads(response.text)
        
        print(f"\n📊 Resultado da detecção:")
        print(f"   É edição? {result.get('is_edit_instruction')}")
        if result.get('instruction'):
            print(f"   Path: {result['instruction'].get('path')}")
            print(f"   Novo valor: {result['instruction'].get('new_value')}")
            print(f"   Descrição: {result['instruction'].get('description')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro ao detectar instrução: {e}")
        import traceback
        traceback.print_exc()
        return {"is_edit_instruction": False, "error": str(e)}


# =========================
# EDITAR DRAFT EXISTENTE (UNIVERSAL)
# =========================

def edit_contract_draft(draft: dict, user_message: str) -> UniversalInstruction:
    """
    Edita um draft JÁ EXISTENTE baseado na mensagem do usuário.
    Funciona para QUALQUER campo do contrato.
    """
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        raise RuntimeError("AI_API_KEY não encontrada")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Você está editando um RASCUNHO DE CONTRATO já consolidado.

Draft atual (JSON):
{json.dumps(draft, indent=2, ensure_ascii=False)}

Instrução do usuário:
"{user_message}"

REGRAS:
- Identifique QUAL campo o usuário quer alterar
- Monte o path correto (ex: "partes[0].nome", "imovel.endereco_completo")
- Extraia o novo valor que o usuário quer definir
- Crie uma descrição clara da alteração

Retorne APENAS o JSON da instrução, sem explicações.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": UniversalInstruction,
        },
    )

    return response.parsed
