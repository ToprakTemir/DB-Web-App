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

// Load available halls for the create match form
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

// Load tables based on selected hall
function loadTables() {
    const hall_id = document.getElementById('hall-id').value;

    const url = `/data/tables?hall_id=${encodeURIComponent(hall_id)}`;

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
            })
        .then(data => {
            const tableSelect = document.getElementById('table-id');
            tableSelect.innerHTML = '<option value="">Select a Table</option>';
            data.forEach(table => {
                const option = document.createElement('option');
                option.value = table.table_id;
                option.textContent = table.table_id;
                tableSelect.appendChild(option);
            });
            })
        .catch(error => {
            console.error('Error loading tables:', error);
        });
}

// Load opponent teams
function loadOpponentTeams() {
    fetch('/data/opponent-teams')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
            })
        .then(data => {
            const teamSelect = document.getElementById('opponent-team');
            teamSelect.innerHTML = '<option value="">Select Opponent Team</option>';
            data.forEach(team => {
                const option = document.createElement('option');
                option.value = team.team_id;
                option.textContent = team.team_name;
                teamSelect.appendChild(option);
            });
            })
        .catch(error => {
            console.error('Error loading teams:', error);
        });
}

// Load arbiters
function loadArbiters() {
    const matchDate = document.getElementById('match-date').value;
    const timeSlot = document.getElementById('time-slot').value;

    const url = `/data/available-arbiters?date=${encodeURIComponent(matchDate)}&time_slot=${encodeURIComponent(timeSlot)}`;

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
            })
        .then(data => {
            const arbiterSelect = document.getElementById('arbiter-name');
            arbiterSelect.innerHTML = '<option value="">Select an Arbiter</option>';
            data.forEach(arbiter => {
                const option = document.createElement('option');
                option.value = arbiter.username;
                option.textContent = arbiter.name + ' ' + arbiter.surname;
                arbiterSelect.appendChild(option);
            });
            })
        .catch(error => {
            console.error('Error loading arbiters:', error);
        });
}

// Show a modal by id
function showModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

// Hide a modal by id
function hideModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Show the assign player modal
function showAssignPlayerModal(matchId) {
    document.getElementById('match-id').value = matchId;
    showModal('assign-modal');
    
    // Load players from your team
    const playerSelect = document.getElementById('player-username');
    playerSelect.innerHTML = '<option value="">Select Player from Your Team</option>' +
        '<option value="1">Alex Johnson</option>' +
        '<option value="2">Robert Davis</option>' +
        '<option value="3">Emma Wilson</option>';
}

// Confirm before deleting a match
function confirmDeleteMatch(matchId) {
    if (confirm('Are you sure you want to delete this match? This action cannot be undone.')) {
        // Send request to delete the match
        // This would be an AJAX call to the server
        alert('Match deleted successfully!');
        // Then remove the row from the table or refresh the table
    }
}

// Set up event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Load initial data
    loadHalls();
    loadOpponentTeams();
    
    // Add event listener for hall selection to load tables
    document.getElementById('hall-id').addEventListener('change', function() {
        loadTables();
    });
    
    // Add event listeners for date and time selection to load available arbiters
    document.getElementById('match-date').addEventListener('change', updateAvailableArbiters);
    document.getElementById('time-slot').addEventListener('change', updateAvailableArbiters);
});

function updateAvailableArbiters() {
    const date = document.getElementById('match-date').value;
    const timeSlot = document.getElementById('time-slot').value;
    
    if (date && timeSlot) {
        loadArbiters();
    }
}
// Function to load unassigned matches for the coach's team
function loadUnassignedMatches() {
    fetch('/data/unassigned-matches')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            const matchesTable = document.getElementById('unassigned-matches-table').getElementsByTagName('tbody')[0];
            matchesTable.innerHTML = ''; // Clear existing rows
            
            if (data.length === 0) {
                // Display a message if no unassigned matches exist
                const row = matchesTable.insertRow();
                const cell = row.insertCell();
                cell.colSpan = 7;
                cell.textContent = 'No unassigned matches found.';
                cell.style.textAlign = 'center';
                cell.style.padding = '20px';
            } else {
                // Populate table with unassigned matches
                data.forEach(match => {
                    const row = matchesTable.insertRow();
                    
                    // Add cells with match data
                    row.insertCell().textContent = match.match_date;
                    row.insertCell().textContent = `Time Slot ${match.time_slot}-${parseInt(match.time_slot) + 1}`;
                    row.insertCell().textContent = match.hall_name;
                    row.insertCell().textContent = `Table ${match.table_id}`;
                    row.insertCell().textContent = match.opponent_team_name;
                    row.insertCell().textContent = match.arbiter_name;
                    
                    // Add action button cell
                    const actionCell = row.insertCell();
                    const assignBtn = document.createElement('button');
                    assignBtn.className = 'assign-btn';
                    assignBtn.textContent = 'Assign Player';
                    assignBtn.onclick = function() { showAssignPlayerModal(match.match_id); };
                    actionCell.appendChild(assignBtn);
                });
            }
        })
        .catch(error => {
            console.error('Error loading unassigned matches:', error);
            showMessage('Failed to load unassigned matches. Please try again later.', 'error');
        });
}

