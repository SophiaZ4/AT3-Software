// This ensures the script runs after the entire HTML document has been loaded
document.addEventListener('DOMContentLoaded', () => {

    // maps position IDs to full name, description, and allowed court areas.
    const positionData = {
        'GS': {
            name: 'Goal Shooter',
            description: 'The Goal Shooter\'s main role is to score goals. They are the only player allowed in the team\'s goal circle along with the Goal Attack.',
            areas: ['goal-third-b', 'goal-circle-b']
        },
        'GA': {
            name: 'Goal Attack',
            description: 'The Goal Attack shares the scoring responsibilities with the GS. They also go in the center third, to help bring the ball down the court.',
            areas: ['goal-third-b', 'centre-third', 'goal-circle-b']
        },
        'WA': {
            name: 'Wing Attack',
            description: 'The Wing Attack feeds the ball to the shooters. They control the attacking flow through the centre third but cannot enter the goal circle.',
            areas: ['goal-third-b', 'centre-third']
        },
        'C': {
            name: 'Centre',
            description: 'The Centre is a central player. They are the only player allowed in all three thirds, but they cannot enter either goal circle. They take the centre pass to restart play.',
            areas: ['goal-third-a', 'centre-third', 'goal-third-b']
        },
        'WD': {
            name: 'Wing Defence',
            description: 'The Wing Defence marks the opposing Wing Attack. Their job is to prevent the ball from reaching the opposition\'s goal third and to win possession for their team.',
            areas: ['goal-third-a', 'centre-third']
        },
        'GD': {
            name: 'Goal Defence',
            description: 'The Goal Defence works to prevent goals and intercept passes. They mark the opposing Goal Attack and can move through the defensive and centre thirds.',
            areas: ['goal-third-a', 'centre-third', 'goal-circle-a']
        },
        'GK': {
            name: 'Goal Keeper',
            description: 'The Goal Keeper is the last line of defence. Their primary role is to prevent the Goal Shooter from scoring and to rebound missed shots. They stay within the defensive goal third.',
            areas: ['goal-third-a', 'goal-circle-a']
        }
    };

    // Get references to the HTML elements
    const buttons = document.querySelectorAll('.position-buttons button');
    const courtAreas = document.querySelectorAll('#court-zones .court-area');
    const infoPanel = document.getElementById('position-info-panel');
    const infoPanelTitle = document.getElementById('info-panel-title');
    const infoPanelDescription = document.getElementById('info-panel-description');
    const infoPanelClose = document.getElementById('info-panel-close');

    // Function to clear all highlights from the court
    const resetCourt = () => {
        courtAreas.forEach(area => {
            area.classList.remove('highlighted-area');
        });
    };

    // Function to hide the info panel and reset the court
    const hideInfoPanel = () => {
        infoPanel.classList.add('info-panel-hidden');
        resetCourt();
    };
    
    // Function to update the info panel and court highlights
    const updateCourtView = (positionId) => {
        const data = positionData[positionId];
        if (!data) return;

        // Clear previous state
        resetCourt();

        // Highlight the new areas
        data.areas.forEach(areaId => {
            document.getElementById(areaId)?.classList.add('highlighted-area');
        });

        // Populate the info panel
        infoPanelTitle.textContent = `${data.name} (${positionId})`;
        infoPanelDescription.textContent = data.description;

        // Show the panel
        infoPanel.classList.remove('info-panel-hidden');
    };

    // Add a click event listener to each position button
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const positionId = button.dataset.position;
            updateCourtView(positionId);
        });
    });

    // Add a click listener to the close button
    infoPanelClose.addEventListener('click', hideInfoPanel);
});
