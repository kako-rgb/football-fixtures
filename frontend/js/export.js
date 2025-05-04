// Handle CSV export functionality
document.addEventListener('DOMContentLoaded', () => {
    const downloadButton = document.getElementById('download-csv');
    downloadButton.addEventListener('click', downloadMatchesCSV);
});

async function downloadMatchesCSV() {
    try {
        const button = document.getElementById('download-csv');
        const originalText = button.textContent;
        
        // Update button state
        button.textContent = 'Downloading...';
        button.disabled = true;
        
        // Request CSV from server
        const response = await fetch('/api/matches/csv');
        
        if (!response.ok) {
            throw new Error(`Failed to generate CSV (${response.status})`);
        }
        
        // Get CSV blob
        const blob = await response.blob();
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        
        // Generate filename with current date
        const date = new Date().toISOString().split('T')[0];
        a.download = `football_fixtures_${date}.csv`;
        
        // Trigger download
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Reset button
        button.textContent = originalText;
        button.disabled = false;
    } catch (error) {
        console.error('Error downloading CSV:', error);
        
        // Reset button and show error
        const button = document.getElementById('download-csv');
        button.textContent = 'Download as CSV';
        button.disabled = false;
        
        alert(`Failed to download: ${error.message}`);
    }
}
