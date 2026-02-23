"""
generator.py — генерация цепочки сообщений через LLM (Claude, etc.)
"""
import json

GENERATION_PROMPT = """
You are an expert B2B sales strategist working for {company_name}.

Your task: Write a {num_messages}-message cold outreach sequence for Telegram for the contact below.
Goal: {goal}

=== ABOUT {company_name} ===
{company_context}

=== CONTACT PROFILE ===
Name: {person_name}
Title: {title}
Company: {company_name_contact}
Website: {website}
Industry: {industry}
Company Size: {company_size}
Location: {company_country}, {company_city}

=== COMPANY INTELLIGENCE ===
(Research data — use ALL relevant insights)
{dynamic_fields}

=== TONE & STYLE ===
{tone_instructions}

=== FUNNEL RULES ===
{message_rules}

Message timing:
{timing_str}

Design a smart funnel tailored SPECIFICALLY to this person.
You decide the angles and escalation logic.

Output ONLY valid JSON — no markdown, no explanation:
{{
  "strategy_rationale": "1-2 sentences on your chosen approach",
  "messages": [
    {{
      "step": 1,
      "send_after": "Day 1",
      "angle": "Hook type",
      "text": "Full message text"
    }}
  ]
}}
"""


def generate_chain(model, contact: dict, config: dict) -> dict:
    """Генерирует сырую цепочку сообщений для одного контакта."""
    funnel = config.get("funnel", {})
    timing = funnel.get("timing", ["Day 1", "Day 3", "Day 6", "Day 10", "Day 14"])
    timing_str = "\n".join([f"  - Message {i+1}: {t}" for i, t in enumerate(timing)])

    prompt = GENERATION_PROMPT.format(
        company_name=config.get("company_name", "Our Company"),
        num_messages=funnel.get("num_messages", 5),
        goal=funnel.get("goal", "Get a reply or book a call"),
        company_context=config.get("company_context", ""),
        person_name=contact.get("person_name", ""),
        title=contact.get("title", ""),
        company_name_contact=contact.get("company_name", ""),
        website=contact.get("website", ""),
        industry=contact.get("industry", ""),
        company_size=contact.get("company_size", ""),
        company_country=contact.get("company_country", ""),
        company_city=contact.get("company_city", ""),
        dynamic_fields=contact.get("dynamic_fields", ""),
        tone_instructions=config.get("tone_instructions", ""),
        message_rules=funnel.get("message_rules", ""),
        timing_str=timing_str,
    )

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Убираем markdown-обёртку если Gemini добавил
    if "```" in raw:
        for part in raw.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("{"):
                raw = part
                break

    return json.loads(raw)
