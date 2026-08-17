function scrollToSpot(spot) {
    var where = (spot === 'bottom') ? document.body.scrollHeight : 0;
    window.scrollTo({
        top: where,
        behavior: 'smooth'
    });
}

function toggleDark() {
    const isNowDark = document.body.classList.toggle('dark-mode');
    const textColor = isNowDark ? '#F5F5F0' : '#35393C';
    const bgColor = isNowDark ? '#35393C' : '#F5F5F0';

    document.querySelectorAll('.card').forEach(function(link) {
        link.style.backgroundColor = bgColor;
        link.style.color = textColor;
    });

    localStorage.setItem('darkMode', isNowDark);
}

const password = document.getElementById('new_password');
const confirmPass = document.getElementById('confirm_password');
const submitBtn = document.getElementById('submitBtn');

function validatePasswords() {
    if (confirmPass.value.length > 0) {
        if (password.value === confirmPass.value) {
            confirmPass.classList.remove('is-invalid');
            confirmPass.classList.add('is-valid');
            submitBtn.disabled = false;
        } else {
            confirmPass.classList.remove('is-valid');
            confirmPass.classList.add('is-invalid');
            submitBtn.disabled = true;
        }
    } else {
        confirmPass.classList.remove('is-invalid', 'is-valid');
        submitBtn.disabled = false;
    }
}

if (password && confirmPass && submitBtn) {
    password.addEventListener('input', validatePasswords);
    confirmPass.addEventListener('input', validatePasswords);
}



window.addEventListener('DOMContentLoaded', () => {
    // Run toggle dark when page loads to restore preferred theme
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true') {
        toggleDark();
    }

    // highlight rows with "fraud" in the description
    const rows = document.querySelectorAll('.expense-row');
    if (rows.length > 0) {
        const regex = /\bfraud\b/i;
        rows.forEach(row => {
            const descriptionCell = row.cells[4]; 
            const descriptionText = descriptionCell.textContent || descriptionCell.innerText;

            if (regex.test(descriptionText)) {
                row.classList.add('fraud');
            }
        });
    }
});