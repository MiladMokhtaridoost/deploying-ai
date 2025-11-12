from dotenv import load_dotenv
load_dotenv('../../05_src/.secrets')

import gradio as gr
from openai import OpenAI
import os
from guardrails import check_guardrails
from memory import ConversationMemory
from router import route_message

# Initialize client and memory
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
memory = ConversationMemory(max_turns=6)

SYSTEM_PROMPT = (
    "You are a friendly research assistant named AIVA. "
    "You respond in a professional, concise, and warm tone. "
    "When useful, you call external tools via the router to provide accurate data. "
    "If a user asks for restricted topics, refuse politely."
)

README = """
### Assignment Chatbot (Final Project)
This chatbot integrates three services:

1️⃣ **Open-Meteo API** — retrieves and summarizes weather info.
2️⃣ **Chroma Semantic Search** — finds relevant facts from a tiny embedded dataset.
3️⃣ **Function Calling** — performs date math, unit conversions, and small CSV lookups.

Extra features:
- Guardrails: prevent prompt leaks & block disallowed topics.
- Memory: summarizes long chats to maintain context (short-term history window).
- Model: `gpt-4o` via OpenAI API.

All code is self-contained in `05_src/assignment_chat/`.
"""

def chat_interface(user_input, history):
    # 1. Guardrails check
    blocked, reason = check_guardrails(user_input)
    if blocked:
        return f"Sorry, I can’t respond to that ({reason})."

    # 2. Append to memory and build context
    memory.add_turn(user_input)
    context = memory.build_context(SYSTEM_PROMPT)

    # 3. Route message
    response_text = route_message(client, user_input, context)

    # 4. Save and summarize if needed
    memory.add_turn(response_text, is_user=False)

    return response_text

with gr.Blocks(title="Assignment Chatbot") as demo:
    gr.Markdown("# Assignment Chatbot — Milad")
    gr.Markdown(README)

    chat = gr.ChatInterface(
        fn=chat_interface,
        title="Milad’s AI Research Bot",
        chatbot=gr.Chatbot(height=450),
        textbox=gr.Textbox(placeholder="Ask me something...", label="Your message"),
    )

if __name__ == "__main__":
    demo.launch()

