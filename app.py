import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to set theme based on user input
def set_theme(dark_mode):
    if dark_mode:
        st.markdown(
            """
            <style>
            body {
                background-color: #121212;
                color: white;
            }
            .stButton>button {
                background-color: #F39C12;
                color: white;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            body {
                background-color: white;
                color: black;
            }
            .stButton>button {
                background-color: #4CAF50;
                color: white;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

# Prompt generator
def build_prompt(transcript_text, word_limit, language):
    return f"""You are a YouTube video summarizer. Please summarize the following transcript into key bullet points within {word_limit} words. The summary should be in {language}.\n\n{transcript_text}"""

# Extract YouTube video ID
def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

# Get transcript from YouTube
def extract_transcript_details(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([i["text"] for i in transcript])
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

# Generate summary using Gemini
def generate_gemini_content(transcript_text, word_limit, language):
    prompt = build_prompt(transcript_text, word_limit, language)
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

# UI Starts
st.set_page_config(page_title="YouTube Transcript AI", layout="centered")
st.title("\U0001F3AC YouTube Transcript AI Tool")

# Dark Mode Toggle
dark_mode = st.checkbox("🌙 Dark Mode", value=False)
set_theme(dark_mode)

with st.container():
    youtube_link = st.text_input("\U0001F4E5 Enter YouTube Video URL:")
    word_limit = st.selectbox("\U0001F5BE Summary Length:", [100, 250, 500], index=1)
    language = st.selectbox("\U0001F310 Summary Language:", ["English", "Hindi", "Spanish", "French", "German"], index=0)

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

summary = None

if st.button("\u26A1 Generate Summary"):
    with st.spinner("\u23F3 Working on it..."):
        video_id = extract_video_id(youtube_link)
        transcript = extract_transcript_details(video_id)

        if transcript:
            summary = generate_gemini_content(transcript, word_limit, language)
            st.success("\u2705 Summary generated!")
            st.markdown("## \U0001F4DD Summary")
            st.text_area("Editable Summary", summary, height=300)

            # Download button
            st.download_button("\U0001F4E5 Download Summary", summary, file_name="video_summary.txt")
        else:
            st.error("\u26A0\uFE0F Transcript not available for this video.")
