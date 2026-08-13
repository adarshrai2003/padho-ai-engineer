import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def llm(prompt, json_mode=False):
    kwargs = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    return json.loads(content) if json_mode else content


# ---------- 1. Customer Complaint Processor ----------

def process_complaint(email):
    facts = llm(f"""
Extract from this email as JSON with keys: customer_name, product, issue_summary, sentiment.
If a field isn't mentioned, use null.
Email: {email}
Return ONLY valid JSON.
""", json_mode=True)

    urgency = llm(f"""
Given: {facts}
Rate urgency as one of: Low, Medium, High, Critical.
Return ONLY valid JSON with keys: urgency, reason.
""", json_mode=True)

    reply = llm(f"""
Facts: {facts}
Urgency: {urgency}
Draft a short customer reply matching the urgency tone.
If customer_name is null, address them as "there" instead of using a name.
""")

    action_item = llm(f"""
Facts: {facts}
Urgency: {urgency}
Write a 1-line internal action item for the support ticket.
""")

    return {
        "facts": facts,
        "urgency": urgency,
        "reply": reply,
        "action_item": action_item,
    }


# ---------- 2. Content Pipeline ----------

def content_pipeline(topic):
    angle = llm(f"""
Rough topic: {topic}
Suggest one sharp, specific angle for an article on this. One sentence only.
""")

    outline = llm(f"""
Angle: {angle}
Create a 4-5 point outline for an article on this angle.
""")

    intro = llm(f"""
Angle: {angle}
Outline: {outline}
Write a 3-sentence intro paragraph for this article.
""")

    return {"angle": angle, "outline": outline, "intro": intro}


# ---------- 3. Support Router ----------

def billing_prompt(message, classification):
    return f"You are a billing specialist. Respond to: {message}\nContext: {classification}"

def technical_prompt(message, classification):
    return f"You are a technical support specialist. Respond to: {message}\nContext: {classification}"

def feature_request_prompt(message, classification):
    return f"You are a product specialist logging a feature request. Respond to: {message}\nContext: {classification}"

def route_support_message(message):
    classification = llm(f"""
Message: {message}
Classify as one of: Billing, Technical, Feature_Request.
Return ONLY valid JSON with keys: category, confidence.
""", json_mode=True)

    category = classification["category"]
    if category == "Billing":
        prompt = billing_prompt(message, classification)
    elif category == "Technical":
        prompt = technical_prompt(message, classification)
    else:
        prompt = feature_request_prompt(message, classification)

    response = llm(prompt)
    return {"classification": classification, "response": response}


# ---------- Run examples ----------

if __name__ == "__main__":
    email = """
    Hi, I ordered a laptop 2 weeks ago and it still hasn't shipped.
    I need it for work next Monday. This is really frustrating.
    """
    print("=== Complaint Processor ===")
    print(json.dumps(process_complaint(email), indent=2))

    print("\n=== Content Pipeline ===")
    print(json.dumps(content_pipeline("remote work productivity"), indent=2))

    print("\n=== Support Router ===")
    print(json.dumps(route_support_message("My invoice charged me twice this month"), indent=2))
    