// Function to load all matches for the coach's team (both assigned and unassigned)
function loadAllMatches() {
    fetch('/data/coach-matches')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            const matchesTable = document.getElementById('manage-matches-table').getElementsByTagName('tbody')[0];
            matchesTable.innerHTML = ''; // Clear existing rows
            
            if (data.length === 0) {
                // Display a message if no matches exist
                const row = matchesTable.insertRow();
                const cell = row.insertCell();
                cell.colSpan = 10;
                cell.textContent = 'No matches found.';
                cell.style.textAlign = 'center';
                cell.style.padding = '20px';
            } else {
                // Populate table with all matches
                data.forEach(match => {
                    const row = matchesTable.insertRow();
                    
                    // Add cells with match data
                    row.insertCell().textContent = match.match_date;
                    row.insertCell().textContent = `Time Slot ${match.time_slot}-${parseInt(match.time_slot) + 1}`;
                    row.insertCell().textContent = match.hall_name;
                    row.insertCell().textContent = `Table ${match.table_id}`;
                    row.insertCell().textContent = match.opponent_team_name;
                    row.insertCell().textContent = match.player_name || 'Not assigned';
                    row.insertCell().textContent = match.opponent_player_name || 'Not assigned';
                    row.insertCell().textContent = match.arbiter_name;
                    row.insertCell().textContent = match.rating || 'Not rated';
                    
                    // Add action button cell
                    const actionCell = row.insertCell();
                    const deleteBtn = document.createElement('button');
                    deleteBtn.className = 'delete-btn';
                    deleteBtn.textContent = 'Delete';
                    deleteBtn.onclick = function() { confirmDeleteMatch(match.match_id); };
                    actionCell.appendChild(deleteBtn);
                });
            }
        })
        .catch(error => {
            console.error('Error loading matches:', error);
            showMessage('Failed to load matches. Please try again later.', 'error');
        });
}

// Function to load all available halls
function loadAllHalls() {
    fetch('/data/halls')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            const hallsTable = document.getElementById('halls-table').getElementsByTagName('tbody')[0];
            hallsTable.innerHTML = ''; // Clear existing rows
            
            if (data.length === 0) {
                // Display a message if no halls exist
                const row = hallsTable.insertRow();
                const cell = row.insertCell();
                cell.colSpan = 3;
                cell.textContent = 'No halls found.';
                cell.style.textAlign = 'center';
                cell.style.padding = '20px';
            } else {
                // Populate table with halls data
                data.forEach(hall => {
                    const row = hallsTable.insertRow();
                    row.insertCell().textContent = hall.hall_name;
                    row.insertCell().textContent = hall.country;
                    row.insertCell().textContent = hall.capacity;
                });
            }
        })
        .catch(error => {
            console.error('Error loading halls:', error);
            showMessage('Failed to load halls data. Please try again later.', 'error');
        });
}

