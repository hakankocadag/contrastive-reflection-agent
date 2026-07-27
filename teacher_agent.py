import asyncio
import os
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from prompt_manager import PromptManager

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
        
        # Simulated parsed response
        return {
            "status": "success",
            "evaluation_result": response,
            "generated_prompt": prompt
        }

async def main():
    agent = TeacherAgentAPI()
    
    # Mock data to test the integration
    import json
    mock_student_output = json.dumps({
        "detected_calls": [
            {"caller": "main", "callee": "calculate_loss", "line_number": 10},
            {"caller": "main", "callee": "non_existent_function", "line_number": 15}
        ]
    }, indent=2)
    
    mock_contrastive_evidence = [
        "Gerçek 'graph.json' dosyasında 'non_existent_function' adında bir fonksiyon çağrısı bulunmamaktadır.",
        "'main' fonksiyonu sadece 'calculate_loss' fonksiyonunu çağırmalıdır."
    ]
    
    result = await agent.evaluate_student_output(mock_student_output, mock_contrastive_evidence)
    
    print("\n--- Teacher Agent Değerlendirme Sonucu ---\n")
    print(result["evaluation_result"])

if __name__ == "__main__":
    asyncio.run(main())
