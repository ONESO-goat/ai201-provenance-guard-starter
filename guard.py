from signals import Signals
from agent import Agent

signal = Signals()
agent = Agent()

def test1(text):
    signals_result = signal.sequence(text)
    if not signals_result:
        return "No results were made during signal seqence"
    response = agent.generate(text)
    if not response:
        return "Agent returned no response in test1"
    
    ai_result = signal.three(response)