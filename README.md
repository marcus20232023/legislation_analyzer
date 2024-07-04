# Legislation Analyzer

This web application analyzes government legislation PDFs using AI (OpenAI's GPT-3.5) to explain key changes.

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/legislation_analyzer.git
   cd legislation_analyzer
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY='your-openai-api-key'
   ```
   On Windows, use:
   ```
   set OPENAI_API_KEY=your-openai-api-key
   ```
   Replace 'your-openai-api-key' with your actual OpenAI API key.

## Running the Application

1. Start the Flask server:
   ```
   python app.py
   ```

2. Open a web browser and go to `http://localhost:5000`

3. Upload a PDF file of government legislation and click "Analyze Legislation"

## Features

- Upload PDF files of government legislation (max 16MB)
- Analyze the content using AI to explain key changes
- Display the analysis results on the web page
- Secure file handling and automatic cleanup after processing

## Technologies Used

- Backend: Python, Flask
- Frontend: HTML, CSS, JavaScript
- PDF Processing: PyPDF2
- AI Analysis: OpenAI GPT-3.5

## Security Notes

- The application uses environment variables for API key management
- Uploaded files are temporarily stored and then deleted after processing
- File size is limited to 16MB to prevent potential issues with large PDFs

## Troubleshooting

If you encounter any issues, check the application logs for error messages. The application uses logging to help with debugging and monitoring.

## Note

This application uses the OpenAI API, which may incur costs. Make sure you understand the pricing and set up appropriate usage limits in your OpenAI account.

## License

This project is open source and available under the [MIT License](LICENSE).# bill_reader
