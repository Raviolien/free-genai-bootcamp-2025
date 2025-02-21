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

## How to run
### Create and acitvate virtual environment
python3 -m venv venv
source venv/bin/activate

### Install dependencies
pip install -r requirements.txt

### Run backend
python backend.py
	

### Run frontend
streamlit run app.py


