document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const apiKeyInput = document.getElementById('api-key');
    const apiModelSelect = document.getElementById('api-model');
    const pdfUrlInput = document.getElementById('pdf-url');
    const pdfFileInput = document.getElementById('pdf-file');
    const loadingDiv = document.getElementById('loading');
    const analysisResultDiv = document.getElementById('analysis-result');

    analyzeBtn.addEventListener('click', function() {
        const apiKey = apiKeyInput.value.trim();
        const apiModel = apiModelSelect.value;
        const pdfUrl = pdfUrlInput.value.trim();
        const pdfFile = pdfFileInput.files[0];

        if (!apiKey) {
            alert('Please enter an API key');
            return;
        }

        if (!pdfUrl && !pdfFile) {
            alert('Please enter a PDF URL or upload a PDF file');
            return;
        }

        loadingDiv.style.display = 'block';
        analysisResultDiv.style.display = 'none';

        const formData = new FormData();
        formData.append('api_key', apiKey);
        formData.append('api_model', apiModel);
        
        if (pdfUrl) {
            formData.append('pdf_url', pdfUrl);
        } else {
            formData.append('pdf_file', pdfFile);
        }

        fetch('/analyze', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            loadingDiv.style.display = 'none';
            analysisResultDiv.style.display = 'block';
            if (data.error) {
                analysisResultDiv.textContent = `Error: ${data.error}`;
            } else {
                analysisResultDiv.textContent = data.analysis;
            }
        })
        .catch(error => {
            loadingDiv.style.display = 'none';
            analysisResultDiv.style.display = 'block';
            analysisResultDiv.textContent = `Error: ${error.message}`;
        });
    });
});
