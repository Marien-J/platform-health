/**
 * Drag and Drop functionality for Platform Health Dashboard cards
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initDragAndDrop();
});

// Re-initialize after Dash updates the DOM
if (window.MutationObserver) {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                initDragAndDrop();
            }
        });
    });

    // Start observing once the document is ready
    document.addEventListener('DOMContentLoaded', function() {
        const container = document.getElementById('platform-cards');
        if (container) {
            observer.observe(container, { childList: true, subtree: true });
        }
    });
}

let draggedElement = null;
let draggedPlatformId = null;

function initDragAndDrop() {
    const container = document.getElementById('platform-cards');
    if (!container) return;

    const cards = container.querySelectorAll('.platform-card-wrapper');

    cards.forEach(function(card) {
        // Skip if already initialized
        if (card.dataset.dragInitialized) return;
        card.dataset.dragInitialized = 'true';

        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
        card.addEventListener('dragover', handleDragOver);
        card.addEventListener('dragenter', handleDragEnter);
        card.addEventListener('dragleave', handleDragLeave);
        card.addEventListener('drop', handleDrop);
    });
}

function handleDragStart(e) {
    draggedElement = this;
    draggedPlatformId = this.dataset.platformId;

    // Set drag data
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', draggedPlatformId);

    // Add dragging class after a small delay to prevent it from affecting the drag image
    setTimeout(function() {
        draggedElement.classList.add('dragging');
    }, 0);
}

function handleDragEnd(e) {
    this.classList.remove('dragging');

    // Remove all drag-over classes
    const cards = document.querySelectorAll('.platform-card-wrapper');
    cards.forEach(function(card) {
        card.classList.remove('drag-over', 'drag-over-left', 'drag-over-right');
    });

    draggedElement = null;
    draggedPlatformId = null;
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';

    // Determine if we're on the left or right half of the target
    if (this !== draggedElement) {
        const rect = this.getBoundingClientRect();
        const midpoint = rect.left + rect.width / 2;

        this.classList.remove('drag-over-left', 'drag-over-right');
        if (e.clientX < midpoint) {
            this.classList.add('drag-over-left');
        } else {
            this.classList.add('drag-over-right');
        }
    }

    return false;
}

function handleDragEnter(e) {
    if (this !== draggedElement) {
        this.classList.add('drag-over');
    }
}

function handleDragLeave(e) {
    this.classList.remove('drag-over', 'drag-over-left', 'drag-over-right');
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    if (e.preventDefault) {
        e.preventDefault();
    }

    if (this === draggedElement) {
        return false;
    }

    const container = document.getElementById('platform-cards');
    const cards = Array.from(container.querySelectorAll('.platform-card-wrapper'));

    const draggedIndex = cards.indexOf(draggedElement);
    const targetIndex = cards.indexOf(this);

    // Determine insert position based on mouse position
    const rect = this.getBoundingClientRect();
    const midpoint = rect.left + rect.width / 2;
    const insertBefore = e.clientX < midpoint;

    // Remove dragged element from current position
    draggedElement.parentNode.removeChild(draggedElement);

    // Insert at new position
    if (insertBefore) {
        this.parentNode.insertBefore(draggedElement, this);
    } else {
        this.parentNode.insertBefore(draggedElement, this.nextSibling);
    }

    // Update the card order in Dash store
    updateCardOrder();

    // Clean up classes
    this.classList.remove('drag-over', 'drag-over-left', 'drag-over-right');

    return false;
}

function updateCardOrder() {
    const container = document.getElementById('platform-cards');
    if (!container) return;

    const cards = container.querySelectorAll('.platform-card-wrapper');
    const newOrder = [];

    cards.forEach(function(card) {
        const platformId = card.dataset.platformId;
        if (platformId) {
            newOrder.push(platformId);
        }
    });

    // Update the Dash store via localStorage
    // Dash stores with storage_type='local' use localStorage
    const storeKey = 'card-order';
    localStorage.setItem(storeKey, JSON.stringify(newOrder));

    // Trigger a custom event to notify Dash of the change
    // This uses Dash's internal mechanism to update stores
    const storeElement = document.getElementById('card-order');
    if (storeElement) {
        // Dispatch a storage event to trigger Dash to re-read the store
        window.dispatchEvent(new StorageEvent('storage', {
            key: storeKey,
            newValue: JSON.stringify(newOrder)
        }));
    }
}
