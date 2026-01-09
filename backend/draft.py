# draft.py

from google import genai
import os
from dotenv import load_dotenv
from schemas import ContractDraft
import copy
import re
from typing import List

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


def apply_instructions_to_draft(draft: dict, instructions: List[dict]) -> dict:
    """
    Aplica uma lista de instruções ao draft.
    """
    print(f"\n🔧 Aplicando {len(instructions)} instruções ao draft...")
    
    result = draft if isinstance(draft, dict) else draft.model_dump()
    
    for i, instruction in enumerate(instructions):
        print(f"\n📝 Instrução {i+1}:")
        print(f"   Path: {instruction.get('path')}")
        print(f"   New Value: {instruction.get('new_value')}")
        
        path = instruction.get("path", "")
        new_value = instruction.get("new_value")
        
        if not path or new_value is None:
            print(f"   ⚠️ Instrução inválida, pulando...")
            continue
        
        # Usa a mesma lógica de setByPath do frontend
        result = set_by_path_python(result, path, new_value)
        print(f"   ✅ Aplicada com sucesso")
    
    print(f"\n✨ Draft final após aplicar instruções:")
    print(result)
    
    return result


def set_by_path_python(obj: dict, path: str, value: any) -> dict:
    """
    Implementação Python do setByPath do frontend.
    Exemplos de paths:
    - "partes[0].nome"
    - "partes.vendedores[0].cpf"
    - "imovel.endereco.logradouro"
    """
    print(f"      🔍 Aplicando path: {path}")
    
    # Parse do path
    parts = []
    for chunk in path.split("."):
        # Match "partes[0]" ou apenas "partes"
        matches = re.findall(r'([^\[\]]+)|\[(\d+)\]', chunk)
        for match in matches:
            if match[0]:  # Nome do campo
                parts.append(match[0])
            elif match[1]:  # Índice de array
                parts.append(int(match[1]))
    
    print(f"      🔍 Parts extraídas: {parts}")
    
    result = copy.deepcopy(obj)
    current = result
    
    # Navega até o penúltimo elemento
    for i, key in enumerate(parts[:-1]):
        print(f"      🔍 Navegando: {key} (tipo: {type(key)})")
        
        if isinstance(key, int):
            # É um índice de array
            if not isinstance(current, list):
                print(f"      ⚠️ Esperava lista, encontrou {type(current)}")
                return result
            
            # Expande array se necessário
            while len(current) <= key:
                current.append({})
            
            if current[key] is None:
                next_key = parts[i + 1]
                current[key] = [] if isinstance(next_key, int) else {}
            
            current = current[key]
        else:
            # É uma chave de dicionário
            if key not in current:
                next_key = parts[i + 1] if i + 1 < len(parts) else None
                current[key] = [] if isinstance(next_key, int) else {}
            
            current = current[key]
    
    # Aplica o valor final
    last_key = parts[-1]
    print(f"      🔍 Aplicando valor final na chave: {last_key}")
    
    if isinstance(last_key, int) and isinstance(current, list):
        while len(current) <= last_key:
            current.append(None)
        current[last_key] = value
    else:
        current[last_key] = value
    
    print(f"      ✅ Valor aplicado: {value}")
    
    return result
