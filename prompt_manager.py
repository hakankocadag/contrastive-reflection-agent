import jinja2
import json

class PromptManager:
    def __init__(self, templates_dir: str = "templates"):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            autoescape=jinja2.select_autoescape()
        )
    
    def generate_contrastive_reflection_prompt(self, student_output: str, contrastive_evidence_list: list) -> str:
        """
        Jinja2 kullanarak dinamik contrastive reflection prompt'unu oluşturur.
        """
        template = self.env.get_template("contrastive_reflection.j2")
        return template.render(
            student_output=student_output,
            contrastive_evidence_list=contrastive_evidence_list
        )

# Başlangıçta kullanılacak sahte (mock) veri ile test
if __name__ == "__main__":
    manager = PromptManager()
    
    # Sahte Veriler
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
    
    prompt = manager.generate_contrastive_reflection_prompt(
        student_output=mock_student_output,
        contrastive_evidence_list=mock_contrastive_evidence
    )
    
    print("Oluşturulan Dinamik Prompt:\n")
    print("-" * 50)
    print(prompt)
    print("-" * 50)
