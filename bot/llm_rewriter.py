import os


class LlmRewriter:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.enabled = bool(self.api_key)

    async def rewrite(self, deterministic_answer: str) -> str:
        if not self.enabled:
            return deterministic_answer

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Rewrite the provided office monitoring answer in a friendly Discord tone. "
                            "Do not add, remove, or change any device counts, room names, wattage values, "
                            "energy values, alerts, or statuses."
                        ),
                    },
                    {"role": "user", "content": deterministic_answer},
                ],
                temperature=0.3,
            )
            rewritten = response.choices[0].message.content
            return rewritten.strip() if rewritten else deterministic_answer
        except Exception:
            return deterministic_answer
