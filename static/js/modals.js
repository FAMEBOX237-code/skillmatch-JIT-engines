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







// ===============================
// MODAL TO MODAL TRANSITION (GLOBAL)
// ===============================

// 6. Find all buttons that open another modal
const nextModalButtons = document.querySelectorAll('[data-next-modal]');

// 7. Loop through them
nextModalButtons.forEach(button => {
    button.addEventListener('click', () => {

        // a) Find the current open modal
        const currentModal = button.closest('.modal');

        // b) Get the ID of the next modal
        const nextModalId = button.getAttribute('data-next-modal');
        const nextModal = document.getElementById(nextModalId);

        // c) Close current modal
        currentModal.classList.remove('show');

        // d) Open next modal
        nextModal.classList.add('show');
    });
});





// ===============================
// GLOBAL MESSAGE HANDLER
// ===============================

/**
 * showMessage(type, text)
 * type: success | error | info | warning
 * text: string message to display
 */
function showMessage(type, text) {

    // 1. Get the message container
    const messageBox = document.getElementById('appMessage');

    // 2. Safety check (in case page has no message box)
    if (!messageBox) return;

    // 3. Reset previous state
    messageBox.className = 'app-message';

    // 4. Apply new message type
    messageBox.classList.add(type);

    // 5. Set icon based on type
    const iconMap = {
        success: '✔️',
        error: '❌',
        info: 'ℹ️',
        warning: '⚠️'
    };

    messageBox.querySelector('.message-icon').textContent = iconMap[type];
    messageBox.querySelector('.message-text').textContent = text;

    // 6. Show message
    messageBox.style.display = 'flex';

    // 7. Auto-hide after 4 seconds
    setTimeout(() => {
        messageBox.style.display = 'none';
    }, 4000);
}
