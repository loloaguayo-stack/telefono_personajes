from dataclasses import dataclass

@dataclass
class Agent:
    name: str
    voice_id: str
    greeting: str

agents = [
    Agent("Carmen", "VOICE_1", "Hola… soy Carmen. Qué alegría oírte."),
    Agent("Paco", "VOICE_2", "Ey, soy Paco. Cuéntame, ¿cómo va todo?")
]

def get_agent_by_phone(phone: str) -> Agent:
    try:
        return agents[int(phone[-1]) % len(agents)]
    except Exception:
        return agents[0]
