from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any
from dotenv import load_dotenv
load_dotenv()

class Parte(BaseModel):
    nome: str
    cpf_cnpj: Optional[str] = None
    rg: Optional[str] = None
    papel: str
    data_nascimento: Optional[str] = None
    filiacao: List[str] = []

class Imovel(BaseModel):
    endereco_completo: str
    matricula: Optional[str] = None
    cidade: str
    area_total: Optional[str] = None
    imobiliaria: str

class DocumentoUnificado(BaseModel):
    tipo_documento: Literal[
        "Matrícula de Imóvel",
        "Contrato de Compra e Venda",
        "Contrato de Locação",
        "RG",
        "CNH",
        "Certidão de Nascimento",
        "Certidão de Casamento",
        "Certidão de Óbito",
        "Certidão de Divórcio",
        "Comprovante de Endereço",
        "Boleto/IPTU",
        "Outro"
    ]
    numero_documento: Optional[str] = None
    data_emissao: Optional[str] = None
    valor_monetario: Optional[float] = None
    partes: List[Parte] = []
    imovel: Optional[Imovel] = None
    resumo_conteudo: str

class ContractDraft(BaseModel):
    partes: List[Parte] = Field(
        ..., description="Partes consolidadas do contrato"
    )

    imovel: Optional[Imovel] = Field(
        None, description="Dados consolidados do imóvel"
    )

    valor_monetario: Optional[float] = Field(
        None, description="Valor total do negócio"
    )

    forma_pagamento: Optional[str] = None


    pendencias: List[str] = Field(
        default_factory=list,
        description="Dados ausentes ou inconsistentes que precisam confirmação"
    )

class UniversalInstruction(BaseModel):
    path: str
    new_value: Any
    description: str
