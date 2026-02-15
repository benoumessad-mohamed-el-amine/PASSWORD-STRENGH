document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    const togglePassword = document.getElementById('togglePassword');
    const strengthMeterFill = document.getElementById('strengthMeterFill');
    const strengthText = document.getElementById('strengthText');
    const resultsSection = document.getElementById('resultsSection');
    const entropyValue = document.getElementById('entropyValue');
    const timeToCrack = document.getElementById('timeToCrack');
    const charPool = document.getElementById('charPool');
    const passwordLength = document.getElementById('passwordLength');
    const feedbackSection = document.getElementById('feedbackSection');
    const feedbackList = document.getElementById('feedbackList');

    const lowercaseIcon = document.getElementById('lowercaseIcon');
    const uppercaseIcon = document.getElementById('uppercaseIcon');
    const numberIcon = document.getElementById('numberIcon');
    const symbolIcon = document.getElementById('symbolIcon');
    const lengthIcon = document.getElementById('lengthIcon');

    let debounceTimer;
    function debounce(func, delay) {
        return function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(func, delay);
        };
    }

    togglePassword.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        this.textContent = type === 'password' ? '👁️' : '🙈';
    });

    passwordInput.addEventListener('input', debounce(function() {
        const password = passwordInput.value;
        if (!password) { resetUI(); return; }
        updateCriteriaIcons(password);
        checkPassword(password);
    }, 300));

    function updateCriteriaIcons(password) {
        lowercaseIcon.classList.toggle('met', /[a-z]/.test(password));
        lowercaseIcon.classList.toggle('unmet', !/[a-z]/.test(password));

        uppercaseIcon.classList.toggle('met', /[A-Z]/.test(password));
        uppercaseIcon.classList.toggle('unmet', !/[A-Z]/.test(password));

        numberIcon.classList.toggle('met', /[0-9]/.test(password));
        numberIcon.classList.toggle('unmet', !/[0-9]/.test(password));

        symbolIcon.classList.toggle('met', /[^a-zA-Z0-9]/.test(password));
        symbolIcon.classList.toggle('unmet', !/[^a-zA-Z0-9]/.test(password));

        lengthIcon.classList.toggle('met', password.length >= 8);
        lengthIcon.classList.toggle('unmet', password.length < 8);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            document.cookie.split(';').forEach(cookie => {
                const c = cookie.trim();
                if (c.startsWith(name + '=')) cookieValue = decodeURIComponent(c.substring(name.length + 1));
            });
        }
        return cookieValue;
    }

    async function checkPassword(password) {
        try {
            const csrftoken = getCookie('csrftoken');
            const response = await fetch('/api/check/', {
                method: 'POST',
                headers: {'Content-Type':'application/json','X-CSRFToken': csrftoken},
                body: JSON.stringify({ password })
            });

            if (response.status === 429) {
                strengthText.textContent = '⚠️ Rate limit exceeded';
                strengthText.style.color = '#ff0033';
                return;
            }

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Network response was not ok');
            }

            const data = await response.json();
            updateUI(data);
        } catch (error) {
            console.error(error);
            strengthText.textContent = error.message || 'Error analyzing password';
            strengthText.style.color = '#ff0033';
        }
    }

    function updateUI(data) {
        resultsSection.style.display = 'block';

        const strengthMap = {
            "Very Weak": ["⚠️ Critical Risk", "very-weak", 20],
            "Weak": ["🛑 Weak", "weak", 40],
            "Medium": ["⚡ Moderate", "medium", 60],
            "Strong": ["✅ Strong", "strong", 80],
            "Very Strong": ["🔒 Very Secure", "very-strong", 100]
        };

        const [text, cls, pct] = strengthMap[data.strength] || ['-', '', 0];
        strengthText.textContent = text;
        strengthText.style.color = '#00ff99';
        strengthMeterFill.style.width = pct + '%';
        strengthMeterFill.className = 'strength-meter-fill ' + cls;

        entropyValue.textContent = data.entropy_bits;
        timeToCrack.textContent = data.time_to_crack;
        charPool.textContent = data.character_pool;
        passwordLength.textContent = data.password_length;

        if (data.feedback?.length) {
            feedbackSection.style.display = 'block';
            feedbackList.innerHTML = '';
            data.feedback.forEach(f => {
                const li = document.createElement('li');
                li.textContent = f;
                feedbackList.appendChild(li);
            });
        } else {
            feedbackSection.style.display = 'none';
        }
    }

    function resetUI() {
        resultsSection.style.display = 'none';
        strengthMeterFill.style.width = '0%';
        strengthText.textContent = 'Enter a password to scan';
        strengthText.style.color = '#00ff99';

        [lowercaseIcon, uppercaseIcon, numberIcon, symbolIcon, lengthIcon].forEach(icon => {
            icon.classList.remove('met');
            icon.classList.add('unmet');
        });
    }

    resetUI();
});
