document.addEventListener('DOMContentLoaded', function(){
    // Add event listener to login form
    document.getElementById('login-form').addEventListener('submit', function(event) {
        event.preventDefault();
        
        
        // Submit the form data via AJAX
        const formData = new FormData(this);
        
        fetch('/login', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect;
            }
            else{
                showMessage(data.message || 'Failed to login.', 'error');
                this.reset(); // Reset form fields
            }
        })
        .catch(error => {
            console.error('Error logging in:', error);
            showMessage('Failed to login. Please try again later.', 'error');
        });
    });
})

// Function to show success/error messages
function showMessage(message, type) {
    const messageContainer = document.getElementById('error-message');
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = type; // 'success' or 'error'
    messageDiv.textContent = message;
    
    // Clear any existing messages
    messageContainer.innerHTML = '';
    messageContainer.appendChild(messageDiv);
    
    // Automatically remove message after 5 seconds
    setTimeout(function() {
        messageDiv.remove();
    }, 5000);
}