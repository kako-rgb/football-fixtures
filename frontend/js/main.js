// Constants
const API_URL = '/api/matches';
const FIXTURES_ELEMENT_ID = 'fixtures-list';
const UPDATE_TIME_ELEMENT_ID = 'update-time';
const LEAGUE_FILTER_ELEMENT_ID = 'league-filter';

// Global state
let matchesData = [];
let selectedLeague = 'all';

// DOM Elements
const fixturesElement = document.getElementById(FIXTURES_ELEMENT_ID);
const updateTimeElement = document.getElementById(UPDATE_TIME_ELEMENT_ID);
const leagueFilterElement = document.getElementById(LEAGUE_FILTER_ELEMENT_ID);

// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', initializeApp);

function initializeApp() {
    // Set up event listeners
    leagueFilterElement.addEventListener('change', handleLeagueFilterChange);
    
    // Initial data fetch
    fetchMatches();
    
    // Refresh data every 30 minutes without user intervention
    setInterval(fetchMatches, 30 * 60 * 1000);
}

async function fetchMatches() {
    try {
        fixturesElement.innerHTML = '<div class="loading">Loading upcoming matches...</div>';
        
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(`API returned ${response.status}: ${response.statusText}`);
        }
        
        matchesData = await response.json();
        
        // Update the last updated time
        updateTimeElement.textContent = new Date().toLocaleString();
        
        // Populate league filter dropdown
        populateLeagueFilter();
        
        // Render matches
        renderMatches();
    } catch (error) {
        console.error('Error fetching matches:', error);
        fixturesElement.innerHTML = `
            <div class="error">
                Failed to load matches. Please try again later.
                <p>${error.message}</p>
            </div>
        `;
    }
}

function populateLeagueFilter() {
    // Get unique leagues
    const leagues = new Set();
    
    matchesData.forEach(match => {
        const leagueName = match.competition?.name;
        if (leagueName) {
            leagues.add(leagueName);
        }
    });
    
    // Clear existing options except "All Leagues"
    while (leagueFilterElement.options.length > 1) {
        leagueFilterElement.remove(1);
    }
    
    // Add league options sorted alphabetically
    [...leagues].sort().forEach(league => {
        const option = document.createElement('option');
        option.value = league;
        option.textContent = league;
        leagueFilterElement.appendChild(option);
    });
}

function handleLeagueFilterChange(event) {
    selectedLeague = event.target.value;
    renderMatches();
}

function renderMatches() {
    // Filter matches by selected league
    const filteredMatches = selectedLeague === 'all' 
        ? matchesData 
        : matchesData.filter(match => match.competition?.name === selectedLeague);
    
    // Clear existing content
    fixturesElement.innerHTML = '';
    
    if (filteredMatches.length === 0) {
        fixturesElement.innerHTML = '<div class="no-matches">No upcoming matches found</div>';
        return;
    }
    
    // Sort matches by date/time
    filteredMatches.sort((a, b) => new Date(a.matchTime) - new Date(b.matchTime));
    
    // Create and append fixture cards
    filteredMatches.forEach(match => {
        const fixtureCard = createFixtureCard(match);
        fixturesElement.appendChild(fixtureCard);
    });
}

function createFixtureCard(match) {
    const card = document.createElement('div');
    card.className = 'fixture-card';
    
    // Format match time
    const matchDate = new Date(match.matchTime);
    const formattedTime = matchDate.toLocaleString(undefined, {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    // Get team data
    const homeTeam = match.homeTeam || {};
    const awayTeam = match.awayTeam || {};
    const competition = match.competition || {};
    
    card.innerHTML = `
        <div class="fixture-header">
            <div class="league-name">${competition.name || 'Unknown League'}</div>
            <div class="match-time">${formattedTime}</div>
        </div>
        
        <div class="teams-container">
            <div class="team">
                <img src="${homeTeam.logo || 'img/default-team.png'}" alt="${homeTeam.name}" class="team-logo">
                <div class="team-name">${homeTeam.name || 'Home Team'}</div>
            </div>
            
            <div class="versus">VS</div>
            
            <div class="team">
                <img src="${awayTeam.logo || 'img/default-team.png'}" alt="${awayTeam.name}" class="team-logo">
                <div class="team-name">${awayTeam.name || 'Away Team'}</div>
            </div>
        </div>
        
        <div class="form-container">
            <div class="form-group">
                <div class="form-title">Home team form</div>
                <div class="form-results">
                    ${renderFormIcons(homeTeam.lastFiveMatches || [])}
                </div>
            </div>
            
            <div class="form-group">
                <div class="form-title">Away team form</div>
                <div class="form-results">
                    ${renderFormIcons(awayTeam.lastFiveMatches || [])}
                </div>
            </div>
        </div>
    `;
    
    return card;
}

function renderFormIcons(formResults) {
    if (!formResults || formResults.length === 0) {
        return '<div class="no-form">No data</div>';
    }
    
    return formResults.map(result => {
        let className = '';
        
        switch (result) {
            case 'W':
                className = 'win';
                break;
            case 'D':
                className = 'draw';
                break;
            case 'L':
                className = 'loss';
                break;
            default:
                className = '';
        }
        
        return `<div class="form-result ${className}">${result}</div>`;
    }).join('');
}
