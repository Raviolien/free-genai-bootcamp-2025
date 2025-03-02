# Listening learning app

## Business goal
Create a listening learning app that mimics the listening comprehension tests in the acutal language exam.

## Technical requirements
- (Optional) Speech to Text, (ASR) Transcribe. eg Amazon Transcribe. OpenWhisper
- Youtube Transcript API (Download Transcript from Youtube)
- LLM + Tool Use “Agent”
- chromadb, Sqlite3 - Knowledge Base 
- Text to Speech (TTS) eg. Amazon Polly
- AI Coding Assistant: eg. Amazon Developer Q, Windsurf, Cursor, Github Copilot
- Frontend eg. Streamlit.
- Guardrails

## Technical description / building blocks
- Get transcript: Use Youtube Transcript API to download the tran transcript from a given Youtube URL
- Analyse transcript: Use LLM to analyse the transcript and get the relevant parts (i.e. filter out stuff that are not the questions)
- Structure the transcript in to a database: Use chromadb for storage
- Generate questions (text): Use LLM to generate questions and answers based on the transcript
- Generate questions (audio): Use LLM to generate questions and answers based on the transcript

## Technical uncertainty
- Build from scratch the backend
- Build from scratch the frontend
- How much does Amazon cost?

## Findings
- Difficult to actually fine good youtube videos, most of them don't read aloud the full text together with answers, so llm end up treating them as two different exercises. 
- Further work: create images & describe them in the transcript, so we can do dialog matching exercises

### @ technical uncertainly
- Build from scratch the backend: Completed this and it can be run in the terminal, not as difficult as I thought, utilizaed AI assistant (Cursor)
- Build from scratch the frontend: This was the most time consuming part. Struggles with error messages with Torch, getting the wanted UI and to make it generate the audio. Workaround for Torch: doing an empty path. For audio Cursor put the generation in a function for displaying the exercise, needed to be moved to main() where the exercise is created
- AWS cost: No that expensive for this use case

## How to run
### Create and acitvate virtual environment
python3 -m venv venv
source venv/bin/activate

### Install dependencies
pip install -r requirements.txt

## How to run
 Follow these steps to run 

### Run backend files to set up vector store
python get_transcript.py
python process_transcripts.py    
python vector_store.py

### Run frontend
streamlit run app.py

### To test backend 
python create_restaurant_mc_exercise.py

## Other
https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/python