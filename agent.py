from config import Config
import ollama
from groq import Groq
from logs.prompts import Prompts
import json


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
                    try:
                        data = json.loads(answer)
                    except json.JSONDecodeError as ex:
                        return {
    "vocabulary_notes": "",
    "sentence_structure_notes": "",
    "stylistic_notes": "",
    "observed_signals": {
        "repetition_low_high": "low|medium|high",
        "structure_uniformity_low_high": "low|medium|high",
        "predictability_low_high": "low|medium|high"
    },
    "error": f"Parsing failed: {ex}",
    "failed": True
}
                
                    parsed_answer = self.parse_observed_signals(data)
                    return parsed_answer
                
                print("No answer generated.")
                return {
    "vocabulary_notes": "",
    "sentence_structure_notes": "",
    "stylistic_notes": "",
    "observed_signals": {
        "repetition_low_high": "low|medium|high",
        "structure_uniformity_low_high": "low|medium|high",
        "predictability_low_high": "low|medium|high"
    },
    "error": "Agent didnt return a response",
    "failed": True
}
            
            except Exception as ex:
                print(f"There was an error while generating response: \n\t\u2022 {ex}")
                return {
    "vocabulary_notes": "",
    "sentence_structure_notes": "",
    "stylistic_notes": "",
    "observed_signals": {
        "repetition_low_high": "low|medium|high",
        "structure_uniformity_low_high": "low|medium|high",
        "predictability_low_high": "low|medium|high"
    },
    "error": f"Error occured during GROQ Agent process: {ex}",
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
                try:
                        data = json.loads(content)
                except json.JSONDecodeError as ex:
                        return {
    "vocabulary_notes": "",
    "sentence_structure_notes": "",
    "stylistic_notes": "",
    "observed_signals": {
        "repetition_low_high": "low|medium|high",
        "structure_uniformity_low_high": "low|medium|high",
        "predictability_low_high": "low|medium|high"
    },
    "error": f"Parsing failed: {ex}",
    "failed": True
}
                parsed_content = self.parse_observed_signals(content)
                return parsed_content

            except Exception as ex:
                print(f"⚠ Ollama generation error: {ex}")

                return {
    "vocabulary_notes": "",
    "sentence_structure_notes": "",
    "stylistic_notes": "",
    "observed_signals": {
        "repetition_low_high": "low|medium|high",
        "structure_uniformity_low_high": "low|medium|high",
        "predictability_low_high": "low|medium|high"
    },
    "error": f"Error occured during OLLAMA Agent process: {ex}",
    "failed": True
}
    
    def format_dict(self, x):
        txt = "=========================================\n"
        for keys, values in x.items():
            txt += f" - The {keys} for the item: {values}\n"
        txt += "=========================================\n"
        return txt
    
    def parse_observed_signals(self, data: dict):
        """
        Converts LLM observed_signals into numeric values usable by your scoring system.
        """
        
        self.mapping = {
            "low": 0.2,
            "medium": 0.5,
            "high": 0.8
        }

        result = {
            "repetition": 0.0,
            "structure_uniformity": 0.0,
            "predictability": 0.0,
            "notes": {}
        }

        if not isinstance(data, dict):
            return result

        signals = data.get("observed_signals", {})

        if not isinstance(signals, dict):
            return result

        # Repetition
        rep = signals.get("repetition_low_high", "low")
        result["repetition"] = self.mapping.get(rep, 0.2)
        result["notes"]["repetition"] = rep

        # Structure uniformity
        struct = signals.get("structure_uniformity_low_high", "low")
        result["structure_uniformity"] = self.mapping.get(struct, 0.2)
        result["notes"]["structure"] = struct

        # Predictability
        pred = signals.get("predictability_low_high", "low")
        result["predictability"] = self.mapping.get(pred, 0.2)
        result["notes"]["predictability"] = pred

        return result
    
    
    
if __name__ == "__main__":
    agent = Agent()
    test = """
    
    The afternoon light over the Charles River was fading into a deep shade of twilight. 
    Elian tucked his collar against the crisp autumn breeze as he walked the familiar path toward the 
    Boston Public Library in Copley Square. He was supposed to be returning a biography on maritime 
    history, but the city had a way of pulling him off his usual route.
    Instead, he found himself ducking down Province Street, drawn by the warm glow of an antiquarian 
    bookshop he had never noticed before. 
    The bell above the door chimed a soft, dissonant note as he stepped inside.
    The air was thick with the scent of old paper and roasted coffee beans.
    "Looking for anything specific?" a voice asked from behind a towering stack of leather-bound journals.
    The shopkeeper, an elderly woman with silver hair and wire-rimmed glasses, peered over her books.
    "Not really," Elian admitted, trailing a finger along a dusty wooden shelf. 
    "Just exploring."The woman nodded knowingly and gestured to the back corner. 
    "Try the bottom shelf in the shadow of the ladder.
    I think you'll find what you didn't know you were looking for.
    "Elian navigated the narrow aisles, the wooden floorboards creaking beneath his boots.
    He knelt in the dim light and reached for a heavy, 
    cloth-bound volume sandwiched between two newer-looking books.
    When he pulled it out, a cloud of dust danced in a stray beam of sunlight. 
    The cover bore no title, just an embossed silver compass rose.
    He opened it to the middle pages, expecting to see a faded map or an old ledger. 
    Instead, he found a collection of intricate, 
    hand-drawn charcoal sketches depicting places he had visited, but with impossible details woven 
    into them. A sketch of the Boston Public Garden showed the iconic weeping willows,
    but nestled in the branches were glowing, bioluminescent flowers."What is this place?" 
    Elian whispered, tracing his finger over the textured paper.
    "It is a record of the places that exist in the spaces between," 
    the shopkeeper said, appearing quietly beside him. 
    "The city you see every day is just the backdrop. The magic lies in the details.
    "He looked up, a dozen questions forming on his lips, 
    but the woman simply smiled and took the book from his hands, 
    replacing it with a quiet grace. "Come back when you are ready to see the real city," 
    she said.Dazed, Elian stepped back out onto the bustling street. 
    The familiar city skyline suddenly felt different, 
    like a stage waiting for the curtain to rise. 
    He looked toward the river, 
    wondering what other hidden landscapes were waiting to be discovered just out of sight.
    
    """.strip() # scores 0.60 for signal.one()
     
    
    print(agent.generate(test))