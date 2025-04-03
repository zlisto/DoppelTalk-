import os
import openai
import json
import pandas as pd
import base64
import requests
import time
import PyPDF2
from docx import Document
import re
from bs4 import BeautifulSoup



class GenAI:
    """
    A class for interacting with the OpenAI API to generate text, images, video descriptions,
    perform speech recognition, and handle basic document processing tasks.

    Attributes:
    ----------
    client : openai.Client
        An instance of the OpenAI client initialized with the API key.
    """
    def __init__(self, openai_api_key):
        """
        Initializes the GenAI class with the provided OpenAI API key.

        Parameters:
        ----------
        openai_api_key : str
            The API key for accessing OpenAI's services.
        """
        self.client = openai.Client(api_key=openai_api_key)
        self.openai_api_key = openai_api_key

    def generate_text(self, prompt, instructions='You are a helpful AI named Jarvis', model="gpt-4o-mini", output_type='text', temperature =1):
        """
        Generates a text completion using the OpenAI API.

        This function sends a prompt to the OpenAI API with optional instructions to guide the AI's behavior. 
        It supports specifying the model and output format, and returns the generated text response.

        Parameters:
        ----------
        prompt : str
            The user input or query that you want the AI to respond to.
        
        instructions : str, optional (default='You are a helpful AI named Jarvis')
            System-level instructions to define the AI's behavior, tone, or style in the response.
        
        model : str, optional (default='gpt-4o-mini')
            The OpenAI model to use for generating the response. You can specify different models like 'gpt-4', 'gpt-3.5-turbo', etc.
        
        output_type : str, optional (default='text')
            The format of the output. Typically 'text', but can be customized for models that support different response formats.

        Returns:
        -------
        str
            The AI-generated response as a string based on the provided prompt and instructions.

        Example:
        -------
        >>> response = generate_text("What's the weather like today?")
        >>> print(response)
        "The weather today is sunny with a high of 75°F."
        """
        completion = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            response_format={"type": output_type},
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt}
            ]
        )
        response = completion.choices[0].message.content
        response = response.replace("```html", "")
        response = response.replace("```", "")
        return response


    def generate_chat_response(self,    
                                chat_history,                          
                               instructions, 
                               model="gpt-4o-mini", 
                               output_type='text'):
        """
        Generates a chatbot-like response based on the conversation history.

        Parameters:
        ----------
        chat_history : list
            List of previous messages, each as a dict with "role" and "content".
        user_message : str
            The latest message from the user.
        instructions : str
            System instructions defining the chatbot's behavior.
        model : str, optional
            The OpenAI model to use (default is 'gpt-4o-mini').
        output_type : str, optional
            The format of the output (default is 'text').

        Returns:
        -------
        str
            The chatbot's response.
        """
        # Add the latest user message to the chat history
        #chat_history.append({"role": "user", "content": user_message})

        # Call the OpenAI API to get a response
        completion = self.client.chat.completions.create(
            model=model,
            response_format={"type": output_type},
            messages=[
                {"role": "system", "content": instructions},  # Add system instructions
                *chat_history  # Unpack the chat history to include all previous messages
            ]
        )

        # Extract the bot's response from the API completion
        response = completion.choices[0].message.content

        return response


    def generate_image(self, prompt, model="dall-e-3", size="1024x1024", quality="standard", n=1):
        """
        Generates an image from a text prompt using the OpenAI DALL-E API.

        Parameters:
        ----------
        prompt : str
            The description of the image to generate. This text guides the AI to create an image
            based on the provided details.
        model : str, optional
            The OpenAI model to use for image generation. Defaults to 'dall-e-3'.
        size : str, optional
            The desired dimensions of the generated image. Defaults to '1024x1024'.
            Supported sizes may vary depending on the model.
        quality : str, optional
            The quality of the generated image, such as 'standard' or 'high'. Defaults to 'standard'.
        n : int, optional
            The number of images to generate. Defaults to 1.

        Returns:
        -------
        tuple
            A tuple containing:
            - image_url (str): The URL of the generated image.
            - revised_prompt (str): The prompt as modified by the model, if applicable.

        Notes:
        -----
        This function introduces a short delay (`time.sleep(1)`) to ensure proper API response handling.
        """
        response_img = self.client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
        )
        time.sleep(1)
        image_url = response_img.data[0].url
        revised_prompt = response_img.data[0].revised_prompt

        return image_url, revised_prompt

    

    def encode_image(self,image_path):
        """
        Encodes an image file into a base64 string.

        Parameters:
        ----------
        image_path : str
            The path to the image file.

        Returns:
        -------
        str
            Base64-encoded image string.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_image_description(self, image_paths, instructions, model = 'gpt-4o-mini'):
        """
        Generates a description for one or more images using OpenAI's vision capabilities.

        Parameters:
        ----------
        image_paths : str or list
            Path(s) to the image file(s).
        instructions : str
            Instructions for the description.
        model : str, optional
            The OpenAI model to use (default is 'gpt-4o-mini').

        Returns:
        -------
        str
            A textual description of the image(s).
        """
        if isinstance(image_paths, str):
            image_paths = [image_paths]

        image_urls = [f"data:image/jpeg;base64,{self.encode_image(image_path)}" for image_path in image_paths]

        PROMPT_MESSAGES = [
            {
                "role": "user",
                "content": [{"type": "text", "text": instructions},
                            *map(lambda x: {"type": "image_url", "image_url": {"url": x}}, image_urls),
                            ],
            },
        ]
        params = {
            "model": model,
            "messages": PROMPT_MESSAGES,
            "max_tokens": 1000,
        }

        completion = self.client.chat.completions.create(**params)
        response = completion.choices[0].message.content
        response = response.replace("```html", "")
        response = response.replace("```", "")
        return response

    def read_pdf(self,file_path):
        # Open the PDF file
        with open(file_path, 'rb') as file:
            # Initialize the PDF reader
            reader = PyPDF2.PdfReader(file)
            
            # Initialize an empty string to store the text
            text = ""
            
            # Iterate through each page in the PDF
            for page in reader.pages:
                # Extract the text from the page and add it to the text string
                text += page.extract_text()
            
        return text



    def read_docx(self,file_path):
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)

