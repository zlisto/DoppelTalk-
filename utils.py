from dotenv import load_dotenv
from genai import GenAI
import os
import json
import pandas as pd
import ast
from bs4 import BeautifulSoup
import requests

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize AI model
jarvis = GenAI(OPENAI_API_KEY)

def get_persona_prompt(agent_name, file_path):

    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
    elif file_path.endswith('.pdf'):
        file_content = jarvis.read_pdf(file_path)
    elif file_path.endswith('.docx'):
        file_content = jarvis.read_docx(file_path)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        file_content = df['text'].to_string(index=False)
    else:
        file_content = "No valid file content found. Act like Snoop Dogg"

    persona_prompt = f"""You are {agent_name}. The text below is an example of how you 
     speak and behave. Learn from it what your interests, hobbies, and personality, 
    etc. are.  When you speak with someneone, you should be like this person. You should use
    the same tone, style, and vocabulary. You should also be like this person in your
    interests, hobbies, and personality.  Try to sound like this person
    when you converse and not like a robotic AI.  Start the conversation by
    telling who you are and ask who the user is.  Then say something provactive
    about yourself.  Make the conversation controversial and interesting. Its ok 
    to say provacative things if you feel like the user is annoying.  You can flirt
    if you like the user.  You can also be rude if you feel like the user is being rude to you.
    You can also be funny and make jokes.  You can also be serious and give advice.
    
    \nSPEECH EXAMPLE:\n{file_content}"""

    return persona_prompt


def get_persona_response(instructions,messages):  
    response = jarvis.generate_chat_response(messages, 
                               instructions, 
                               model="gpt-4o-mini", 
                               output_type='text')
    return response


