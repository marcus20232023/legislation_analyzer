from flask import Flask, request, render_template
import openai
import logging
import requests
from io import BytesIO
from PyPDF2 import PdfReader

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    analysis_result = None
    if request.method == 'POST':
        pdf_url = request.form['pdf_url']
        api_key = request.form['api_key']
        api_model = request.form['api_model']
        # Fetch and process the PDF text here
        text = fetch_pdf_text(pdf_url)
        analysis_result = analyze_bill_text(text, api_key, api_model)
    return render_template('index.html', analysis_result=analysis_result)

def fetch_pdf_text(pdf_url):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        pdf_file = BytesIO(response.content)
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"Error fetching or processing PDF: {str(e)}")
        return ""

def analyze_bill_text(text, api_key, api_model):
    try:
        if api_model == 'gpt-4':
            response = openai.ChatCompletion.create(
                api_key=api_key,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Please analyze the following bill text and provide a summary, key points, and potential impacts:\n\n{text[:8000]}"}
                ],
                max_tokens=1000
            )
            analysis_content = response.choices[0].message['content']
        elif api_model == 'claude-3-5-sonnet-20240620':
            client = anthropic.Anthropic(api_key=api_key)
            response = client.Completion.create(
                model="claude-3-5-sonnet-20240620",
                prompt=f"Please analyze the following bill text and provide a summary, key points, and potential impacts:\n\n{text[:8000]}",
                max_tokens=1000
            )
            analysis_content = response.choices[0].text
        else:
            return "Invalid API model selected"

        logger.info(f"Received analysis: {analysis_content}")
        return analysis_content
    except Exception as e:
        logger.error(f"Error in API call: {str(e)}")
        return f"Error in analysis: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)