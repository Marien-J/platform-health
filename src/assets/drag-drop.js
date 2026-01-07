/**
 * Drag and Drop functionality for Platform Cards
 * Allows users to reorder platform cards by dragging and dropping them.
 */

(function() {
    'use strict';

    let draggedElement = null;
    let draggedPlatformId = null;

    /**
     * Initialize drag and drop after Dash has rendered the cards
     */
    function initDragDrop() {
        const container = document.querySelector('.platform-cards-container');
        if (!container) {
            // Container not ready yet, retry later
            setTimeout(initDragDrop, 100);
            return;
        }

        // Remove existing listeners to avoid duplicates
        container.removeEventListener('dragstart', handleDragStart);
        container.removeEventListener('dragend', handleDragEnd);
        container.removeEventListener('dragover', handleDragOver);
        container.removeEventListener('drop', handleDrop);
        container.removeEventListener('dragleave', handleDragLeave);

        // Add event listeners to container (event delegation)
        container.addEventListener('dragstart', handleDragStart);
        container.addEventListener('dragend', handleDragEnd);
        container.addEventListener('dragover', handleDragOver);
        container.addEventListener('drop', handleDrop);
        container.addEventListener('dragleave', handleDragLeave);
    }

    /**
     * Handle drag start event
     */
    function handleDragStart(e) {
        const card = e.target.closest('.platform-card-wrapper');
        if (!card) return;

        draggedElement = card;
        draggedPlatformId = card.getAttribute('data-platform-id');

        // Set drag data
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', draggedPlatformId);

        // Add dragging class after a small delay to ensure the drag image is captured
        setTimeout(() => {
            card.classList.add('dragging');
        }, 0);
    }

    /**
     * Handle drag end event
     */
    function handleDragEnd(e) {
        if (draggedElement) {
            draggedElement.classList.remove('dragging');
        }

        // Remove all drag-over classes
        document.querySelectorAll('.platform-card-wrapper').forEach(card => {
            card.classList.remove('drag-over', 'drag-over-left', 'drag-over-right');
        });

        draggedElement = null;
        draggedPlatformId = null;
    }

    /**
     * Handle drag over event
     */
    function handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';

        const card = e.target.closest('.platform-card-wrapper');
        if (!card || card === draggedElement) return;

        // Get card position info
        const rect = card.getBoundingClientRect();
        const midpoint = rect.left + rect.width / 2;
        const isLeftHalf = e.clientX < midpoint;

        // Remove previous indicators from all cards
        document.querySelectorAll('.platform-card-wrapper').forEach(c => {
            c.classList.remove('drag-over', 'drag-over-left', 'drag-over-right');
        });

        // Add indicator to current card
        card.classList.add('drag-over');
        if (isLeftHalf) {
            card.classList.add('drag-over-left');
        } else {
            card.classList.add('drag-over-right');
        }
    }

    /**
     * Handle drag leave event
     */
    function handleDragLeave(e) {
        const card = e.target.closest('.platform-card-wrapper');
        if (card && !card.contains(e.relatedTarget)) {
            card.classList.remove('drag-over', 'drag-over-left', 'drag-over-right');
        }
    }

    /**
     * Handle drop event
     */
    function handleDrop(e) {
        e.preventDefault();

        const targetCard = e.target.closest('.platform-card-wrapper');
        if (!targetCard || !draggedElement || targetCard === draggedElement) {
            handleDragEnd(e);
            return;
        }

        const container = document.querySelector('.platform-cards-container');
        const cards = Array.from(container.querySelectorAll('.platform-card-wrapper'));

        // Determine drop position (left or right of target)
        const rect = targetCard.getBoundingClientRect();
        const midpoint = rect.left + rect.width / 2;
        const insertBefore = e.clientX < midpoint;

        // Calculate new order
        const currentOrder = cards.map(card => card.getAttribute('data-platform-id'));
        const draggedIndex = currentOrder.indexOf(draggedPlatformId);
        const targetId = targetCard.getAttribute('data-platform-id');
        let targetIndex = currentOrder.indexOf(targetId);

        // Remove dragged item from array
        currentOrder.splice(draggedIndex, 1);

        // Adjust target index if needed (since we removed an item)
        if (draggedIndex < targetIndex) {
            targetIndex--;
        }

        // Insert at new position
        if (insertBefore) {
            currentOrder.splice(targetIndex, 0, draggedPlatformId);
        } else {
            currentOrder.splice(targetIndex + 1, 0, draggedPlatformId);
        }

        // Update the Dash store
        updateCardOrder(currentOrder);

        // Reorder cards visually immediately (optimistic UI)
        reorderCardsVisually(currentOrder);

        handleDragEnd(e);
    }

    /**
     * Update the card-order store in Dash by triggering the clientside callback
     */
    function updateCardOrder(newOrder) {
        const triggerEl = document.getElementById('drag-drop-trigger');
        if (triggerEl) {
            // Store the new order in the data attribute
            triggerEl.setAttribute('data-order', JSON.stringify(newOrder));

            // Trigger the Dash callback by clicking the element
            triggerEl.click();
        }
    }

    /**
     * Reorder cards visually without waiting for Dash callback
     */
    function reorderCardsVisually(newOrder) {
        const container = document.querySelector('.platform-cards-container');
        if (!container) return;

        const cards = Array.from(container.querySelectorAll('.platform-card-wrapper'));
        const cardsMap = {};
        cards.forEach(card => {
            cardsMap[card.getAttribute('data-platform-id')] = card;
        });

        // Reorder cards in DOM
        newOrder.forEach(platformId => {
            const card = cardsMap[platformId];
            if (card) {
                container.appendChild(card);
            }
        });
    }

    // Initialize on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDragDrop);
    } else {
        initDragDrop();
    }

    // Re-initialize when Dash updates the cards
    // Use MutationObserver to detect when cards are re-rendered
    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.type === 'childList' && mutation.target.classList.contains('platform-cards-container')) {
                // Cards were updated, reinitialize drag handlers
                initDragDrop();
                break;
            }
        }
    });

    // Start observing once the document is ready
    function startObserver() {
        const container = document.querySelector('.platform-cards-container');
        if (container) {
            observer.observe(container, { childList: true, subtree: false });
        } else {
            setTimeout(startObserver, 100);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startObserver);
    } else {
        startObserver();
    }
})();
