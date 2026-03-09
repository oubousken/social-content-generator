import streamlit as st
import anthropic
import re

GUMROAD_URL = "https://bousken.gumroad.com/l/fkekil"
FREE_LIMIT = 3

st.set_page_config(page_title="Social Media Content Generator", page_icon="✨", layout="centered")

st.title("Social Media Content Generator")
st.caption("Generate captions, hashtags, and post ideas instantly with AI")

# Track free usage
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0

# Sidebar
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.caption("Get your key at console.anthropic.com")
    st.markdown("---")
    remaining = FREE_LIMIT - st.session_state.usage_count
    if remaining > 0:
        st.info(f"Free generations left: {remaining}/{FREE_LIMIT}")
    else:
        st.warning("Free limit reached!")
        st.markdown(f"[Unlock unlimited access — $9]({GUMROAD_URL})")

# Main form
st.subheader("What do you want to post about?")

topic = st.text_input("Topic or niche", placeholder="e.g. fitness, coffee shop, digital marketing")
platform = st.selectbox("Platform", ["Instagram", "Twitter/X", "LinkedIn", "TikTok", "Facebook"])
tone = st.selectbox("Tone", ["Engaging & Fun", "Professional", "Motivational", "Casual", "Educational"])
num_posts = st.slider("Number of post ideas", min_value=1, max_value=5, value=3)

# Character limits per platform
char_limits = {"Instagram": 2200, "Twitter/X": 280, "LinkedIn": 3000, "TikTok": 2200, "Facebook": 63206}

generate = st.button("Generate Content", type="primary", use_container_width=True)

if generate:
    if not topic:
        st.error("Please enter a topic.")
    elif st.session_state.usage_count >= FREE_LIMIT and not api_key:
        st.error("You've used all 3 free generations.")
        st.markdown(f"### [Unlock unlimited access for $9]({GUMROAD_URL})")
    elif not api_key and st.session_state.usage_count >= FREE_LIMIT:
        st.error("Please enter your API key or purchase access.")
    else:
        # Allow free use without API key up to limit
        if not api_key and st.session_state.usage_count < FREE_LIMIT:
            st.warning("Using free trial. Add your API key for unlimited use.")

        with st.spinner("Generating your content..."):
            try:
                # Use provided key or demo behavior
                if not api_key:
                    st.error("Please enter your Anthropic API key to generate content.")
                    st.stop()

                client = anthropic.Anthropic(api_key=api_key)

                prompt = f"""You are a social media expert. Generate {num_posts} unique post ideas for {platform}.

Topic: {topic}
Tone: {tone}
Character limit per post: {char_limits[platform]}

For each post provide:
1. Caption (ready to copy-paste, must be under {char_limits[platform]} characters)
2. Hashtags (10 relevant ones)
3. Best time to post tip

Separate each post with ---. Make them engaging and optimized for {platform}."""

                message = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )

                result = message.content[0].text
                st.session_state.usage_count += 1

                st.success("Content generated!")
                st.markdown("---")

                # Split posts and display each in a card with copy button
                posts = result.split("---")
                for i, post in enumerate(posts):
                    post = post.strip()
                    if not post:
                        continue
                    with st.container(border=True):
                        st.markdown(post)
                        # Character count for caption
                        caption_match = re.search(r'Caption[:\s]+(.+?)(?=Hashtags|$)', post, re.DOTALL | re.IGNORECASE)
                        if caption_match:
                            caption_text = caption_match.group(1).strip()
                            char_count = len(caption_text)
                            limit = char_limits[platform]
                            color = "green" if char_count <= limit else "red"
                            st.markdown(f"**Caption length:** :{color}[{char_count}/{limit} characters]")
                        st.code(post, language=None)

                st.download_button(
                    label="Download all as text file",
                    data=result,
                    file_name=f"{topic.replace(' ', '_')}_content.txt",
                    mime="text/plain"
                )

                # Show upsell after free uses
                remaining = FREE_LIMIT - st.session_state.usage_count
                if remaining <= 0:
                    st.warning(f"You've used all {FREE_LIMIT} free generations.")
                    st.markdown(f"### [Unlock unlimited access for $9]({GUMROAD_URL})")
                else:
                    st.info(f"Free generations left: {remaining}/{FREE_LIMIT}")

            except anthropic.AuthenticationError:
                st.error("Invalid API key. Please check your key and try again.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")