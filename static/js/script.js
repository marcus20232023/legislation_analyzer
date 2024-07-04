document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const billsDropdown = document.getElementById('bills-dropdown');
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
                    const option = document.createElement('option');
                    option.value = bill.link;
                    option.textContent = `${bill.id}: ${bill.title}`;
                    billsDropdown.appendChild(option);
                });
            }
        } catch (error) {
            M.toast({html: 'An error occurred while fetching bills', classes: 'red'});
        }
    }

    fetchBills();

    billsDropdown.addEventListener('change', function() {
        pdfUrlInput.value = this.value;
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
