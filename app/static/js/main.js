function scrollToSpot(spot) {
    // Determine where to scroll then do it
    var where = (spot === 'bottom') ? document.body.scrollHeight : 0;
    window.scrollTo({
        top: where,
        behavior: 'smooth'
    });
}

function toggleDark() {
    // Determine the new theme based on current background
    const isNowDark = document.body.style.backgroundColor !== 'black';
    const bgColor = isNowDark ? 'black' : 'white';
    const textColor = isNowDark ? 'white' : 'black';

    // Apply to body
    document.body.style.backgroundColor = bgColor;
    document.body.style.color = textColor;

    // Apply to all cards
    document.querySelectorAll('.card').forEach(function(link) {
        link.style.backgroundColor = bgColor;
        link.style.color = textColor;
    });

    // Save to storage
    localStorage.setItem('darkMode', isNowDark);
}

const password = document.getElementById('new_password');
const confirmPass = document.getElementById('confirm_password');
const submitBtn = document.getElementById('submitBtn');

function validatePasswords() {
    // Only validate if the user has actually typed something in the confirmation box
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
        // Reset if confirm is empty
        confirmPass.classList.remove('is-invalid', 'is-valid');
        submitBtn.disabled = false;
    }
}

// Listen for typing events on both fields
if (password && confirmPass && submitBtn) {
    password.addEventListener('input', validatePasswords);
    confirmPass.addEventListener('input', validatePasswords);
}


// Run toggle dark when page loads to restore preferred theme
window.addEventListener('DOMContentLoaded', () => {
    const savedDarkMode = localStorage.getItem('darkMode');
    
    if (savedDarkMode === 'true') {
        toggleDark();
    }
});