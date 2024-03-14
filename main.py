import google.generativeai as genai
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import json
load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Nutrition Label Extraction API. Please use the /extract endpoint to extract values from nutrition labels."

@app.route('/extract', methods=['POST'])
def extract_values():
    # Check if 'image' is present in the request
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided in request'}), 400

    # getting image
    image_path = request.files['image']

    # system prompt
    system_prompt = """
               You are a specialist in comprehending nutrition labels.
               Input images in the form of nutrition labels will be provided to you,
               and your task is to respond answer in the json format to questions based on the content of the input image.
               """
    # user prompt
    user_prompt = "Extract the following value and answer in json format: calories, Total Fat, Cholesterol, Sodium, Total Carbohydrate, Protein, Total Sugars Dietary Fiber ?"
    
    # resut
    extracted_values = gemini_output(image_path, system_prompt, user_prompt)

    # result cleaning
    extracted_values = extracted_values.replace("\n", "")
    extracted_values = extracted_values.replace(" ", "")
    extracted_values = extracted_values.replace(":", ": ")
    extracted_values = extracted_values.replace(",", ", ")
    extracted_values = extracted_values.replace("{", "{ ")
    extracted_values = extracted_values.replace("}", " }")
    extracted_values = extracted_values.replace("`", "")
    extracted_values = extracted_values.replace("json", "")
    extracted_values = extracted_values.replace("\"", '"')

    # converting to json
    extracted_values = json.loads(extracted_values)

    # Respond with the extracted values in JSON format
    return extracted_values, 200


# main function
def gemini_output(image_path, system_prompt, user_prompt):

    image_info = image_format(image_path)
    input_prompt= [system_prompt, image_info[0], user_prompt]
    response = model.generate_content(input_prompt)
    return response.text

# model configuration
MODEL_CONFIG = {
"temperature": 0.2,
"top_p": 1,
"top_k": 32,
"max_output_tokens": 4096,
}

# safety settings
safety_settings = [
{
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
},
{
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
},
{
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
},
{
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
}
]

model = genai.GenerativeModel(model_name = "gemini-pro-vision",
                              generation_config = MODEL_CONFIG,
                              safety_settings = safety_settings)

# image function
from pathlib import Path

def image_format(image_object):
    image_bytes = image_object.read()
    image_parts = [
        {
            "mime_type": "image/jpeg",  # Adjust MIME type if necessary
            "data": image_bytes
        }
    ]
    return image_parts

    


if __name__ == '__main__':
    app.run(debug=True)
