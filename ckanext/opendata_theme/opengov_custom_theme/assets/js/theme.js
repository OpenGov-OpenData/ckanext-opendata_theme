/**
 * CKAN resource-view-filters-form applies Select2 3.x to the filter value input.
 * Select2 sets aria-labelledby on .select2-focusser to the displayed value, so the
 * native input's aria-label is ignored. Sync label onto the focusser after init.
 */
function syncResourceViewFilterValueSelect2A11y($root) {
  $root.find('.resource-view-filters input[name="filter_values"]').each(function () {
    var $input = $(this);
    var label = $input.attr('aria-label');
    if (!label) {
      return;
    }
    // Select2 inserts the container immediately before the original input
    var $container = $input.prev('.select2-container');
    if (!$container.length) {
      return;
    }
    var $focusser = $container.find('input.select2-focusser');
    if ($focusser.length) {
      $focusser.removeAttr('aria-labelledby');
      $focusser.attr('aria-label', label);
    }
  });
}

function setupResourceViewFilterValueSelect2A11y() {
  var forms = document.querySelectorAll('[data-module="resource-view-filters-form"]');
  if (!forms.length) {
    return;
  }
  Array.prototype.forEach.call(forms, function (formEl) {
    var $form = $(formEl);
    var filtersEl = formEl.querySelector('.resource-view-filters');
    if (!filtersEl) {
      return;
    }
    var run = function () {
      syncResourceViewFilterValueSelect2A11y($form);
    };
    run();
    var mo = new MutationObserver(function () {
      window.requestAnimationFrame(run);
    });
    mo.observe(filtersEl, { childList: true, subtree: true });
  });
  // CKAN modules may init after this script's ready handler
  $(window).on('load', function () {
    Array.prototype.forEach.call(forms, function (formEl) {
      syncResourceViewFilterValueSelect2A11y($(formEl));
    });
  });
}

/**
 * Enter on Select2 filter value controls triggers implicit form submission (first submit
 * button, often Delete). Intercept Enter inside .resource-view-filters: open Select2 or
 * native field select instead. Select2 3 attaches the open dropdown to body, so key
 * events from the list do not match this delegate and keep default behavior.
 */
function setupResourceViewFiltersEnterKey() {
  $(document).on('keydown.resourceViewFiltersEnter', '[data-module="resource-view-filters-form"]', function (e) {
    if (e.key !== 'Enter' && e.which !== 13) {
      return;
    }
    var target = e.target;
    if (!target || target.nodeType !== 1) {
      return;
    }
    var filtersRoot = this.querySelector('.resource-view-filters');
    if (!filtersRoot || !filtersRoot.contains(target)) {
      return;
    }
    if (target.tagName === 'SELECT') {
      e.preventDefault();
      e.stopPropagation();
      if (typeof target.showPicker === 'function') {
        try {
          target.showPicker();
        } catch (ignore) {
          target.dispatchEvent(new KeyboardEvent('keydown', { key: ' ', code: 'Space', keyCode: 32, bubbles: true }));
        }
      } else {
        target.dispatchEvent(new KeyboardEvent('keydown', { key: ' ', code: 'Space', keyCode: 32, bubbles: true }));
      }
      return;
    }
    var $container = $(target).closest('.select2-container');
    if ($container.length && filtersRoot.contains($container[0])) {
      var $input = $container.next('input[name="filter_values"]');
      if (!$input.length) {
        $input = $container.parent().find('input[name="filter_values"]');
      }
      e.preventDefault();
      e.stopPropagation();
      if ($input.length && $input.data('select2')) {
        $input.select2('open');
      }
      return;
    }
    if (target.tagName === 'INPUT' && target.getAttribute('name') === 'filter_values') {
      e.preventDefault();
      e.stopPropagation();
      var $inp = $(target);
      if ($inp.data('select2')) {
        $inp.select2('open');
      }
    }
  });
}

$(document).ready(function () {
  setupResourceViewFilterValueSelect2A11y();
  setupResourceViewFiltersEnterKey();
});

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

