/* Keyboard-accessible reordering for resource and resource-view lists.
 *
 * Works alongside the existing jQuery UI Sortable modules (resource-reorder,
 * resource-view-reorder).  Attach to the same container element via
 * data-module="resource-reorder keyboard-reorder".
 *
 * Interaction model
 * -----------------
 * 1. The existing module adds the class .reordering when reorder mode is
 *    enabled.  A MutationObserver detects this and sets up keyboard support.
 * 2. With reorder mode active the user can Tab to a .handle element and press
 *    Enter to begin keyboard reordering for that item.
 * 3. Arrow Up / Arrow Down moves the item; Enter confirms; Escape cancels.
 * 4. A visually-hidden aria-live region announces every state change.
 */
this.ckan.module('keyboard-reorder', function ($) {
  return {
    options: {},

    /* ── state ────────────────────────────────────────────────── */
    _isReorderMode: false,   // an item is actively being keyboard-moved
    _activeItem: null,       // jQuery <li> currently being moved
    _originalNextSibling: null, // DOM node that followed the item before move
    _liveRegion: null,       // aria-live announcement element
    _observer: null,         // MutationObserver for .reordering class
    _reorderEnabled: false,  // tracks whether the container has .reordering

    /* ── lifecycle ────────────────────────────────────────────── */

    initialize: function () {
      $.proxyAll(this, /_on/);

      this._liveRegion = $(
        '<div class="sr-only" aria-live="polite" aria-atomic="true"></div>'
      ).appendTo(document.body);

      this._instructionsId = 'keyboard-reorder-instructions-' + Date.now();
      this._instructions = $(
        '<div id="' + this._instructionsId + '" class="sr-only">' +
        'Press Enter on a handle to start reordering. ' +
        'Use Arrow Up and Arrow Down to move. ' +
        'Press Enter to confirm or Escape to cancel.' +
        '</div>'
      ).appendTo(document.body);

      this.el.attr('aria-describedby', this._instructionsId);

      this._observer = new MutationObserver(this._onClassMutation);
      this._observer.observe(this.el[0], {
        attributes: true,
        attributeFilter: ['class']
      });

      this.el.on('keydown.keyboardReorder', this._onKeydown);

      // In case .reordering is already present when the module initialises
      if (this.el.hasClass('reordering')) {
        this._enableKeyboardReorder();
      }
    },

    teardown: function () {
      if (this._observer) {
        this._observer.disconnect();
      }
      this._disableKeyboardReorder();
      this.el.off('.keyboardReorder');
      if (this._liveRegion) {
        this._liveRegion.remove();
      }
      if (this._instructions) {
        this._instructions.remove();
      }
    },

    /* ── reorder-mode detection ───────────────────────────────── */

    _onClassMutation: function () {
      var hasClass = this.el.hasClass('reordering');
      if (hasClass && !this._reorderEnabled) {
        this._enableKeyboardReorder();
      } else if (!hasClass && this._reorderEnabled) {
        this._disableKeyboardReorder();
      }
    },

    _enableKeyboardReorder: function () {
      this._reorderEnabled = true;
      var $items = this._getItems();

      $items.attr('role', 'listitem');

      // Disable links inside items so Tab stays on the handles
      $items.find('a').not('.handle').attr('tabindex', '-1');

      // Label each handle with the item's visible name so screen readers
      // announce something meaningful instead of an empty link.
      var $handles = $items.find('.handle');
      $handles.each(function () {
        var $handle = $(this);
        var $item = $handle.closest('li');
        var name = $item.find('.heading').text().trim() ||
                   $item.find('a').first().text().trim() ||
                   'item';
        $handle.attr({
          'aria-label': 'Reorder ' + name,
          'role': 'button'
        });
      });

      // Roving tabindex on handles: first handle is tabbable, rest are not
      $handles.attr('tabindex', '-1');
      $handles.first().attr('tabindex', '0');
    },

    _disableKeyboardReorder: function () {
      if (this._isReorderMode) {
        this._cancelReorder();
      }
      this._reorderEnabled = false;

      var $items = this._getItems();
      $items.removeAttr('role');
      $items.find('a').not('.handle').removeAttr('tabindex');
      $items.find('.handle').removeAttr('tabindex').removeAttr('aria-label').removeAttr('role');
      $items.removeClass('keyboard-reorder-active');
    },

    /* ── keyboard handling ────────────────────────────────────── */

    _onKeydown: function (e) {
      if (!this._reorderEnabled) {
        return;
      }

      var key = e.key;

      // Enter on a .handle starts reorder mode for that item
      if (
        key === 'Enter' &&
        !this._isReorderMode &&
        $(e.target).hasClass('handle')
      ) {
        e.preventDefault();
        this._startReorder($(e.target).closest('li'));
        return;
      }

      if (!this._isReorderMode) {
        // When not in reorder mode, support roving tabindex navigation
        if (key === 'ArrowUp' || key === 'ArrowDown') {
          var $focused = $(e.target).closest('li');
          if ($focused.length && this.el.has($focused).length) {
            e.preventDefault();
            this._rovingMove($focused, key === 'ArrowUp' ? -1 : 1);
          }
        }
        return;
      }

      // While in reorder mode, key events apply to the active item
      switch (key) {
        case 'ArrowUp':
          e.preventDefault();
          this._moveItem(-1);
          break;
        case 'ArrowDown':
          e.preventDefault();
          this._moveItem(1);
          break;
        case 'Enter':
          e.preventDefault();
          this._confirmReorder();
          break;
        case 'Escape':
          e.preventDefault();
          this._cancelReorder();
          break;
      }
    },

    /* ── roving tabindex (when reorder mode is NOT active) ───── */

    _rovingMove: function ($currentItem, direction) {
      var $items = this._getItems();
      var idx = $items.index($currentItem);
      var newIdx = idx + direction;

      if (newIdx < 0 || newIdx >= $items.length) {
        return;
      }

      // Move roving tabindex across all handles
      var $allHandles = $items.find('.handle');
      $allHandles.attr('tabindex', '-1');

      var $nextHandle = $items.eq(newIdx).find('.handle');
      if ($nextHandle.length) {
        $nextHandle.attr('tabindex', '0').focus();
      }
    },

    /* ── keyboard reorder operations ──────────────────────────── */

    _startReorder: function ($item) {
      this._isReorderMode = true;
      this._activeItem = $item;

      // Remember the next sibling so we can restore on cancel
      this._originalNextSibling = $item[0].nextElementSibling;

      $item.addClass('keyboard-reorder-active');

      this._announce(
        'Reordering started. Use arrow keys to move. ' +
        'Press Escape to cancel, Enter to save.'
      );
    },

    _moveItem: function (direction) {
      var $item = this._activeItem;
      var $items = this._getItems();
      var currentIndex = $items.index($item);
      var targetIndex = currentIndex + direction;

      if (targetIndex < 0 || targetIndex >= $items.length) {
        return;
      }

      var $target = $items.eq(targetIndex);

      if (direction < 0) {
        $item.insertBefore($target);
      } else {
        $item.insertAfter($target);
      }

      // Update roving tabindex and keep focus on the moved item's handle
      var $allHandles = this._getItems().find('.handle');
      $allHandles.attr('tabindex', '-1');
      var $handle = $item.find('.handle');
      $handle.attr('tabindex', '0').focus();

      var updatedItems = this._getItems();
      var newPosition = updatedItems.index($item) + 1;

      this._announce(
        'Moved to position ' + newPosition + ' of ' + updatedItems.length
      );
    },

    _confirmReorder: function () {
      var $item = this._activeItem;

      this._isReorderMode = false;
      this._activeItem = null;
      this._originalNextSibling = null;

      if ($item) {
        $item.removeClass('keyboard-reorder-active');
        $item.find('.handle').focus();
      }

      this._announce('Order saved');
    },

    _cancelReorder: function () {
      var $item = this._activeItem;

      this._isReorderMode = false;
      this._activeItem = null;

      if ($item) {
        $item.removeClass('keyboard-reorder-active');

        // Restore original position
        if (this._originalNextSibling) {
          $item.insertBefore(this._originalNextSibling);
        } else {
          // Was the last item — append to end
          this.el.append($item);
        }

        // Update roving tabindex and return focus to the handle
        var $allHandles = this._getItems().find('.handle');
        $allHandles.attr('tabindex', '-1');
        $item.find('.handle').attr('tabindex', '0').focus();
      }

      this._originalNextSibling = null;
      this._announce('Reordering cancelled');
    },

    /* ── helpers ───────────────────────────────────────────────── */

    _getItems: function () {
      return this.el.children('li');
    },

    /**
     * Update the aria-live region. Uses a clear-then-set pattern so that
     * repeated identical messages are still announced.
     */
    _announce: function (message) {
      var region = this._liveRegion;
      region.text('');
      setTimeout(function () {
        region.text(message);
      }, 50);
    }
  };
});
