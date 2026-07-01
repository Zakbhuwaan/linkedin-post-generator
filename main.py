import streamlit as st
from few_shot import FewShotPosts
from post_generator import stream_post

st.set_page_config(
    page_title="LinkedIn Post Generator",
    page_icon="✍️",
    layout="centered",
)


@st.cache_resource
def load_few_shot():
    return FewShotPosts()


def _char_badge(text):
    count = len(text)
    color = "red" if count > 2800 else "orange" if count > 1800 else "green"
    st.caption(f":{color}[{count} / 3,000 characters]")


def main():
    st.title("✍️ LinkedIn Post Generator")
    st.caption("On-brand LinkedIn posts in seconds — powered by Llama 3.3 70B & Groq")
    st.divider()

    fs = load_few_shot()

    # ── Topic ──────────────────────────────────────────────────────────────
    st.markdown("#### Topic")
    topic_mode = st.radio(
        "topic_mode",
        ["Choose from list", "Enter my own"],
        horizontal=True,
        label_visibility="collapsed",
    )
    if topic_mode == "Choose from list":
        selected_tag = st.selectbox("Select topic", options=fs.get_tags(), label_visibility="collapsed")
    else:
        selected_tag = st.text_input(
            "Your topic",
            placeholder="e.g. Remote Work, AI Tools, Career Pivots, Burnout...",
            label_visibility="collapsed",
        )

    # ── Controls ───────────────────────────────────────────────────────────
    st.markdown("#### Options")
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_length = st.selectbox("Length", ["Short", "Medium", "Long"])
    with col2:
        selected_language = st.selectbox("Language", ["English", "Hinglish"])
    with col3:
        selected_tone = st.selectbox("Tone", ["Professional", "Storytelling", "Contrarian", "Inspirational"])

    col4, col5 = st.columns(2)
    with col4:
        use_emojis = st.toggle("Add emojis", value=True)
    with col5:
        add_hashtags = st.toggle("Add hashtags", value=True)

    st.divider()

    # ── Buttons ────────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    generate_one = col_a.button("Generate Post", type="primary", use_container_width=True)
    generate_three = col_b.button("Generate 3 Variants", use_container_width=True)

    if "history" not in st.session_state:
        st.session_state.history = []

    tag = selected_tag.strip() if selected_tag else ""

    # ── Single post ────────────────────────────────────────────────────────
    if generate_one:
        if not tag:
            st.warning("Please enter or select a topic first.")
        else:
            st.markdown("---")
            st.markdown("**Your post**")
            result = st.write_stream(
                stream_post(selected_length, selected_language, tag, selected_tone, use_emojis, add_hashtags, fs)
            )
            _char_badge(result)
            st.code(result, language=None)
            st.session_state.history.insert(0, {"tag": tag, "tone": selected_tone, "post": result})

    # ── 3 variants ─────────────────────────────────────────────────────────
    if generate_three:
        if not tag:
            st.warning("Please enter or select a topic first.")
        else:
            st.markdown("---")
            st.info("Generating 3 variants sequentially — switch tabs after all are done.", icon="ℹ️")
            tabs = st.tabs(["Variant 1", "Variant 2", "Variant 3"])
            for i, tab in enumerate(tabs):
                with tab:
                    result = st.write_stream(
                        stream_post(selected_length, selected_language, tag, selected_tone, use_emojis, add_hashtags, fs)
                    )
                    _char_badge(result)
                    st.code(result, language=None)
                    if i == 0:
                        st.session_state.history.insert(0, {"tag": tag, "tone": selected_tone, "post": result})

    # ── History ────────────────────────────────────────────────────────────
    if st.session_state.history:
        st.divider()
        with st.expander(f"📋 Recent posts ({min(len(st.session_state.history), 5)})"):
            for i, item in enumerate(st.session_state.history[:5]):
                st.caption(f"**#{i + 1}** · {item['tag']} · {item['tone']}")
                st.code(item["post"], language=None)
                if i < min(len(st.session_state.history), 5) - 1:
                    st.divider()


if __name__ == "__main__":
    main()
