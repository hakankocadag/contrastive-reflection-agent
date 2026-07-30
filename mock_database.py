import json
import uuid
from typing import List, Dict, Any

class MockDatabase:
    """
    Simulates the SQLite database that will be implemented by Hossein in Week 1.
    Provides mock data for the Teacher Agent to process in Week 2.
    """
    def __init__(self):
        self.evaluations = [
            {
                "log_id": str(uuid.uuid4()),
                "file_id": "synthetic_file_001.py",
                "student_output": json.dumps({
                    "detected_calls": [
                        {"caller": "main", "callee": "calculate_loss", "line_number": 10},
                        {"caller": "main", "callee": "non_existent_function", "line_number": 15}
                    ]
                }),
                "contrastive_evidence": [
                    "Gerçek 'graph.json' dosyasında 'non_existent_function' adında bir fonksiyon çağrısı bulunmamaktadır.",
                    "'main' fonksiyonu sadece 'calculate_loss' fonksiyonunu çağırmalıdır."
                ],
                "status": "pending_teacher_review"
            },
            {
                "log_id": str(uuid.uuid4()),
                "file_id": "synthetic_file_002.py",
                "student_output": json.dumps({
                    "detected_calls": [
                        {"caller": "app_run", "callee": "init_db", "line_number": 5}
                    ]
                }),
                "contrastive_evidence": [
                    "Gerçek referans dosyasına göre 'app_run' fonksiyonu 'init_db' fonksiyonundan önce 'load_config' fonksiyonunu çağırmalıdır. Ancak Öğrenci Ajan 'load_config' çağrısını raporlamamıştır."
                ],
                "status": "pending_teacher_review"
            }
        ]

    async def get_unprocessed_evaluations(self) -> List[Dict[str, Any]]:
        """
        Fetches records that have not been processed by the Teacher Agent yet.
        """
        # In a real db, you'd run something like: 
        # SELECT * FROM EvaluationLog WHERE status = 'pending_teacher_review'
        return [record for record in self.evaluations if record["status"] == "pending_teacher_review"]
    
    async def update_evaluation_status(self, log_id: str, new_status: str, teacher_feedback: str = None):
        """
        Updates the status of an evaluation log after Teacher Agent processing.
        """
        for record in self.evaluations:
            if record["log_id"] == log_id:
                record["status"] = new_status
                if teacher_feedback:
                    record["teacher_feedback"] = teacher_feedback
                print(f"[MockDatabase] Kayıt {log_id[:8]}... güncellendi: {new_status}")
                return True
        return False
