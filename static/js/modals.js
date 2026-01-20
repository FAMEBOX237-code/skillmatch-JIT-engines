// ===============================
// GLOBAL MODAL HANDLER (BEGINNER)
// ===============================

// 1. Find all buttons that open modals
const openModalButtons = document.querySelectorAll('[data-open-modal]');

// 2. Find all elements that close modals
const closeModalButtons = document.querySelectorAll('.close-modal');

// 3. Open modal when button is clicked
openModalButtons.forEach(button => {
    button.addEventListener('click', () => {
        const modalId = button.getAttribute('data-open-modal');
        const modal = document.getElementById(modalId);
        modal.classList.add('show');
    });
});

// 4. Close modal when close button is clicked
closeModalButtons.forEach(button => {
    button.addEventListener('click', () => {
        const modal = button.closest('.modal');
        modal.classList.remove('show');
    });
});

// 5. Close modal when clicking outside the modal content
window.addEventListener('click', (event) => {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('show');
    }
});







const params = new URLSearchParams(window.location.search);
if (params.has('reset') === true ) {
    const modal = document.getElementById('resetPasswordModal');
    if (modal) {
        modal.classList.add("show");
    }
}



      // Handle Accept button clicks
document.querySelectorAll('.accept-collaboration-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        // Optional: Confirm before accepting
        if (confirm(`Accept collaboration with ${this.closest('.interested-user').querySelector('.user-name').textContent}?`)) {
            
            // Visual feedback: change button to "Accepted"
            this.textContent = 'Accepted';
            this.classList.add('accepted');
            this.disabled = true;

            // TODO: Here you would send data to your backend
            // Example: fetch('/accept-collaboration', { method: 'POST', body: JSON.stringify({ userId: ..., postId: ... }) })

            alert('Collaboration accepted! You can now message them.');
        }
    });
});

// AUTO-HIDE FLASH MESSAGES AFTER 6 SECONDS
setTimeout(() => {
    const messages = document.querySelectorAll('.flash-messages');
    messages.forEach(msg => {
        msg.style.opacity = '0';
        setTimeout(() => msg.remove(), 500);
    });
}, 6000);



const slider = document.getElementById("ratingSlider");
    const output = document.getElementById("ratingValue");
    if (slider && output) {
        slider.addEventListener("input", function() {
            output.textContent = slider.value + " +";
        });
    }






const countdownElem = document.getElementById("lockoutCountdown");

if (countdownElem) {
    let remaining = parseInt(countdownElem.textContent);
    const loginBtn = document.querySelector(".auth-btn");

    if (loginBtn) loginBtn.disabled = true;

    const interval = setInterval(() => {
        remaining--;
        countdownElem.textContent = remaining;

        if (remaining <= 0) {
            clearInterval(interval);

            if (loginBtn) loginBtn.disabled = false;

            countdownElem.parentElement.textContent =
                "You can try logging in again. Reloading…";

            setTimeout(() => {
                window.location.href = "/login";
            }, 1000);
        }
    }, 1000);
}