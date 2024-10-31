import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

load_dotenv()  # Load all the environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video, providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """

# Getting the transcript data from YouTube videos
def extract_transcript_details(youtube_video_url, language='en'):
    try:
        video_id = youtube_video_url.split("v=")[1].split("&")[0]  # Support different formats
        
        # Get the transcript for the specified language
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except NoTranscriptFound:
        available_languages = YouTubeTranscriptApi.list_transcripts(video_id)
        available_langs = [transcript.language for transcript in available_languages]
        st.error(f"No transcripts found for the requested language: {language}. Available languages: {available_langs}.")
        return None
    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
        return None
    except VideoUnavailable:
        st.error("The requested video is unavailable.")
        return None
    except Exception as e:
        st.error(f"Error fetching transcript: {str(e)}")
        return None

# Getting the summary based on the prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Streamlit app
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")
language = st.selectbox("Select Transcript Language:", ["en", "hi", "es", "fr", "de", "pt"])  # Add more languages as needed

if youtube_link:
    try:
        video_id = youtube_link.split("v=")[1].split("&")[0]  # Handle different URL formats
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except IndexError:
        st.error("Invalid YouTube link. Please make sure it is formatted correctly.")

if st.button("Get Detailed Notes"):
    if youtube_link:
        transcript_text = extract_transcript_details(youtube_link, language)

        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("## Detailed Notes:")
            st.write(summary)
        else:
            st.error("Could not generate summary. Please check the transcript.")
    else:
        st.error("Please enter a valid YouTube link.")
