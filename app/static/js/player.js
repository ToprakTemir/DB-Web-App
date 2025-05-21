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

// Load opponent history
function loadOpponentHistory() {
    console.log("Loading opponent history...");

    fetch('/player/opponent-history')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            const opponentsTable = document.getElementById('opponents-table').getElementsByTagName('tbody')[0];
            opponentsTable.innerHTML = ''; // Clear existing rows
            
            if (data.length === 0) {
                // Display a message if no opponents exist
                const row = opponentsTable.insertRow();
                const cell = row.insertCell();
                cell.colSpan = 5;
                cell.textContent = 'No opponent history found.';
                cell.style.textAlign = 'center';
                cell.style.padding = '20px';
            } else {
                // Populate table with opponent data
                data.forEach(opponent => {
                    const row = opponentsTable.insertRow();
                    row.insertCell().textContent = opponent.player_name;
                    row.insertCell().textContent = opponent.elo_rating;
                    row.insertCell().textContent = opponent.title_name;
                    row.insertCell().textContent = opponent.nationality;
                    row.insertCell().textContent = opponent.times_played;
                });
            }
        })
        .catch(error => {
            console.error('Error loading opponents:', error);
            showMessage('Failed to load opponents data. Please try again later.', 'error');
        });
}

// Load most frequent opponent data
function loadMostFrequentOpponent() {
    console.log("Loading most frequent opponent data...");

    fetch('/player/frequent-opponent')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            document.getElementById("player-name").textContent = data.player_name;
            document.getElementById("player-country").textContent = data.nationality;
            document.getElementById("elo-rating").textContent = data.elo_rating;
            document.getElementById("player-title").textContent = data.title_name;
            document.getElementById("matches-played").textContent = data.times_played;
        })
        .catch(error => {
            console.error('Error loading most frequent opponent:', error);
            showMessage('Failed to load most frequent opponent. Please try again later.', 'error');
        });
}

// Load match history
function loadMatchHistory() {
    console.log("Loading match history...");

    fetch('/player/match-history')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            const matchesTable = document.getElementById('matches-table').getElementsByTagName('tbody')[0];
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
                    row.insertCell().textContent = match.date;
                    row.insertCell().textContent = match.slot;
                    row.insertCell().textContent = match.hall_name;
                    row.insertCell().textContent = `${match.table}`;
                    row.insertCell().textContent = match.your_team;
                    row.insertCell().textContent = match.opponent_team;
                    row.insertCell().textContent = match.opponent_name;
                    row.insertCell().textContent = match.arbiter_name;
                    row.insertCell().textContent = match.rating || 'Not rated';
                    row.insertCell().textContent = match.result || 'Unknown';
                    
                });
            }
        })
        .catch(error => {
            console.error('Error loading matches:', error);
            showMessage('Failed to load matches. Please try again later.', 'error');
        });
}

// Load player info
function loadPlayerInfo() {
    console.log("Loading player info...");
    
    fetch('/player/profile')
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(player => {
            const data = player[0];
            console.log("Player info received:", data);

            document.querySelector('.player-name').textContent = data.fullname;
            document.querySelector('.player-id').textContent = `FIDE ID: ${data.fide_id}`;
            document.getElementById('player-nationality').textContent = `Nationality: ${data.nationality}`;
            document.getElementById('player-teams').textContent = `Teams: ${data.teams.join(', ')}`;
            document.querySelector('.rating').textContent = data.elo_rating;
            document.querySelector('.title').textContent = data.title_name;
        })
        .catch(error => {
            console.error('Failed to load player info:', error);
        });
}

// Set up event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Load initial data
    loadPlayerInfo();
    loadOpponentHistory();
    loadMostFrequentOpponent();
    loadMatchHistory();
});