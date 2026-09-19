// stats_engine.js
const StatsEngine = {
    trackEvent: (event, details) => {
        const stats = JSON.parse(localStorage.getItem('sighub_stats') || '{"events": [], "archetypes": {}, "toggles": {}}');
        stats.events.push({ timestamp: new Date().toISOString(), event, details });
        
        if (event === 'archetype_selected') stats.archetypes[details] = (stats.archetypes[details] || 0) + 1;
        if (event === 'toggle_used') stats.toggles[details] = (stats.toggles[details] || 0) + 1;
        
        localStorage.setItem('sighub_stats', JSON.stringify(stats));
    },
    getReport: () => JSON.parse(localStorage.getItem('sighub_stats') || '{}')
};
