from flask import Flask, render_template, request, jsonify
import openai
import os
import logging
import feedparser
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Set up logging.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    logger.warning("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")
else:
    logger.info(f"OpenAI API key loaded. Key starts with: {openai.api_key[:5]}...")

RSS_FEED_URL = "https://www.parl.ca/legisinfo/en/bills/rss"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_bills')
def get_bills():
    feed = feedparser.parse(RSS_FEED_URL)
    bills = []
    for entry in feed.entries:
        bills.append({
            'title': entry.title,
            'link': entry.link,
            'description': entry.description
        })
    return jsonify(bills)

@app.route('/analyze_bill', methods=['POST'])
def analyze_bill():
    bill_url = request.json.get('bill_url')
    if not bill_url:
        return jsonify({'error': 'No bill URL provided'})
    
    try:
        bill_text = fetch_bill_text(bill_url)
        analysis = analyze_legislation(bill_text)
        return jsonify({'analysis': analysis})
    except Exception as e:
        logger.error(f"Error analyzing bill {bill_url}: {str(e)}")
        return jsonify({'error': 'An error occurred while analyzing the bill. Please try again'})

def fetch_bill_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Try to find the bill text in various possible locations
    bill_text = None
    possible_containers = [
        soup.find('div', class_='BillTextContainer'),
        soup.find('div', id='billTextContainer'),
        soup.find('div', class_='BillText'),
        soup.find('pre', class_='BillTextPre')
    ]
    for container in possible_containers:
        if container:
            bill_text = container.get_text(strip=True)
            break
    
    if not bill_text:
        # If we couldn't find the bill text, get all the text from the page
        bill_text = soup.get_text(strip=True)
    
    return bill_text

def analyze_legislation(text):
    if not openai.api_key:
        logger.error("OpenAI API key is not set.")
        return "Error: OpenAI API key is not set. Please contact the administrator."

    # Truncate the text if it's too long
    max_text_length = 3000  # Adjust this value as needed
    truncated_text = text[:max_text_length] + ("..." if len(text) > max_text_length else "")

    prompt = f"Analyze the following government legislation and explain the key changes. If the text appears to be truncated, focus on analyzing the available content:\n\n{truncated_text}"
    
    try:
        logger.info("Calling OpenAI API for analysis")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in analyzing government legislation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500  # Limit the response length
        )
        logger.info("OpenAI API call successful")
        return response.choices[0].message['content']
    except openai.error.AuthenticationError as e:
        logger.error(f"OpenAI API authentication error: {str(e)}")
        return "Error: Unable to authenticate with the AI service. Please try again later or contact support."
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return "Error: An issue occurred with the AI analysis. Please try again later."
    except Exception as e:
        logger.error(f"Unexpected error during OpenAI API call: {str(e)}")
        return "An unexpected error occurred. Please try again later or contact support."

if __name__ == '__main__':
    app.run(debug=True)
