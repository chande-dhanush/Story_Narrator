import time
from flask import Flask, request, jsonify, render_template
import os
import torch
from gtts import gTTS
from diffusers import StableDiffusionPipeline
from langchain_google_genai import ChatGoogleGenerativeAI
import datetime

app = Flask(__name__)

# Set up API Key for Google Gemini and Hugging Face
os.environ["GOOGLE_API_KEY"] = 'Enter google API'
os.environ["HF_TOKEN"] = 'Enter hugging face api'

# Initialize the Google Gemini LLM (Language Model)
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    max_tokens=None,
    timeout=None,
    max_retries=2,
    handle_parsing_errors=True,
    temperature=0.7,
)

# Load the image generation model
image_gen_model = StableDiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2", torch_dtype=torch.float16, revision="fp16", use_auth_token=os.environ["HF_TOKEN"]
)
image_gen_model = image_gen_model.to("cuda" if torch.cuda.is_available() else "cpu")

# Global memory to keep track of the conversation context and style
memory = []
initial_prompt = None
first_output_generated = False
style_context = {}  # To store genre and related for style consistency

# Function to generate an image based on a summary prompt
def generate_image(prompt):
    image = image_gen_model(prompt, num_inference_steps=35, guidance_scale=9).images[0]
    image = image.resize((400, 400))
    image.save("static/story_image.png")
    return "static/story_image.png"

# Function to generate audio from text using gTTS
def generate_audio(text):
    tts = gTTS(text=text, lang='en')
    filename = "static/audio_output.mp3"
    tts.save(filename)
    return filename

# Function to get an image-specific summary from the LLM
def generate_image_summary(story):
    
    summary_prompt = f'''Maintain a realistic artstyle,
    Summarize the following story in a concise and vivid manner, 
    extracting most of the key points, specifically for generating an image: {story}
    compress the prompt to 50 words at max'''
    
    summary_response = llm.invoke(summary_prompt).content
    return summary_response

# Function to process user input with the Google Gemini model
def process_input(user_input):
    global memory, first_output_generated
    if not first_output_generated:
        # Start the conversation with the initial prompt and generate the first response
        response = llm.invoke(user_input).content
        first_output_generated = True
        # Save the initial prompt and response to memory
        memory.append({"user": user_input, "bot": response})
    else:
        # Retrieve the entire conversation context
        full_context = "\n".join([f"User: {entry['user']}\nBot: {entry['bot']}" for entry in memory])
        # Append the current user input to the conversation
        conversation_input = f"{full_context}\nUser: {user_input}"
        response = llm.invoke(conversation_input).content
        
        # Add the response to the memory
        memory.append({"user": user_input, "bot": response})
    
    # Format actions to appear on the next line
    response = response.replace("actions:", "\nactions:\n")
    return response


@app.route('/')
def home():
    return render_template('index.html')

import re
import re

import re

@app.route('/generate', methods=['POST'])
def chat_story():
    global initial_prompt, style_context
    data = request.json
    user = data.get('user')
    genre = data.get('genre')
    tone = data.get('tone')
    characters = data.get('characters')
    skills = data.get('skills')
    related = data.get('related')

    # Save genre and related for consistent styling in images
    style_context["genre"] = genre
    style_context["related"] = related

    initial_prompt = f'''You're a very creative and flexible author writing an immersive story with detailed screenplay and descriptions. The user wants
    to play a role of {user} of a {genre} genre story with a {tone} tone and the characters: {characters}. The characters have the special skills: {skills}.
    The story should be somewhat similar to the movie or anime: {related}.

    Start the story by describing the scene or the environment in which the characters are present in a detailed and imaginative manner and
    give the users a set of actions or options to choose from so that they continue or progress through the story. Use the next line at the end of each statement so that it looks neat.
    Try to limit each response to two paragraphs maximum so that it doesn't get too boring. Also try to maintain continuity in the story after every user response.
    
    Make sure you provide sufficient space and newline characters before giving the actions or options for the user to choose.
    '''

    # Generate story
    story = process_input(initial_prompt)

    
    # Regular expression for all variations of "actions" and "options"
    pattern = r'(\[?\s*(actions|options)\s*:?]?\s*:)'
    story = story.replace('*','')
    # Replace all matches with properly formatted text
    story = re.sub(pattern, lambda m: f"\n\n{m.group(2).lower()}:\n", story, flags=re.IGNORECASE)

    # Generate an image-specific summary using the LLM
    image_summary = generate_image_summary(story)
    
    # Generate image based on the summary
    image_path = generate_image(image_summary)
    
    # Generate audio of the story
    audio_path = generate_audio(story)
    
    # Append a timestamp to the image and audio URLs for cache busting
    timestamp = datetime.datetime.now().timestamp()
    image_path_with_timestamp = f"{image_path}?v={timestamp}"
    audio_path_with_timestamp = f"{audio_path}?v={timestamp}"
    
    return jsonify({
        "story": story,
        "image_path": image_path_with_timestamp,
        "audio_path": audio_path_with_timestamp
    })



if __name__ == '__main__':
    app.run(debug=True)
