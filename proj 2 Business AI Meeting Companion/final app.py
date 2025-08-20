import torch
from transformers import pipeline
import gradio as gr
from google import genai
import os
from dotenv import load_dotenv



# Requirements
# Python 3.9–3.11
# pip install transformers==4.36.0 gradio==5.23.2 langchain==0.0.343 ibm_watson_machine_learning==1.0.335 huggingface-hub==0.28.1
# pip install git+https://github.com/openai/whisper.git   # for OpenAI Whisper
# ffmpeg is required to load/process audio files (install separately)


# ---------------------------
# Gemini API Setup
# ---------------------------
# STEP 1: Get an API key from https://aistudio.google.com/
# STEP 2: Set it as an environment variable for security:
#   Linux/Mac: export GEMINI_API_KEY="your_api_key_here"
#   Windows (PowerShell): setx GEMINI_API_KEY "your_api_key_here"

load_dotenv() # load env variables
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it as an environment variable.")

# Initialize Gemini client
client = genai.Client(api_key=api_key)

# ---------------------------
# Automatic Speech Recognition (Whisper)
# ---------------------------
# Using Hugging Face pipeline with OpenAI Whisper (tiny English model)
# It transcribes speech to text in chunks (30 seconds each)
pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny.en",
    chunk_length_s=30,
)


# ---------------------------
# Transcription + Summarization
# ---------------------------
def transcript_audio(audio_file):
    """
    1. Takes an uploaded audio file
    2. Transcribes speech into text using Whisper
    3. Sends transcription to Gemini to extract concise key points
    4. Saves results to a text file and returns them
    """
    try:
        # Step 1: Transcribe audio
        result = pipe(audio_file, batch_size=8)["text"]

        # Step 2: Prepare summarization prompt for Gemini
        prompt = (
            "Extract the key points from the following transcription in a clear, "
            "concise bullet list, making it 1/3rd of the original text:\n\n"
            f"{result}"
        )

        # Step 3: Generate summary with Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        # Step 4: Combine results
        full_output = f"Transcription: \n{result}\n\nKey Points: \n{response.text.strip()}"
        file_path = "Summary.txt"

        # Save to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_output)

        return full_output, file_path

    except Exception as e:
        return f"Exception occurred: {e}"


# ---------------------------
# Gradio Web Interface
# ---------------------------
audio_input = gr.Audio(sources="upload", type="filepath")
output = [
    gr.Textbox(label="Transcription and Summary"),
    gr.File(label="Download File")
]

iface = gr.Interface(
    fn=transcript_audio,
    inputs=audio_input,
    outputs=output,
    title="Audio Transcription + Key Points Extractor",
    description="Upload an audio file. The app will transcribe it and summarize the key points using Gemini."
)

iface.launch(server_name="127.0.0.1", server_port=3000)
