from fastapi import FastAPI, UploadFile, File, Form
from ocr import analisar_documento
from chat import chat_with_context
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from draft import prepare_contract_draft
from pydantic import BaseModel
from typing import Literal, Any, Dict
from gerar_contrato import gerar_contrato_docx_bytes
from fastapi.responses import Response


load_dotenv()
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

@app.post("/api/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    result = analisar_documento(file)

    return {
        "filename": file.filename,
        "text": result["text"],
        "data": result["data"],
    }


@app.post("/api/chat")
async def chat_endpoint(payload: dict):
    api_key = os.getenv("AI_API_KEY")

    if not api_key:
        raise RuntimeError("AI_API_KEY não encontrada no ambiente")

    response = chat_with_context(
        api_key=api_key,
        model_name=payload.get("model", "gemini-2.5-flash"),
        chat_history=payload.get("history", []),
        extracted_documents=payload.get("documents", {}),
        user_message=payload["message"],
    )

    return {"response": response}


@app.post("/api/draft")
async def contract_draft_endpoint(payload: dict):
    documents = payload.get("documents")

    if not documents:
        return {"error": "Nenhum documento fornecido"}

    draft = prepare_contract_draft(documents)
    return draft


@app.post("/api/contract/generate")
def contract_generate(payload: ContractGeneratePayload):
    gemini_key = os.getenv("AI_API_KEY")
    if not gemini_key:
        return Response("AI_API_KEY não definida no .env", status_code=500)

    docx_bytes = gerar_contrato_docx_bytes(
        draft=payload.draft,
        template_key=payload.template,
        api_key=gemini_key,
        model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        extra_text=payload.extra_text or "",
    )

    filename = f"contrato_{payload.template}.docx"
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
