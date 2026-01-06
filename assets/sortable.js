/**
 * SortableJS initialization for platform cards drag-and-drop
 */

// Initialize Sortable when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initSortable();
});

// Re-initialize when Dash updates the cards
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList' && mutation.target.id === 'platform-cards') {
            initSortable();
        }
    });
});

// Start observing once document is ready
document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('platform-cards');
    if (container) {
        observer.observe(container, { childList: true });
    }
});

let sortableInstance = null;

function initSortable() {
    const container = document.getElementById('platform-cards');
    if (!container || container.children.length === 0) return;

    // Destroy existing instance if any
    if (sortableInstance) {
        sortableInstance.destroy();
    }

    // Create new Sortable instance
    sortableInstance = new Sortable(container, {
        animation: 200,
        ghostClass: 'sortable-ghost',
        chosenClass: 'sortable-chosen',
        dragClass: 'sortable-drag',
        handle: '.platform-card-wrapper',
        onEnd: function(evt) {
            // Get new order from DOM
            const cards = container.querySelectorAll('.platform-card-wrapper');
            const newOrder = [];
            cards.forEach(function(card) {
                const platformId = card.getAttribute('data-platform-id');
                if (platformId) {
                    newOrder.push(platformId);
                }
            });

            // Update the Dash store via localStorage
            localStorage.setItem('card-order', JSON.stringify(newOrder));

            // Trigger storage event to notify other tabs and Dash
            window.dispatchEvent(new StorageEvent('storage', {
                key: 'card-order',
                newValue: JSON.stringify(newOrder)
            }));
        }
    });
}
