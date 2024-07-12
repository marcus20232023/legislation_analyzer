from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import anthropic
import requests
import io
from PyPDF2 import PdfReader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    api_key = request.form['api_key']
    api_model = request.form['api_model']
    pdf_url = request.form.get('pdf_url')
    pdf_file = request.files.get('pdf_file')

    if pdf_url:
        bill_data = fetch_bill_text_from_url(pdf_url)
    elif pdf_file:
        bill_data = fetch_bill_text_from_file(pdf_file)
    else:
        return jsonify({"error": "No PDF URL or file provided"})

    if "error" in bill_data:
        return jsonify({"error": bill_data["error"]})

    bill_text = bill_data["text"]
    analysis = analyze_bill_text(bill_text, api_key, api_model)
    
    return jsonify({"analysis": analysis})

def fetch_bill_text_from_url(pdf_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        logger.info(f"Fetching PDF from: {pdf_url}")
        response = requests.get(pdf_url, headers=headers)
        response.raise_for_status()
        
        pdf_file = io.BytesIO(response.content)
        return extract_text_from_pdf(pdf_file)
        
    except requests.exceptions.RequestException as err:
        logger.error(f"Error fetching PDF: {str(err)}")
        return {"error": f"Failed to fetch PDF: {str(err)}"}

def fetch_bill_text_from_file(pdf_file):
    try:
        return extract_text_from_pdf(pdf_file)
    except Exception as err:
        logger.error(f"Error processing uploaded PDF: {str(err)}")
        return {"error": f"Failed to process uploaded PDF: {str(err)}"}

def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    if text.strip():
        logger.info("Successfully extracted bill text")
        return {"text": text}
    else:
        logger.warning("No text content found")
        return {"error": "No text content found in the PDF"}

def analyze_bill_text(text, api_key, api_model):
    try:
        if api_model == 'gpt-4':
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes legislative bills."},
                    {"role": "user", "content": f"Please analyze the following bill text and provide a summary, key points, and potential impacts:\n\n{text[:8000]}"}
                ]
            )
            analysis_content = response.choices[0].message.content
        elif api_model == 'claude-3.5':
            client = anthropic.Anthropic(api_key=api_key)
            response = client.completions.create(
                model="claude-3.5",
                prompt=f"Human: Please analyze the following bill text and provide a summary, key points, and potential impacts:\n\n{text[:8000]}\n\nAssistant:",
                max_tokens_to_sample=1000
            )
            analysis_content = response.completion
        else:
            return "Invalid API model selected"

        logger.info(f"Received analysis: {analysis_content}")
        return analysis_content
    except Exception as e:
        logger.error(f"Error in API call: {str(e)}")
        return f"Error in analysis: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
