from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any

class Parte(BaseModel):
    nome: str
    cpf_cnpj: Optional[str] = None
    rg: Optional[str] = None
    papel: str
    data_nascimento: Optional[str] = None
    filiacao: List[str] = []
    estado_civil: str
    profissao: str
    endereco: str

class Imovel(BaseModel):
    endereco_completo: str
    matricula: Optional[str] = None
    cidade: str
    area_total: Optional[str] = None
    imobiliaria: str

class Parcela(BaseModel):
    tipo: str = Field(description="Tipo da parcela: E (Entrada), P (Parcela Mensal), B (Balão/Intermediária)")
    indice: str = Field(description="Número da parcela, ex: 1/360")
    vencimento: str
    valor: float
    status: Optional[str] = Field(None, description="Ex: Pago, Aberto, Vencido")

class DocumentoUnificado(BaseModel):
    tipo_documento: Literal[
        "Matrícula de Imóvel",
        "Contrato de Compra e Venda",
        "Contrato de Locação",
        "Extrato Financeiro / Demonstrativo de Pagamento", 
        "RG", "CNH", "Certidão de Nascimento", "Certidão de Casamento",
        "Certidão de Óbito", "Certidão de Divórcio", "Comprovante de Endereço",
        "Boleto/IPTU", "Outro"
    ]
    numero_documento: Optional[str] = None
    data_emissao: Optional[str] = None
    valor_monetario: Optional[float] = None
    partes: List[Parte] = []
    imovel: Optional[Imovel] = None
    cronograma_financeiro: List[Parcela] = Field(default_factory=list, description="Lista de parcelas detalhadas encontradas")
    resumo_conteudo: str

class ContractDraft(BaseModel):
    partes: List[Parte] = Field(..., description="Partes consolidadas do contrato")
    imovel: Optional[Imovel] = Field(None, description="Dados consolidados do imóvel")
    valor_monetario: Optional[float] = Field(None, description="Valor total do negócio")
    forma_pagamento: Optional[str] = None
    cronograma_financeiro: List[Parcela] = [] 
    pendencias: List[str] = Field(default_factory=list, description="Dados ausentes ou inconsistentes")
