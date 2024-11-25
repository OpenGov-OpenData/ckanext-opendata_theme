// Close popover on pressing Escape key
$(document).on('keydown', function (e) {
  if (e.key === "Escape") {
    $('.popover').each(function () {
      $(this).popover('hide');
      $(this).data('bs.popover').inState.click = false;
    });
  }
});

// Trap focus inside api-info modal
$(document).ready(function () {
  $('a[data-module="api-info"]').on('click', function () {
    trapApiInfoEmbed();
  });

  $('a[data-module="api-info"]').on('keyup', function (e) {
    if (e.key === 'Enter') {
      trapApiInfoEmbed();
    }
  });

  function trapApiInfoEmbed() {
    const modal = $(`#api-info-embed`);
    if (modal.length) {
      // Trap focus within the modal
      trapFocus(modal);
      // When closed remove event handlers
      modal.find('.close').on('click', function () {
        modal.off('keydown');
        $('[data-module="api-info"]').focus();
      });
    }
  }
});

// Trap focus inside resource-view-embed modal
$(document).ready(function () {
  $('a[data-module="resource-view-embed"]').on('click', function () {
    const modalId = $(this).data('module-id');
    trapResourceViewEmbed(modalId);
  });

  $('a[data-module="resource-view-embed"]').on('keyup', function (e) {
    if (e.key === 'Enter') {
      const modalId = $(this).data('module-id');
      trapResourceViewEmbed(modalId);
    }
  });

  function trapResourceViewEmbed(modalId) {
    const modal = $(`#embed-${modalId}`);
    if (modal.length) {
      // Trap focus within the modal
      trapFocus(modal);
      // When closed remove event handlers
      modal.find('.close').on('click', function () {
        modal.off('keydown');
        $('[data-module="resource-view-embed"]').focus();
      });
    }
  }
});

function trapFocus(modal) {
  const focusableElements = modal.find('a, button, input, textarea');
  const firstElement = focusableElements.first();
  const lastElement = focusableElements.last();

  // Focus on first element when the modal opens
  modal.on('shown.bs.modal', function () {
    firstElement.focus();
  });

  modal.on('keydown', function (e) {
    if (e.key === 'Tab') {
      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement[0]) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement[0]) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    }
  });
}