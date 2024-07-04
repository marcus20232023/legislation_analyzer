document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const billsList = document.getElementById('bills');
    const pdfUrlInput = document.getElementById('pdf-url');
    const loadingIndicator = document.getElementById('loading');
    const analysisResult = document.getElementById('analysis-result');

    async function fetchBills() {
        try {
            const response = await fetch('/bills');
            const bills = await response.json();
            if (bills.error) {
                M.toast({html: bills.error, classes: 'red'});
            } else {
                bills.forEach(bill => {
                    const li = document.createElement('li');
                    const a = document.createElement('a');
                    a.href = bill.link;
                    a.textContent = `${bill.id}: ${bill.title}`;
                    a.target = "_blank";
                    li.appendChild(a);
                    billsList.appendChild(li);
                });
            }
        } catch (error) {
            M.toast({html: 'An error occurred while fetching bills', classes: 'red'});
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        fetchBills();
    });

    analyzeBtn.addEventListener('click', async function() {
        const pdfUrl = pdfUrlInput.value.trim();
        if (!pdfUrl) {
            M.toast({html: 'Please enter a PDF URL', classes: 'red'});
            return;
        }

        loadingIndicator.classList.remove('hidden');
        analysisResult.innerHTML = '';

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ pdf_url: pdfUrl })
            });

            const data = await response.json();
            if (data.error) {
                M.toast({html: data.error, classes: 'red'});
            } else {
                analysisResult.innerHTML = `<p>${data.analysis}</p>`;
            }
        } catch (error) {
            M.toast({html: 'An error occurred while analyzing the PDF', classes: 'red'});
        } finally {
            loadingIndicator.classList.add('hidden');
        }
    });
});
