document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const pdfUrlInput = document.getElementById('pdf-url');
    const loadingDiv = document.getElementById('loading');
    const analysisResultDiv = document.getElementById('analysis-result');

    analyzeBtn.addEventListener('click', function() {
        const pdfUrl = pdfUrlInput.value.trim();
        if (!pdfUrl) {
            alert('Please enter a PDF URL');
            return;
        }

        loadingDiv.style.display = 'block';
        analysisResultDiv.style.display = 'none';

        fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ pdf_url: pdfUrl }),
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