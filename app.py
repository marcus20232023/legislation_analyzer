import re
import requests
from bs4 import BeautifulSoup
import logging
from functools import lru_cache
import io
import PyPDF2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ... (keep the rest of the imports and setup)

@lru_cache(maxsize=100)
def fetch_bill_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Extract bill number and session from the URL
    match = re.search(r'/bill/(\d+-\d+)/([A-Z]-\d+)', url)
    if not match:
        return {"error": "Unable to extract bill information from URL"}
    
    session, bill_number = match.groups()
    
    # Construct the correct DocumentViewer URL
    document_viewer_url = f"https://www.parl.ca/DocumentViewer/en/{session}/bill/{bill_number}/first-reading"
    
    try:
        logger.info(f"Fetching DocumentViewer page: {document_viewer_url}")
        response = requests.get(document_viewer_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Directly construct the PDF URL
        pdf_url = f"https://www.parl.ca/Content/Bills/{session}/Government/{bill_number}/{bill_number}_1/{bill_number}_1.PDF"
        
        logger.info(f"PDF link constructed: {pdf_url}")
        
        # Fetch and process the PDF
        pdf_response = requests.get(pdf_url, headers=headers)
        pdf_response.raise_for_status()
        
        pdf_file = io.BytesIO(pdf_response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        if text.strip():
            logger.info("Successfully extracted bill text")
            return {"text": text, "url": pdf_url if pdf_link else document_viewer_url}
        else:
            logger.warning("No text content found")
            return {"error": "No text content found in the bill"}
        
    except requests.exceptions.RequestException as err:
        logger.error(f"Error fetching bill text: {str(err)}")
        return {"error": f"Failed to fetch bill text: {str(err)}"}

# ... (keep the rest of the file unchanged)
