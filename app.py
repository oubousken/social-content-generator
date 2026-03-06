import streamlit as st
import anthropic

st.set_page_config(page_title="Social Media Content Generator", page_icon="✨", layout="centered")

st.title("Social Media Content Generator")
st.caption("Generate captions, hashtags, and post ideas instantly with AI")

# Sidebar for API key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.caption("Get your key at console.anthropic.com")

# Main form
st.subheader("What do you want to post about?")

topic = st.text_input("Topic or niche", placeholder="e.g. fitness, coffee shop, digital marketing")
platform = st.selectbox("Platform", ["Instagram", "Twitter/X", "LinkedIn", "TikTok", "Facebook"])
tone = st.selectbox("Tone", ["Engaging & Fun", "Professional", "Motivational", "Casual", "Educational"])
num_posts = st.slider("Number of post ideas", min_value=1, max_value=5, value=3)

generate = st.button("Generate Content", type="primary", use_container_width=True)

if generate:
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
    elif not topic:
        st.error("Please enter a topic.")
    else:
        with st.spinner("Generating your content..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)

                prompt = f"""You are a social media expert. Generate {num_posts} unique post ideas for {platform}.

Topic: {topic}
Tone: {tone}

For each post provide:
1. Caption (ready to copy-paste)
2. Hashtags (10 relevant ones)
3. Best time to post tip

Format each post clearly with numbered sections. Make them engaging and optimized for {platform}."""

                message = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )

                result = message.content[0].text

                st.success("Content generated!")
                st.markdown("---")
                st.markdown(result)

                st.download_button(
                    label="Download as text file",
                    data=result,
                    file_name=f"{topic.replace(' ', '_')}_content.txt",
                    mime="text/plain"
                )

            except anthropic.AuthenticationError:
                st.error("Invalid API key. Please check your key and try again.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")