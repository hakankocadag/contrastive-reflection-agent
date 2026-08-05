import ast
import json
import uuid
from typing import List
from pydantic import BaseModel, Field

# ==========================================
# 2. SABİTLENMİŞ VERİ ŞEMALARI (Anayasa)
# ==========================================
class FunctionCall(BaseModel):
    caller: str = Field(description="Çağrıyı yapan fonksiyonun adı (örn: main)")
    callee: str = Field(description="Çağrılan fonksiyonun adı (örn: calculate_loss)")
    line_number: int = Field(description="Çağrının yapıldığı satır numarası")

class ArchitectureError(BaseModel):
    error_type: str = Field(description="Hatanın tipi (örn: CircularDependency, UndefinedCall)")
    target_node: str = Field(description="Hatanın gerçekleştiği AST düğümü veya fonksiyon adı")
    line_number: int = Field(description="Hatanın tespit edildiği satır numarası")

class GroundTruthSchema(BaseModel):
    file_id: str = Field(description="Analiz edilen sentetik dosyanın benzersiz ID'si")
    detected_calls: List[FunctionCall] = Field(default_factory=list)
    reported_errors: List[ArchitectureError] = Field(default_factory=list)

class StudentAgentOutput(BaseModel):
    detected_calls: List[FunctionCall] = Field(default_factory=list)
    reported_errors: List[ArchitectureError] = Field(default_factory=list)

class EvaluationLog(BaseModel):
    log_id: str = Field(description="Bu analiz döngüsünün benzersiz ID'si (UUID)")
    file_id: str = Field(description="Analiz edilen dosyanın ID'si")
    prompt_version: str = Field(description="Öğrenci ajanı çalıştıran promptun versiyonu")
    status: str = Field(description="'Başarılı' veya 'Halüsinasyon' etiketi")
    student_output: StudentAgentOutput = Field(description="Ajanın ürettiği iddialar")
    ground_truth: GroundTruthSchema = Field(description="Gerçek (Deterministik) referans tablosu")

# ==========================================
# HAFTA 1: Temellerin Atılması ve Sahaya İniş
# ==========================================
class ASTParser(ast.NodeVisitor):
    def __init__(self):
        self.calls: List[FunctionCall] = []
        self.current_function = "global"

    def visit_FunctionDef(self, node):
        prev_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = prev_function

    def visit_Call(self, node):
        # Determine the name of the called function
        callee_name = "unknown"
        if isinstance(node.func, ast.Name):
            callee_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            callee_name = node.func.attr
            
        self.calls.append(FunctionCall(
            caller=self.current_function,
            callee=callee_name,
            line_number=node.lineno
        ))
        self.generic_visit(node)

def generate_ground_truth(synthetic_code: str, file_id: str) -> GroundTruthSchema:
    """Parses Python code and generates a deterministic graph.json compliant GroundTruthSchema."""
    tree = ast.parse(synthetic_code)
    parser = ASTParser()
    parser.visit(tree)
    
    # Hardcoded error injection for the synthetic file simulation
    simulated_errors = [
        ArchitectureError(error_type="UndefinedCall", target_node="non_existent_func", line_number=12)
    ]
    
    ground_truth = GroundTruthSchema(
        file_id=file_id,
        detected_calls=parser.calls,
        reported_errors=simulated_errors
    )
    
    # Save to graph.json
    with open(f"{file_id}_graph.json", "w", encoding="utf-8") as f:
        f.write(ground_truth.model_dump_json(indent=4))
        
    return ground_truth

