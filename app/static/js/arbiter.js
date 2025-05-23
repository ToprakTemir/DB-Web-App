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

// Show a modal by id
function showModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

// Hide a modal by id
function hideModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Show the rate match modal
function showRateMatchModal(matchId) {
    document.getElementById('rate-match-id').value = matchId;
    showModal('rate-modal');
}

// Show the rate match modal
function showUpdateResultModal(matchId) {
    document.getElementById('update-result-id').value = matchId;
    showModal('update-result-modal');
}

// Load assigned matches
function loadAssignedMatches() {
    fetch('/arbiter/assigned-matches')
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch assigned matches');
            return response.json();
        })
        .then(matches => {
            const tbody = document.querySelector('#assigned-matches-table tbody');
            tbody.innerHTML = ''; // Clear existing rows

            matches.forEach(match => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${match.match_date}</td>
                    <td>${match.time_slot}</td>
                    <td>${match.hall_name}</td>
                    <td>${match.table_id}</td>
                    <td>${match.team1}</td>
                    <td>${match.team2}</td>
                    <td>${match.player1}</td>
                    <td>${match.player2}</td>
                    <td>${match.result == null ? 'Not updated.' : match.result}</td>
                    <td>${match.ratings == null ? 'Not rated.' : match.ratings}</td>
                    <td>
                        ${parseDate(match.match_date) > new Date() ?
                        'Upcoming match' :
                        (match.result == null ? 
                            `<button class="rate-btn" onclick="showUpdateResultModal(${match.match_id})">Update Result</button>` :
                            'Already updated.')
                        }
                    </td>
                    <td>
                        ${parseDate(match.match_date) > new Date() ?
                        'Upcoming match' :
                        (match.ratings == null ? 
                            `<button class="rate-btn" onclick="showRateMatchModal(${match.match_id})">Rate Match</button>` :
                            'Already rated.')
                        }
                    </td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error(error);
            showMessage('Error loading assigned matches.', 'error');
        });
}

// Load rating statistics
function loadRatingStats() {
    console.log("Loading rating statistics...");

    fetch('/arbiter/rating-stats')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(datalist => {
            // Update Total Matches Rated
            datalist.forEach(data => {
                document.querySelector('#ratingStats .stat-box:nth-child(1) .stat-value').textContent = data.total_matches_rated ?? 0;

                // Update Average Rating Given (formatted to 1 decimal place)
                const avgRating = data.average_rating_given;
                document.querySelector('#ratingStats .stat-box:nth-child(2) .stat-value').textContent =
                    (avgRating !== null && avgRating !== undefined) ? avgRating : '0.0';
            });
            
        })
        .catch(error => {
            console.error('Error fetching rating stats:', error);
        });
}

function parseDate(dateStr) {
    const [day, month, year] = dateStr.split('-');
    return new Date(`${year}-${month}-${day}`);
}

// Set up event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Load initial data
    loadAssignedMatches();
    loadRatingStats();
    
    // Add form submission handler for rating
    document.getElementById('rate-match-form').addEventListener('submit', async function(event) {
        event.preventDefault();

        const matchId = document.getElementById('rate-match-id').value;
        const ratingInput = document.getElementById('match-rating');
        const rating = parseFloat(ratingInput.value);

        // Basic validation
        if (isNaN(rating) || rating < 0 || rating > 10) {
            alert('Please enter a valid rating between 0 and 10.');
            ratingInput.focus();
            return;
        }

        // Disable submit button to prevent multiple submissions
        const submitBtn = this.querySelector('button[type="submit"]');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/arbiter/rate-match', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ match_id: matchId, rating: rating })
            });

            if (!response.ok) {
                throw new Error('Failed to submit rating. Please try again.');
            }

            const result = await response.json();

            // Assuming backend returns { success: true, message: "Rating saved" }
            if (result.success) {
                alert(`Rating of ${rating.toFixed(1)} submitted for match #${matchId}`);
                hideModal('rate-modal');
                loadAssignedMatches();
            } else {
                alert(`Error: ${result.message || 'Unknown error'}`);
            }
        } catch (error) {
            alert(`Submission error: ${error.message}`);
        } finally {
            submitBtn.disabled = false;
        }
    });


    // Add form submission handler for result updating
    document.getElementById('update-result-form').addEventListener('submit', async function(event) {
        event.preventDefault();

        const matchId = document.getElementById('update-result-id').value;
        const resultInput = document.getElementById('result');

        // Disable submit button to prevent multiple submissions
        const submitBtn = this.querySelector('button[type="submit"]');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/arbiter/update-result', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ match_id: matchId, result: resultInput.value })
            });

            if (!response.ok) {
                throw new Error('Failed to update result. Please try again.');
            }

            const resp = await response.json();

            // Assuming backend returns { success: true, message: "Rating saved" }
            if (resp.success) {
                alert(`Result of ${resultInput.value} submitted for match #${matchId}`);
                hideModal('update-result-modal');
                loadAssignedMatches();
            } else {
                alert(`Error: ${resp.message || 'Unknown error'}`);
            }
        } catch (error) {
            alert(`Submission error: ${error.message}`);
        } finally {
            submitBtn.disabled = false;
        }
    });
});