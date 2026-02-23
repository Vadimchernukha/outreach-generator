"""
humanizer.py — делает сгенерированные сообщения живыми и человечными через Claude
"""
import anthropic

HUMANIZE_PROMPT = """You are a native {language} speaker who writes {platform} messages like a real human.

Rewrite the message below so it sounds like a real person typing — natural, direct, zero fluff:
- Keep the exact meaning, key facts, and any CTA
- Natural sentence flow — appropriate for {platform}
- Remove all corporate/AI language:
  ("I hope this message finds you well", "I wanted to reach out",
   "leverage", "synergies", "circle back", "touch base", etc.)
{platform_specific}
- Do NOT make it longer than the original
- Write in {language}

Original message:
{message}

Return ONLY the rewritten message. No quotes, no labels, no explanation."""


def humanize(client: anthropic.Anthropic, message_text: str, language: str = "English", platform: str = "LinkedIn") -> str:
    """
    Переписывает одно сообщение в живой человеческий стиль.

    Args:
        client: инстанс anthropic.Anthropic
        message_text: оригинальный текст сообщения
        language: язык для переписи
        platform: "LinkedIn" или "Email"

    Returns:
        str — очеловеченная версия сообщения
    """
    platform = platform.lower()
    if platform == "linkedin":
        platform_specific = "- Professional but conversational — LinkedIn style\n- Short, punchy sentences\n- No emojis unless context genuinely calls for it"
    elif platform == "email":
        platform_specific = "- Professional but warm — email style\n- Slightly more formal than LinkedIn but still personal\n- No emojis in professional emails"
    else:
        platform_specific = "- Natural, professional tone"

    prompt = HUMANIZE_PROMPT.format(
        message=message_text,
        language=language.capitalize(),
        platform=platform.capitalize(),
        platform_specific=platform_specific,
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()
