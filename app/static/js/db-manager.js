// Show/hide fields based on user type selection
document.getElementById('user-type').addEventListener('change', function () {
    const userType = this.value;

    // Utility to show/hide and enable/disable groups
    function toggleGroup(id, show) {
        const group = document.getElementById(id);
        group.style.display = show ? 'block' : 'none';

    // Enable or disable all inputs in the group
    const inputs = group.querySelectorAll('input, select');
    inputs.forEach(input => {
    input.disabled = !show;
    });
}

toggleGroup('player-fields', userType === 'player');
toggleGroup('arbiter-fields', userType === 'arbiter');
toggleGroup('coach-fields', userType === 'coach');
});

// Tab switching function
function openTab(evt, tabName) {
    const tabcontent = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
        tabcontent[i].classList.remove("active-tab");
    }
    
    const tablinks = document.getElementsByClassName("tablinks");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    
    document.getElementById(tabName).style.display = "block";
    document.getElementById(tabName).classList.add("active-tab");
    evt.currentTarget.className += " active";
}

// Load halls for the rename hall form (would be implemented with backend)
function loadHalls() {
    fetch('/data/halls')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
            })
        .then(data => {
            const hallSelect = document.getElementById('hall-id');
            hallSelect.innerHTML = '<option value="">Select a Hall</option>';
            data.forEach(hall => {
                const option = document.createElement('option');
                option.value = hall.hall_id;
                option.textContent = hall.hall_name;
                hallSelect.appendChild(option);
            });
            })
        .catch(error => {
            console.error('Error loading halls:', error);
        });
}
window.onload = function() {
    loadHalls();
};