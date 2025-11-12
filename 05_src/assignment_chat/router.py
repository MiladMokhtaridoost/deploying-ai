import re
from openai import OpenAI
from services.api_service import summarize_weather
from services.semantic_service import semantic_query
from services.tools_service import c_to_f, f_to_c, days_until

def route_message(client: OpenAI, user_text: str, context: str) -> str:
    """
    Very lightweight router:
    - weather intent: "weather in <city>" or "forecast <city>"
    - semantic intent: "search:" or "find:" prefix
    - tool intent: "convert 25C", "25F to C", "days until 2026-01-01"
    Otherwise: fallback to general chat.
    """
    t = user_text.lower().strip()

    # Weather: detect "weather in <city>"
    m = re.search(r"weather in ([a-zA-Z\s]+)", t)
    if m:
        city = m.group(1).strip().title()
        # naive geocode defaults (Toronto)
        lat, lon = 43.65107, -79.347015
        if "vancouver" in t: lat, lon = 49.2827, -123.1207
        if "montreal" in t:  lat, lon = 45.5019, -73.5674
        wx = summarize_weather(lat, lon, city)
        return f"{wx.summary} {wx.advice}"

    # Semantic search: prefixed with search:/find:
    if t.startswith("search:") or t.startswith("find:"):
        q = user_text.split(":",1)[1].strip()
        ans = semantic_query(q, k=3)
        return f"Top passages:\n- " + "\n- ".join(ans.top_passages[:3]) + f"\n\nSynthesis: {ans.answer}"

    # Tool: conversions and date math
    if re.search(r"\b(\d+)\s?c\b", t):
        c = float(re.search(r"(\d+)\s?c", t).group(1))
        return c_to_f(c).result
    if re.search(r"\b(\d+)\s?f\b", t):
        f = float(re.search(r"(\d+)\s?f", t).group(1))
        return f_to_c(f).result
    if "days until" in t:
        d = t.split("days until",1)[1].strip()
        return days_until(d).result

    # Fallback general chat with context
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"system","content":context},
            {"role":"user","content":user_text}
        ],
        temperature=0.4,
    )
    return resp.choices[0].message.content.strip()