// Dataset page primary nav: ARIA tablist and arrow-key navigation
$(document).ready(function () {
  var pathname = window.location.pathname || '';
  if (pathname.indexOf('/dataset/') !== 0) {
    return;
  }
  var $tablist = $('.module-content.page-header ul.nav.nav-tabs');
  if (!$tablist.length) {
    return;
  }

  $tablist.attr('role', 'tablist');
  var $tabs = $tablist.find('> li > a');
  $tablist.find('> li').attr('role', 'presentation');
  $tabs.attr('role', 'tab');

  function setRovingTabindex() {
    var currentPath = pathname.replace(/\/$/, '');
    $tabs.each(function () {
      var $a = $(this);
      var href = $a.attr('href') || '';
      var tabPath = href.replace(/^https?:\/\/[^/]+/, '').replace(/\/$/, '');
      var isActive = $a.closest('li').hasClass('active') || tabPath === currentPath;
      $a.attr('tabindex', isActive ? '0' : '-1');
      $a.attr('aria-selected', isActive ? 'true' : 'false');
    });
  }
  setRovingTabindex();

  $tablist.on('keydown', function (e) {
    var $target = $(e.target);
    if ($target.attr('role') !== 'tab' || !$target.closest($tablist).length) {
      return;
    }
    var key = e.key;
    if (key !== 'ArrowLeft' && key !== 'ArrowRight' && key !== 'Home' && key !== 'End') {
      return;
    }
    e.preventDefault();
    var index = $tabs.index($target);
    if (key === 'ArrowRight') {
      index = index < $tabs.length - 1 ? index + 1 : 0;
    } else if (key === 'ArrowLeft') {
      index = index > 0 ? index - 1 : $tabs.length - 1;
    } else if (key === 'Home') {
      index = 0;
    } else if (key === 'End') {
      index = $tabs.length - 1;
    }
    $tabs.attr('tabindex', '-1');
    var $next = $tabs.eq(index);
    $next.attr('tabindex', '0').focus();
  });
});

// Sidebar menu: keyboard (Enter/Escape), focus first link when opened, skip tab when closed
$(document).ready(function () {
  var $menuTrigger = $('#hb__trigger');
  var $navLabel = $('label[for="hb__trigger"]');

  if (!$menuTrigger.length) return;

  function setSidebarFocusable(focusable) {
    var $nav = $('.main-navigation');
    var $focusables = $nav.find('a, button');
    if (focusable) {
      $nav.removeAttr('aria-hidden');
      $focusables.removeAttr('tabindex');
    } else {
      $nav.attr('aria-hidden', 'true');
      $focusables.attr('tabindex', '-1');
    }
  }

  function focusSidebarFirstLink() {
    var $nav = $('.main-navigation');
    var $firstLink = $nav.find('.menu a').first();
    if (!$firstLink.length) {
      $firstLink = $nav.find('a').first();
    }
    if (!$firstLink.length) return;
    setTimeout(function () {
      requestAnimationFrame(function () {
        $firstLink[0].focus();
      });
    }, 400);
  }

  function openSidebar() {
    $menuTrigger.prop('checked', true);
    setSidebarFocusable(true);
    focusSidebarFirstLink();
  }

  function closeSidebar() {
    var focusWasInside = $('.main-navigation').has(document.activeElement).length > 0;
    $menuTrigger.prop('checked', false);
    setSidebarFocusable(false);
    if (focusWasInside) {
      $navLabel.focus();
    }
  }

  // Set initial tab order based on whether the sidebar starts open
  setSidebarFocusable($menuTrigger.prop('checked'));

  // Enter toggles the sidebar; Escape closes it
  $navLabel.on('keydown', function (event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      if ($menuTrigger.prop('checked')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    }
  });

  $(document).on('keydown', function (event) {
    if (event.key === 'Escape' && $menuTrigger.prop('checked')) {
      closeSidebar();
    }
  });

  // Handle click (label click fires a change event on the checkbox)
  $menuTrigger.on('change', function () {
    if ($(this).prop('checked')) {
      setSidebarFocusable(true);
      focusSidebarFirstLink();
    } else {
      closeSidebar();
    }
  });
});