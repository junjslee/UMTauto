// script.js
document.addEventListener('DOMContentLoaded', () => {
    const participantLimitInput = document.getElementById('participant_limit');
    const eventNameSelect = document.getElementById('event_name');
    const form = document.querySelector('form');
    const cancelButton = document.getElementById('cancel_button');

    // Validate participant limit
    participantLimitInput.addEventListener('input', () => {
        if (participantLimitInput.value < 0) {
            participantLimitInput.value = 0;
        }
    });

    // Validate event name selection
    eventNameSelect.addEventListener('change', () => {
        if (!eventNameSelect.value) {
            eventNameSelect.setCustomValidity('Please select an event from the list.');
        } else {
            eventNameSelect.setCustomValidity('');
        }
    });

    // Handle form submission
    form.addEventListener('submit', (event) => {
        if (eventNameSelect.value === "") {
            eventNameSelect.setCustomValidity('Please select an event from the list.');
            event.preventDefault();
        }
    });

    // Handle cancel button click
    cancelButton.addEventListener('click', () => {
        form.reset(); // Reset all form fields
        eventNameSelect.setCustomValidity(''); // Clear validation messages
        CKEDITOR.instances['message'].setData(''); // Clear CKEditor content
    });
});
