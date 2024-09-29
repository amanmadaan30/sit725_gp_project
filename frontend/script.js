// frontend/script.js

const API_URL = 'http://127.0.0.1:5000';

function showCodeInput() {
    document.getElementById('codeSection').style.display = 'block';
}

function analyzeCode() {
    const code = document.getElementById('codeInput').value;

    fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('issuesOutput').innerText = data.issues.join('\n');
    })
    .catch(error => console.error('Error analyzing code:', error));
}

function refactorCode() {
    const code = document.getElementById('codeInput').value;

    fetch(`${API_URL}/refactor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('refactoredOutput').innerText = data.refactored_code;
    })
    .catch(error => console.error('Error refactoring code:', error));
}
