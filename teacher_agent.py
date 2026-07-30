import asyncio
import os
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
import re
from prompt_manager import PromptManager
from mock_database import MockDatabase

class TeacherAgentAPI:
    def __init__(self, api_key: str = None, base_url: str = None):
        load_dotenv()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")
        self.prompt_manager = PromptManager()
        
        if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY_HERE":
            print("[Uyarı] GEMINI_API_KEY ayarlanmamış. Lütfen .env dosyasına key'inizi girin.")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        
    async def call_model(self, prompt: str, **kwargs) -> str:
        """
        Simulates an asynchronous API call to an advanced reasoning model.
        """
        print(f"[TeacherAgentAPI] {self.model_name} modeline API isteği gönderiliyor...")
        
        if not hasattr(self, 'model'):
            return "Hata: Model yapılandırılamadı. Lütfen .env dosyasında geçerli bir API anahtarı sağladığınızdan emin olun."
            
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            return f"API Hatası: {str(e)}"

    async def evaluate_student_output(self, student_output: str, contrastive_evidence_list: list) -> Dict[str, Any]:
        """
        Specific method to evaluate student output using contrastive reflection.
        """
        prompt = self.prompt_manager.generate_contrastive_reflection_prompt(
            student_output=student_output,
            contrastive_evidence_list=contrastive_evidence_list
        )
        
        response = await self.call_model(prompt)
        
        
        # Extract the specific rule/prompt update
        prompt_update = self.extract_prompt_update(response)
        
        # Simulated parsed response
        return {
            "status": "success",
            "evaluation_result": response,
            "extracted_rule": prompt_update,
            "generated_prompt": prompt
        }
        
    def extract_prompt_update(self, evaluation_text: str) -> str:
        """
        Parses the LLM output to extract just the recommended prompt update (the new rule).
        """
        # Look for the "Önerilen Prompt Güncellemesi:" section
        match = re.search(r"Önerilen Prompt Güncellemesi:\s*(.*)", evaluation_text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return "No specific rule extracted."

async def main():
    agent = TeacherAgentAPI()
    db = MockDatabase()
    
    print("--- 2. Hafta Entegrasyon Testi Başlıyor ---")
    
    records = await db.get_unprocessed_evaluations()
    if not records:
        print("İşlenecek kayıt bulunamadı.")
        return
        
    for record in records:
        print(f"\nİncelenen Dosya: {record['file_id']} (Log ID: {record['log_id'][:8]}...)")
        
        result = await agent.evaluate_student_output(
            student_output=record["student_output"],
            contrastive_evidence_list=record["contrastive_evidence"]
        )
        
        print(f" LLM Ham Değerlendirmesi:\n  {result['evaluation_result'].replace(chr(10), chr(10)+'  ')}")
        
        rule = result.get('extracted_rule')
        if rule and rule != "No specific rule extracted.":
            print(f"\n [BAŞARILI] Çıkarılan Yeni Kural (Prompt Update):\n  >>> {rule}")
            await db.update_evaluation_status(record['log_id'], "processed", teacher_feedback=rule)
        else:
            print("\n [BAŞARISIZ] Kural çıkarılamadı.")
            await db.update_evaluation_status(record['log_id'], "failed_to_extract_rule")

if __name__ == "__main__":
    asyncio.run(main())
