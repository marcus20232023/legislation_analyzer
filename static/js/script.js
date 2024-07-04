document.addEventListener('DOMContentLoaded', () => {
    // Initialize Materialize components
    M.AutoInit();

    const billSelect = document.getElementById('bill-select');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const analysisText = document.getElementById('analysis-text');

    // Fetch bills and populate the dropdown
    fetchBills();

    analyzeBtn.addEventListener('click', analyzeBill);

    async function fetchBills() {
        try {
            const response = await fetch('/get_bills');
            const bills = await response.json();

            bills.forEach(bill => {
                const option = document.createElement('option');
                option.value = bill.url;
                option.textContent = bill.title;
                billSelect.appendChild(option);
            });

            // Reinitialize Materialize select
            M.FormSelect.init(billSelect);
        } catch (error) {
            console.error('Error fetching bills:', error);
            M.toast({html: 'Error fetching bills. Please try again later.', classes: 'red'});
        }
    }

    async function analyzeBill() {
        const selectedBillUrl = billSelect.value;
        if (!selectedBillUrl) {
            M.toast({html: 'Please select a bill to analyze', classes: 'red'});
            return;
        }

        loading.classList.remove('hidden');
        result.classList.add('hidden');

        try {
            const response = await fetch('/analyze_bill', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ bill_url: selectedBillUrl }),
            });

            const data = await response.json();

            if (data.error) {
                M.toast({html: data.error, classes: 'red'});
            } else {
                analysisText.textContent = data.analysis;
                result.classList.remove('hidden');
                M.toast({html: 'Analysis complete!', classes: 'green'});
            }
        } catch (error) {
            console.error('Error:', error);
            M.toast({html: 'An error occurred while analyzing the legislation', classes: 'red'});
        } finally {
            loading.classList.add('hidden');
        }
    }
});
