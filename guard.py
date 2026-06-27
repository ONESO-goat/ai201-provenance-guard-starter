from signals import Signals
from agent import Agent

signal = Signals()
agent = Agent()

def analyze(text):
    
    signals_result = signal.sequence(text)
    if not signals_result:
        return {}
    response = agent.generate(text)
    if not response:
        return {}
    
    ai_result = signal.three(response)

    print(f"\nSEQUENCE SCORES: \n\t- signal 1 {signals_result['signal1_score']} \n\t- signal 2 {signals_result['signal2_score']} \n\t- OVERALL {signals_result['score']} \n\t- AI {ai_result['score']}")
    fs = float(min(signals_result['score'] + ai_result['score'], 1.0))
    print(f"\nFINAL SCORE: {fs}")
    reason = signals_result['reasons']
    reason['ai_overview'] = ai_result['reason']
    if fs < 0.5:
        origin = "likely_human"
    elif 0.5 <= fs < 0.7:
        origin = "uncertain"
    else:
        origin = "likely_ai"
        
    return {
        "origin": origin,
        "score": fs,
        "reason": reason
    }