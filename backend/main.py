from fastapi import FastAPI, UploadFile, File
from ocr import analisar_documento
from chat import chat_with_context
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from draft import prepare_contract_draft, apply_instructions_to_draft
from pydantic import BaseModel
from typing import Literal, Any, Dict, List, Optional
from gerar_contrato import gerar_contrato_docx_bytes
from fastapi.responses import Response
from fastapi import HTTPException
import time
import asyncio
from edit_draft import edit_contract_draft, detect_edit_instruction

load_dotenv(override=True)
api_key_check = os.getenv("AI_API_KEY")
if api_key_check:
    print(f"🔑 [DEBUG] Chave de IA carregada: {api_key_check[:5]}...{api_key_check[-4:]}")
else:
    print("⚠️ [DEBUG] Falha ao carregar AI_API_KEY do .env!")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContractGeneratePayload(BaseModel):
    template: Literal["compra-venda", "financiamento-go", "financiamento-ms"]
    draft: Dict[str, Any]
    extra_text: str | None = None

class DraftPayload(BaseModel):
    documents: Dict[str, Any]
    pending_instructions: List[Dict[str, Any]] = []

# ✅ NOVO ENDPOINT: Detecta se mensagem é instrução de edição
@app.post("/api/detect-edit")
async def detect_edit_endpoint(payload: dict):
    message = payload.get("message")
    documents = payload.get("documents", {})
    
    if not message:
        return {"is_edit_instruction": False}
    
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail="Chave de IA não configurada. Verifique o arquivo .env no backend."
        )

    start_time = time.time()
    try:
        print(f"🔍 [DETECT-EDIT] Iniciando detecção para mensagem: '{message[:50]}...'")
        result = await asyncio.to_thread(detect_edit_instruction, message, documents)
        duration = time.time() - start_time
        print(f"✅ [DETECT-EDIT] Concluído em {duration:.2f}s")
        return result
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ [DETECT-EDIT] Erro após {duration:.2f}s: {e}")
        if "quota" in str(e).lower():
            raise HTTPException(status_code=429, detail="Limite de uso da IA atingido. Tente novamente em um minuto.")
        return {"is_edit_instruction": False, "error": str(e)}

@app.post("/api/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail="Chave de IA não configurada. Verifique o arquivo .env no backend."
        )

    start_time = time.time()
    try:
        print(f"📄 [OCR] Recebido arquivo: {file.filename}")
        result = await asyncio.to_thread(analisar_documento, file)
        duration = time.time() - start_time
        print(f"✅ [OCR] Processamento concluído em {duration:.2f}s")
        
        if not result or not result.get("data"):
            raise HTTPException(status_code=422, detail="Não consegui extrair dados deste arquivo. Ele parece estar ilegível ou vazio.")
        
        return {
            "filename": file.filename,
            "text": result["text"],
            "data": result["data"],
            "processing_time": f"{duration:.2f}s"
        }
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ [OCR] Erro após {duration:.2f}s: {e}")
        if "quota" in str(e).lower() or "resourceexhausted" in str(e).lower():
            raise HTTPException(status_code=429, detail="Nossa cota de uso da IA atingiu o limite momentâneo. Aguarde um minuto e tente de novo.")
        raise HTTPException(status_code=500, detail=f"Erro ao processar documento: {str(e)}")

@app.post("/api/chat")
async def chat_endpoint(payload: dict):
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400, 
            detail="Chave de IA não configurada. Verifique o arquivo .env no backend."
        )

    start_time = time.time()
    try:
        print(f"💬 [CHAT] Processando mensagem do usuário...")
        response = await asyncio.to_thread(
            chat_with_context,
            api_key=api_key,
            model_name=payload.get("model", "gemini-2.5-pro"), # Mantendo o nome original se desejar, mas atente à versão
            chat_history=payload.get("history", []),
            extracted_documents=payload.get("documents", {}),
            user_message=payload["message"],
        )
        duration = time.time() - start_time
        print(f"✅ [CHAT] Resposta gerada em {duration:.2f}s")
        return {"response": response}
    except Exception as e:
        if "quota" in str(e).lower() or "resourceexhausted" in str(e).lower():
            raise HTTPException(status_code=429, detail="Nossa cota de uso da IA atingiu o limite momentâneo. Aguarde um minuto e tente de novo.")
        raise HTTPException(status_code=500, detail="Tive um pequeno tropeço ao processar sua dúvida. Pode tentar perguntar de novo com outras palavras?")

@app.post("/api/draft")
async def contract_draft_endpoint(payload: dict):
    documents = payload.get("documents")
    pending_instructions = payload.get("pending_instructions", [])
    
    print(f"\n📥 Recebido em /api/draft:")
    print(f"   - Documentos: {len(documents)} arquivo(s)")
    print(f"   - Instruções pendentes: {len(pending_instructions)}")
    
    if pending_instructions:
        print(f"\n📋 Instruções recebidas:")
        for i, inst in enumerate(pending_instructions):
            print(f"   {i+1}. {inst}")

    if not documents:
        return {"error": "Nenhum documento fornecido"}

    # Gera o draft base
    print("\n🔨 Gerando draft base...")
    draft = prepare_contract_draft(documents)
    
    # Converte para dict se necessário
    if hasattr(draft, 'model_dump'):
        draft = draft.model_dump()
    
    print(f"\n📄 Draft base gerado:")
    print(draft)
    
    # Aplica instruções pendentes
    if pending_instructions:
        print(f"\n🔧 Aplicando {len(pending_instructions)} instruções...")
        draft = apply_instructions_to_draft(draft, pending_instructions)
    
    return draft

@app.post("/api/contract/generate")
async def contract_generate(payload: ContractGeneratePayload):
    gemini_key = os.getenv("AI_API_KEY")
    if not gemini_key:
        return Response("AI_API_KEY não definida no .env", status_code=500)

    docx_bytes = gerar_contrato_docx_bytes(
        draft=payload.draft,
        template_key=payload.template,
        api_key=gemini_key,
        model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
        extra_text=payload.extra_text or "",
    )

    filename = f"contrato_{payload.template}.docx"
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@app.post("/api/edit")
async def edit_draft(payload: dict):
    draft = payload.get("draft")
    message = payload.get("message")

    if not draft or not message:
        raise HTTPException(status_code=400, detail="draft e message são obrigatórios")

    try:
        instruction = edit_contract_draft(draft, message)
        return {"instruction": instruction.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))