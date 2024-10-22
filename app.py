import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable

# Load environment variables
load_dotenv()

# Configure Google Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the summarization prompt
prompt = """You are a YouTube video summarizer. You will take the transcript text 
and summarize the entire video, providing the important points in 250 words or less. 
Please provide the summary of the text given here: """

# Function to extract transcript details from YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        
        # Fetch transcript using YouTubeTranscriptApi
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine transcript text into one string
        transcript = " ".join([i["text"] for i in transcript_text])

        return transcript

    except TranscriptsDisabled:
        # Handle if transcripts are disabled for the video
        return "Transcripts are disabled for this video. Please try another video."
    except VideoUnavailable:
        # Handle if video is unavailable or private
        return "This video is unavailable or private. Please check the link."
    except Exception as e:
        # Generic error handling
        return f"An error occurred: {str(e)}"

# Function to generate content using Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    try:
        # Use the Gemini API to generate content
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        # Handle API errors
        return f"An error occurred while generating the summary: {str(e)}"

# Streamlit app interface
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    # Extract the video ID and display a thumbnail
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    # Fetch transcript details
    transcript_text = extract_transcript_details(youtube_link)

    if "An error occurred" in transcript_text or "Transcripts are disabled" in transcript_text:
        st.error(transcript_text)
    else:
        # Generate the summary using the Gemini API
        summary = generate_gemini_content(transcript_text, prompt)
        
        st.markdown("## Detailed Notes:")
        st.write(summary)
