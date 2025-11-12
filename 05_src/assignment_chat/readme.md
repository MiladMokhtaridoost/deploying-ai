# Assignment Chatbot (Final Project)

**Model:** `gpt-4o`  
**Services:**  
1) Open-Meteo API transform  
2) Chroma semantic search (persistent)  
3) Function calling (date math, unit conversion)  

**Extras:** Guardrails, memory summarization, Gradio UI.

## Run locally

```bash
source ~/Desktop/DSI/deploying-ai/deploying-ai-env/bin/activate
cd 05_src/assignment_chat
pip install -r requirements.txt
python app.py
