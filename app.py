import io
import logging
import requests
from  PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, jsonify, url_for
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bills', methods=['GET'])
def get_bills():
    url = "https://www.parl.ca/legisinfo/en/bills/rss"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch bills data"}), 500

    bills = []
    root = ET.fromstring(response.content)
    for item in root.findall('.//item'):
        title = item.find('title').text
        link = item.find('link').text
        bill_id = link.split('/')[-1].split('_')[0]  # Extract bill ID from the link
        bills.append({"id": bill_id, "title": title, "link": link})

    return jsonify(bills)

@app.route('/analyze', methods=['POST'])
def analyze():
    pdf_url = request.json['pdf_url']
    bill_data = fetch_bill_text(pdf_url)
    
    if "error" in bill_data:
        return jsonify({"error": bill_data["error"]})

    bill_text = bill_data["text"]
    analysis = analyze_bill_text(bill_text)
    
    return jsonify({"analysis": analysis})

def fetch_bill_text(pdf_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        logger.info(f"Fetching PDF from: {pdf_url}")
        response = requests.get(pdf_url, headers=headers)
        response.raise_for_status()
        
        pdf_file = io.BytesIO(response.content)
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        if text.strip():
            logger.info("Successfully extracted bill text")
            return {"text": text, "url": pdf_url}
        else:
            logger.warning("No text content found")
            return {"error": "No text content found in the PDF"}
        
    except requests.exceptions.RequestException as err:
        logger.error(f"Error fetching PDF: {str(err)}")
        return {"error": f"Failed to fetch PDF: {str(err)}"}

def analyze_bill_text(text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes legislative bills."},
                {"role": "user", "content": f"Please analyze the following bill text and provide a summary, key points, and potential impacts:\n\n{text[:4000]}"}  # Limiting to 4000 characters for this example
            ]
        )
        analysis_content = response.choices[0].message.content
        logger.info(f"Received analysis: {analysis_content}")
        return analysis_content
    except Exception as e:
        logger.error(f"Error in OpenAI API call: {str(e)}")
        return f"Error in analysis: {str(e)}"

def main(pdf_url):
    bill_data = fetch_bill_text(pdf_url)
    
    if "error" in bill_data:
        print(f"Error: {bill_data['error']}")
        return

    bill_text = bill_data["text"]
    analysis = analyze_bill_text(bill_text)
    
    print("Bill Analysis:")
    print(analysis)

if __name__ == "__main__":
    app.run(debug=True)
