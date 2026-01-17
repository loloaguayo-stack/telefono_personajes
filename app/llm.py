import os
from anthropic import AsyncAnthropic

class LLMManager:
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)

    async def get_response(self, system_prompt: str, user_text: str, history: list = None) -> str:
        if history is None:
            history = []
        
        # Claude usa una estructura clara de 'system' y 'messages'
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20240620", # El más equilibrado para voz
            max_tokens=150, # Mantenemos frases cortas para llamadas
            system=system_prompt,
            messages=history + [{"role": "user", "content": user_text}]
        )
        return response.content[0].text

llm_manager = LLMManager(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