// Function to load available players from your team for assignment
function loadTeamPlayers(matchId) {
    fetch(`/data/available-players?match_id=${encodeURIComponent(matchId)}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            const playerSelect = document.getElementById('player-username');
            playerSelect.innerHTML = '<option value="">Select Player from Your Team</option>';
            
            if (data.length === 0) {
                const option = document.createElement('option');
                option.value = "";
                option.textContent = "No available players for this match";
                option.disabled = true;
                playerSelect.appendChild(option);
            } else {
                data.forEach(player => {
                    const option = document.createElement('option');
                    option.value = player.player_username;
                    option.textContent = `${player.name} ${player.surname} (Rating: ${player.ratings})`;
                    playerSelect.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Error loading team players:', error);
            showMessage('Failed to load team players. Please try again later.', 'error');
        });
}

// Function to handle player assignment form submission
function submitPlayerAssignment(event) {
    event.preventDefault();
    
    const matchId = document.getElementById('match-id').value;
    const playerId = document.getElementById('player-username').value;
    
    // Validate form fields
    if (!matchId || !playerId) {
        showMessage('Please select a player.', 'error');
        return;
    }
    
    // Create request body
    const formData = {
        match_id: matchId,
        player_username: playerId
    };
    
    // Submit assignment via AJAX
    fetch('/coach/assign-player', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showMessage('Player assigned successfully!', 'success');
            hideModal('assign-modal');
            
            // Reload both unassigned matches and all matches
            loadUnassignedMatches();
            loadAllMatches();
        } else {
            showMessage(data.message || 'Failed to assign player.', 'error');
        }
    })
    .catch(error => {
        console.error('Error assigning player:', error);
        showMessage('Failed to assign player. Please try again later.', 'error');
    });
}

// Function to handle match deletion
function deleteMatch(matchId) {
    fetch(`/coach/delete-match/${matchId}`, {
        method: 'DELETE',
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showMessage('Match deleted successfully!', 'success');
            
            // Reload all matches
            loadAllMatches();
        } else {
            showMessage(data.message || 'Failed to delete match.', 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting match:', error);
        showMessage('Failed to delete match. Please try again later.', 'error');
    });
}

// Improved function for confirming and executing match deletion
function confirmDeleteMatch(matchId) {
    if (confirm('Are you sure you want to delete this match? This action cannot be undone.')) {
        deleteMatch(matchId);
    }
}

// Function to show success/error messages
function showMessage(message, type) {
    const messageContainer = document.getElementById('message-container');
    
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

// Improved function to show the assign player modal
function showAssignPlayerModal(matchId) {
    document.getElementById('match-id').value = matchId;
    loadTeamPlayers(matchId); // Load available players for this match
    showModal('assign-modal');
}

function loadCoachTeam(){
    fetch('/data/coach-team')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            const teamName = document.getElementById("team-name");
            if (data.length === 0){   
                teamName.textContent = "No Active Contract";
            }
            else{
                teamName.textContent = data.team_name;
            }
        })
        .catch(error => {
            console.error('Error loading coach team:', error);
            showMessage('Failed to load coach team. Please try again later.', 'error');
        });
}

// Update event listeners in the DOMContentLoaded function
document.addEventListener('DOMContentLoaded', function() {
    // Load data for all tabs
    loadHalls();
    loadOpponentTeams();
    loadUnassignedMatches();
    loadAllMatches();
    loadAllHalls();
    loadCoachTeam();
    
    // Add event listener for hall selection to load tables
    document.getElementById('hall-id').addEventListener('change', function() {
        loadTables();
    });
    
    // Add event listeners for date and time selection to load available arbiters
    document.getElementById('match-date').addEventListener('change', updateAvailableArbiters);
    document.getElementById('time-slot').addEventListener('change', updateAvailableArbiters);
    
    // Add event listener to player assignment form
    document.getElementById('assign-player-form').addEventListener('submit', submitPlayerAssignment);
    
    // Add event listener to match creation form
    document.getElementById('create-match-form').addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Validate form fields (simple validation)
        const date = document.getElementById('match-date').value;
        const timeSlot = document.getElementById('time-slot').value;
        const hallId = document.getElementById('hall-id').value;
        const tableId = document.getElementById('table-id').value;
        const opponentTeamId = document.getElementById('opponent-team').value;
        const arbiterName = document.getElementById('arbiter-name').value;
        
        if (!date || !timeSlot || !hallId || !tableId || !opponentTeamId || !arbiterName) {
            showMessage('Please fill in all required fields.', 'error');
            return;
        }
        
        // Submit the form data via AJAX
        const formData = new FormData(this);
        
        fetch('/coach/create-match', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showMessage('Match created successfully!', 'success');
                this.reset(); // Reset form fields
                
                // Reload unassigned matches and all matches
                loadUnassignedMatches();
                loadAllMatches();
            } else {
                showMessage(data.message || 'Failed to create match.', 'error');
            }
        })
        .catch(error => {
            console.error('Error creating match:', error);
            showMessage('Failed to create match. Please try again later.', 'error');
        });
    });
});