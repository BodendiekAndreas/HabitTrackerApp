document.addEventListener('DOMContentLoaded', function() {
    // Example: AJAX form submission for adding a new habit
    const addHabitForm = document.querySelector('#addHabitForm');
    if (addHabitForm) {
        addHabitForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent the default form submission
            const formData = new FormData(this);

            // Perform the AJAX request
            fetch('/habits/add', {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Handle success, e.g., display a message, redirect, etc.
                    console.log('Habit added successfully');
                } else {
                    // Handle failure, e.g., display error messages
                    console.error('Failed to add habit');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // Example: Initializing a date picker component
    // Assuming you are using a library like flatpickr
    const datePickerElements = document.querySelectorAll('.date-picker');
    datePickerElements.forEach(datePickerElement => {
        function flatpickr(datePickerElement, param2) {
            
        }

        flatpickr(datePickerElement, {
            // Configuration options here
        });
    });

    // Other dynamic behaviors and initializations can go here
});
