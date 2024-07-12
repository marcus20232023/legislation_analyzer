document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const apiKeyInput = document.getElementById('api-key');
    const apiModelSelect = document.getElementById('api-model');
    const pdfUrlInput = document.getElementById('pdf-url');
    const pdfFileInput = document.getElementById('pdf-file');
    const loadingDiv = document.getElementById('loading');
    const analysisResultDiv = document.getElementById('analysis-result');
    const themeToggle = document.getElementById('theme-toggle');

    // Theme handling
    function setTheme(isDark) {
        document.body.classList.toggle('dark-theme', isDark);
        localStorage.setItem('darkTheme', isDark);
    }

    // Check for saved theme preference or use system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedTheme = localStorage.getItem('darkTheme');
    setTheme(savedTheme !== null ? savedTheme === 'true' : prefersDark);

    // Theme toggle button
    themeToggle.addEventListener('click', () => {
        setTheme(!document.body.classList.contains('dark-theme'));
    });

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        setTheme(e.matches);
    });

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