# ==========================================
# HAFTA 2: Otonom Denetim ve Zekanın Bütünleşmesi
# ==========================================
def evaluate_student_output(student_output: StudentAgentOutput, ground_truth: GroundTruthSchema, prompt_version: str) -> EvaluationLog:
    """Compares Student Agent output with Ground Truth using Exact Match and returns a Log."""
    
    # AST Normalization (Sorting lists for exact deterministic matching)
    def normalize_calls(calls: List[FunctionCall]):
        return sorted([c.model_dump() for c in calls], key=lambda x: (x['caller'], x['callee'], x['line_number']))
        
    def normalize_errors(errors: List[ArchitectureError]):
        return sorted([e.model_dump() for e in errors], key=lambda x: (x['error_type'], x['target_node'], x['line_number']))

    gt_calls_norm = normalize_calls(ground_truth.detected_calls)
    st_calls_norm = normalize_calls(student_output.detected_calls)
    
    gt_errors_norm = normalize_errors(ground_truth.reported_errors)
    st_errors_norm = normalize_errors(student_output.reported_errors)
    
    # Exact Match Logic
    is_successful = (gt_calls_norm == st_calls_norm) and (gt_errors_norm == st_errors_norm)
    status = "Başarılı" if is_successful else "Halüsinasyon"
    
    return EvaluationLog(
        log_id=str(uuid.uuid4()),
        file_id=ground_truth.file_id,
        prompt_version=prompt_version,
        status=status,
        student_output=student_output,
        ground_truth=ground_truth
    )

# ==========================================
# HAFTA 3: Doğrulama, Uçtan Uca Test ve Sahiplenme
# ==========================================
def autonomous_validation_flow(old_logs: List[EvaluationLog], new_logs: List[EvaluationLog]) -> bool:
    """Tests if the new rule (prompt) increases success. Returns True to commit, False to reject."""
    
    def calc_success_rate(logs: List[EvaluationLog]) -> float:
        if not logs: return 0.0
        successes = sum(1 for log in logs if log.status == "Başarılı")
        return successes / len(logs)
        
    old_rate = calc_success_rate(old_logs)
    new_rate = calc_success_rate(new_logs)
    
    print(f"[Doğrulama] Eski Prompt Başarısı: %{old_rate * 100:.1f}")
    print(f"[Doğrulama] Yeni Prompt Başarısı: %{new_rate * 100:.1f}")
    
    if new_rate > old_rate:
        print("[KARAR] Başarı arttı. Yeni kural kalıcı yapılıyor (Commit).")
        return True
    else:
        print("[KARAR] Başarı artmadı veya düştü. Yeni kural reddedildi, eski prompt korunuyor (Rollback).")
        return False

# ==========================================
# Geliştirme Ortamı Testi (Pipeline Run)
# ==========================================
if __name__ == "__main__":
    # 1. Sentetik Kod (Hafta 1)
    synthetic_code_sample = """
def authenticate_user():
    db_connect()
    
def main():
    authenticate_user()
    non_existent_func() # Intentionally causes UndefinedCall
"""
    
    print("--- HAFTA 1: Ground Truth Üretimi ---")
    file_id = "test_script_001"
    gt = generate_ground_truth(synthetic_code_sample, file_id)
    print(f"{file_id}_graph.json oluşturuldu.\n")

    print("--- HAFTA 2: Öğrenci Ajan Değerlendirmesi ---")
    # Simulate a Hallucinating Student Output (Missed the error)
    bad_student_output = StudentAgentOutput(
        detected_calls=[
            FunctionCall(caller="authenticate_user", callee="db_connect", line_number=3),
            FunctionCall(caller="main", callee="authenticate_user", line_number=6),
            FunctionCall(caller="main", callee="non_existent_func", line_number=7)
        ],
        reported_errors=[] # Failed to report the architecture error
    )
    
    # Simulate a Successful Student Output (Matched exactly)
    good_student_output = StudentAgentOutput(
        detected_calls=gt.detected_calls,
        reported_errors=gt.reported_errors
    )
    
    log_v1 = evaluate_student_output(bad_student_output, gt, prompt_version="v1.0")
    print(f"v1.0 Değerlendirme Sonucu: {log_v1.status}")
    
    log_v2 = evaluate_student_output(good_student_output, gt, prompt_version="v1.1")
    print(f"v1.1 Değerlendirme Sonucu: {log_v2.status}\n")

    print("--- HAFTA 3: Otonom Doğrulama Akışı ---")
    # Simulate the validation flow with dummy historical data
    old_evaluation_logs = [log_v1, log_v1, log_v1] # 0% success
    new_evaluation_logs = [log_v2, log_v2, log_v1] # 66.6% success
    
    autonomous_validation_flow(old_evaluation_logs, new_evaluation_logs)