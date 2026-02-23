"""
humanizer.py — делает сгенерированные сообщения живыми и человечными
через выбранную LLM (Claude и т.п.)
"""

HUMANIZE_PROMPT = """
You are a native {language} speaker who writes Telegram messages like a real human.

Rewrite the message below so it sounds like a real person typing — casual, direct, zero fluff:
- Keep the exact meaning, key facts, and any CTA
- Natural sentence flow — short, punchy, real
- Remove all corporate/AI language:
  ("I hope this message finds you well", "I wanted to reach out",
   "leverage", "synergies", "circle back", "touch base", etc.)
- Small human imperfections are fine — it's Telegram, not a formal email
- No emojis unless the context genuinely calls for it
- Do NOT make it longer than the original
- Write in {language}

Original message:
{message}

Return ONLY the rewritten message. No quotes, no labels, no explanation.
"""


def humanize(model, message_text: str, language: str = "English") -> str:
    """Переписывает одно сообщение в живой человеческий стиль."""
    prompt = HUMANIZE_PROMPT.format(
        message=message_text,
        language=language.capitalize(),
    )
    response = model.generate_content(prompt)
    return response.text.strip()
