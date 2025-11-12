from typing import List, Tuple
from openai import OpenAI
import os

class ConversationMemory:
    """
    Maintains a short sliding window of recent turns and a running summary
    of older context to keep prompts small.
    """
    def __init__(self, max_turns: int = 6):
        self.max_turns = max_turns
        self.turns: List[Tuple[bool,str]] = []  # (is_user, text)
        self.summary: str = ""

    def add_turn(self, text: str, is_user: bool = True):
        self.turns.append((is_user, text))
        if len(self.turns) > self.max_turns:
            # summarize oldest two turns into running summary
            oldest = self.turns[:-self.max_turns]
            self.turns = self.turns[-self.max_turns:]
            snippet = "\n".join(
                ["User: "+t[1] if t[0] else "Assistant: "+t[1] for t in oldest]
            )
            self.summary = self._summarize(self.summary, snippet)

    def build_context(self, system_prompt: str) -> str:
        recent = "\n".join(
            ["User: "+t[1] if t[0] else "Assistant: "+t[1] for t in self.turns]
        )
        ctx = f"{system_prompt}\n\n"
        if self.summary:
            ctx += f"[Running summary]\n{self.summary}\n\n"
        ctx += f"[Recent turns]\n{recent}"
        return ctx

    def _summarize(self, prev_summary: str, new_text: str) -> str:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        prompt = (
            "Summarize the conversation snippet into 3-4 bullet points that preserve factual context. "
            "Be concise.\n\n"
            f"Previous summary:\n{prev_summary}\n\n"
            f"New snippet:\n{new_text}\n\n"
            "Return a concise updated summary."
        )
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role":"system","content":"You produce terse, accurate summaries."},
                {"role":"user","content":prompt}
            ],
            temperature=0.2
        )
        return resp.choices[0].message.content.strip()

