"""
generator.py — генерация цепочки сообщений через Claude (Anthropic)

Использует Tool Use для гарантированного structured output —
никакого хрупкого парсинга текста.
"""
import json
import anthropic

# Схема инструмента — Claude обязан вернуть данные в этом формате
OUTREACH_TOOL = {
    "name": "save_outreach_chain",
    "description": "Save the generated outreach message chain for a contact.",
    "input_schema": {
        "type": "object",
        "properties": {
            "strategy_rationale": {
                "type": "string",
                "description": "1-2 sentences explaining the chosen outreach angle and funnel logic for this specific contact."
            },
            "messages": {
                "type": "array",
                "description": "The sequence of outreach messages.",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "properties": {
                        "step": {
                            "type": "integer",
                            "description": "Message number in the sequence (1, 2, 3...)."
                        },
                        "send_after": {
                            "type": "string",
                            "description": "When to send this message, e.g. 'Day 1', 'Day 3'."
                        },
                        "angle": {
                            "type": "string",
                            "description": "The hook or angle for this message, e.g. 'Curiosity hook', 'Social proof', 'Soft CTA'."
                        },
                        "text": {
                            "type": "string",
                            "description": "Full text of the message to send."
                        }
                    },
                    "required": ["step", "send_after", "angle", "text"]
                }
            }
        },
        "required": ["strategy_rationale", "messages"]
    }
}

GENERATION_PROMPT = """You are an expert B2B sales strategist working for {company_name}.

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
(Research data — use ALL relevant insights to personalise)
{dynamic_fields}

=== TONE & STYLE ===
{tone_instructions}

=== FUNNEL RULES ===
{message_rules}

Message timing:
{timing_str}

Design a smart funnel tailored SPECIFICALLY to this person and their company context.
You decide the angles and escalation logic based on the intelligence provided."""


def generate_chain(client: anthropic.Anthropic, contact: dict, config: dict) -> dict:
    """
    Генерирует сырую цепочку сообщений для одного контакта.

    Args:
        client: инстанс anthropic.Anthropic
        contact: данные контакта из CSV
        config: конфиг клиента из YAML

    Returns:
        dict с ключами 'strategy_rationale' и 'messages'
    """
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

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        tools=[OUTREACH_TOOL],
        tool_choice={"type": "tool", "name": "save_outreach_chain"},  # принудительно вызвать инструмент
        messages=[{"role": "user", "content": prompt}]
    )

    # Извлекаем результат из tool_use блока
    for block in response.content:
        if block.type == "tool_use" and block.name == "save_outreach_chain":
            return block.input

    raise ValueError(f"Claude did not call the expected tool. Response: {response.content}")
