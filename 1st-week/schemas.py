"""
SABITLENMIS VERI SEMALARI
Bu semalar sistemin anayasasidir ve hicbir gelistirici tarafindan
tek tarafli degistirilemez. (Proje dokumanindan birebir alinmistir.)
"""
from pydantic import BaseModel, Field
from typing import List


# --- CEKIRDEK VERI YAPILARI ---

class FunctionCall(BaseModel):
    caller: str = Field(description="Cagriyi yapan fonksiyonun adi (orn: main)")
    callee: str = Field(description="Cagrilan fonksiyonun adi (orn: calculate_loss)")
    line_number: int = Field(description="Cagrinin yapildigi satir numarasi")


class ArchitectureError(BaseModel):
    error_type: str = Field(
        description="Hatanin tipi (orn: CircularDependency, UndefinedCall)"
    )
    target_node: str = Field(
        description="Hatanin gerceklestigi AST dugumu / fonksiyon adi"
    )
    line_number: int = Field(description="Hatanin tespit edildigi satir numarasi")


# --- 1. GROUND TRUTH (graph.json) SEMASI (Ali Mojarrad uretir) ---

class GroundTruthSchema(BaseModel):
    file_id: str = Field(description="Analiz edilen sentetik dosyanin benzersiz ID'si")
    detected_calls: List[FunctionCall] = Field(default_factory=list)
    reported_errors: List[ArchitectureError] = Field(default_factory=list)
