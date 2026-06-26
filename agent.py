from config import Config
import ollama
from groq import Groq
from logs.prompts import Prompts


class Agent:
    def __init__(self, 
                 api_key=Config.GROQ_API_KEY, 
                 llm_model:str=Config.LLM_MODEL,
                 use_ollama:bool=False) -> None:
        
        if use_ollama:
            self.backend = 'ollama'
            self.ollama_model = 'qwen3:0.6b'

            try:
                ollama.show(self.ollama_model)
                print(f"✓ Using Ollama ({self.ollama_model})")

            except Exception:
                print(f"⚠ Ollama model '{self.ollama_model}' not found")
                print(f"Run: ollama pull {self.ollama_model}")
        else:
            self.backend = "grok"
            self.ai = Groq(api_key=api_key)
        
        self.llm_model = llm_model
        
    def generate(self, user_text):
        m = [
            {"role": "system", "content": Prompts.determine_ai_or_human},
            {"role": "user", "content": f"<<<TEXT>>>\n{user_text}\n<<<TEXT>>>"}
        ]
        if self.backend == 'grok':
            try:
                response = self.ai.chat.completions.create(
                model=self.llm_model,
                messages=m,
                
            )

                answer = response.choices[0].message.content
                
                if answer:
                
                    parsed_answer = self.parse(answer)
                    parsed_answer["failed"] = False
                    return parsed_answer
                
                print("No answer generated.")
                return {
                    "origin": "unknown",
                    "classification": "Unknown",
                    "confidence": 0.0,
                    "signal1_score": None,
                    "signal2_score": None,
                    "reason": "The AI analyzer failed to generate a response.",
                    "failed": True
                }
            
            except Exception as ex:
                print(f"There was an error while generating response: \n\t\u2022 {ex}")
                return {
                    "origin": "unknown",
                    "classification": "Unknown",
                    "confidence": 0.0,
                    "signal1_score": None,
                    "signal2_score": None,
                    "reason": f"The AI analyzer failed to generate a response: {ex}",
                    "failed": True
                }
                
        else:
            try:
             
                client = ollama.Client(timeout=60.0)

               
                kwargs = {
                    'model': self.ollama_model,
                    'messages': m,
                    'options': {
                        'temperature': 0.2,
                    }
                }
            

                
                response = client.chat(**kwargs)

                content = response['message']['content']
                print("\nOllama Response and content are created successfully\n")
              
                #print(f'\n\n\t\u2022CONTENT: {content}')
                parsed_content = self.parse(content)
                parsed_content['failed'] = False
                return parsed_content

            except Exception as ex:
                print(f"⚠ Ollama generation error: {ex}")

                return {
                    "origin": "unknown",
                    "classification": "Unknown",
                    "confidence": 0.0,
                    "signal1_score": None,
                    "signal2_score": None,
                    "reason": f"The Ollama AI analyzer failed to generate a response: {ex}",
                    "failed": True
                }
    
    def format_dict(self, x):
        txt = "=========================================\n"
        for keys, values in x.items():
            txt += f" - The {keys} for the item: {values}\n"
        txt += "=========================================\n"
        return txt
    
    def parse(self, response)->dict:
        return {} 