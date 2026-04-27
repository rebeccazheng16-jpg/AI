"""
Gemini-based translation (multi-language → Chinese) and keyword matching.
Uses google-generativeai SDK.
"""

import json
import google.generativeai as genai

LANG_NAMES = {
    "id": "Indonesian",
    "ko": "Korean",
    "ja": "Japanese",
    "zh": "Chinese",
    "auto": None,
}


def init_gemini(api_key: str):
    """Initialize Gemini with API key."""
    genai.configure(api_key=api_key)


def translate_sentences(sentences: list, api_key: str, source_language: str = "id") -> list:
    """
    Translate sentences to Chinese using Gemini 2.5 Flash.
    Supports Indonesian, Korean, Japanese, Chinese (skip), and auto-detect.

    Input: [{"text": "wow beneran ya", "start": 2.05, "end": 5.10, ...}, ...]
    Output: same list with added "translation" field
    """
    # If source is Chinese, no translation needed
    if source_language == "zh":
        for s in sentences:
            s["translation"] = s["text"]
        return sentences

    init_gemini(api_key)

    # Batch all sentences into one prompt for efficiency
    texts = [s["text"] for s in sentences]
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))

    lang_name = LANG_NAMES.get(source_language)
    if lang_name:
        lang_desc = f"the following {lang_name} sentences"
    else:
        lang_desc = "the following sentences (auto-detect language)"

    prompt = f"""Translate {lang_desc} to Chinese (中文).
Return ONLY a JSON array of strings, one translation per sentence, in the same order.
Keep it natural and colloquial. Do not add explanations.

Sentences:
{numbered}

Return format: ["translation1", "translation2", ...]"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    try:
        text = response.text.strip()
        # Strip markdown code fence if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            text = text.strip()
        translations = json.loads(text)
    except (json.JSONDecodeError, IndexError):
        # Fallback: return empty translations
        translations = [""] * len(sentences)

    for i, s in enumerate(sentences):
        s["translation"] = translations[i] if i < len(translations) else ""

    return sentences


def match_keywords(chinese_keywords: list, sentences: list, api_key: str) -> dict:
    """
    Given Chinese keywords, find the corresponding Indonesian words in the transcription.

    Input:
        chinese_keywords: ["真的", "百万", "一天"]
        sentences: [{"text": "wow beneran ya", "translation": "哇真的吗", ...}, ...]

    Output: {"真的": "beneran", "百万": "juta", "一天": "sehari"}
    """
    init_gemini(api_key)

    # Build context: all sentences with translations
    context_lines = []
    for s in sentences:
        context_lines.append(f"原文: {s['text']}")
        context_lines.append(f"中文: {s.get('translation', '')}")
        context_lines.append("")

    context = "\n".join(context_lines)
    keywords_str = ", ".join(chinese_keywords)

    prompt = f"""Below are transcribed sentences with Chinese translations from a video.

{context}

For each Chinese keyword below, find the EXACT original-language word that appears in the transcription above.
IMPORTANT: Only pick words that actually appear in the original text (原文). Do not invent translations.

Chinese keywords: {keywords_str}

Return ONLY a JSON object mapping each Chinese keyword to its match from the original text.
Format: {{"中文词": "original_word", ...}}
If a keyword has no match in the transcription, map it to null."""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    try:
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            text = text.strip()
        matches = json.loads(text)
    except (json.JSONDecodeError, IndexError):
        matches = {kw: None for kw in chinese_keywords}

    return matches
