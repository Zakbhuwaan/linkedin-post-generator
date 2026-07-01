from llm_helper import llm
from few_shot import FewShotPosts

_TONE_MAP = {
    "Professional":   "authoritative and professional — clear, direct, credible",
    "Storytelling":   "narrative and personal — open with a story or real anecdote",
    "Contrarian":     "bold and contrarian — challenge a common assumption or share a hot take",
    "Inspirational":  "motivational and uplifting — energise and move the reader to action",
}

_LENGTH_MAP = {
    "Short":  "1 to 5 lines",
    "Medium": "6 to 10 lines",
    "Long":   "11 to 15 lines",
}


def _build_prompt(length, language, tag, tone, use_emojis, add_hashtags, fs):
    lang_note = " (mix of Hindi and English; script always in English)" if language == "Hinglish" else ""
    emoji_line = "Use relevant emojis throughout." if use_emojis else "Do not use any emojis."
    hashtag_line = "End with 3–5 relevant hashtags." if add_hashtags else "Do not include hashtags."

    prompt = f"""Generate a LinkedIn post. Output only the post text — no preamble, no explanation.

1) Topic: {tag}
2) Length: {_LENGTH_MAP[length]}
3) Language: {language}{lang_note}
4) Tone: {_TONE_MAP[tone]}
5) {emoji_line}
6) {hashtag_line}
"""

    examples = fs.get_filtered_posts(length, language, tag)
    if examples:
        prompt += "\n7) Mirror the writing style of these real high-engagement posts:\n"
        for i, post in enumerate(examples[:2]):
            prompt += f"\nExample {i + 1}:\n{post['text']}\n"

    return prompt


def stream_post(length, language, tag, tone, use_emojis, add_hashtags, fs):
    prompt = _build_prompt(length, language, tag, tone, use_emojis, add_hashtags, fs)
    for chunk in llm.stream(prompt):
        yield chunk.content


def generate_post(length, language, tag, tone="Professional", use_emojis=True, add_hashtags=True, fs=None):
    if fs is None:
        fs = FewShotPosts()
    prompt = _build_prompt(length, language, tag, tone, use_emojis, add_hashtags, fs)
    return llm.invoke(prompt).content
