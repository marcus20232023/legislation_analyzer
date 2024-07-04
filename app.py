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
    match = re.search(r'/(\d+-\d+)/([A-Z]-\d+)', url)
    if not match:
        return {"error": "Unable to extract bill information from URL"}
    
    session, bill_number = match.groups()
    
    # Construct the correct PDF URL
    document_viewer_url = f"https://www.parl.ca/Content/Bills/{session}/Government/{bill_number}/{bill_number}_1/{bill_number}_1.PDF"
    
    try:
        logger.info(f"Fetching DocumentViewer page: {document_viewer_url}")
        response = requests.get(document_viewer_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for the PDF link
        pdf_link = soup.find('a', href=re.compile(r'.*\.pdf$', re.IGNORECASE))
        
        if pdf_link:
            pdf_url = pdf_link['href']
            if not pdf_url.startswith('http'):
                pdf_url = 'https://www.parl.ca' + pdf_url
            
            logger.info(f"PDF link found: {pdf_url}")
            
            # Fetch and process the PDF
            pdf_response = requests.get(pdf_url, headers=headers)
            pdf_response.raise_for_status()
            
            pdf_file = io.BytesIO(pdf_response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        else:
            logger.warning("No PDF link found. Extracting text from HTML.")
            # If no PDF link is found, extract text from the HTML
            main_content = soup.find('div', id='publicationContent')
            if main_content:
                text = main_content.get_text(strip=True)
            else:
                text = soup.get_text(strip=True)
        
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
