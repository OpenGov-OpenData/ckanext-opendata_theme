// Close popover on pressing Escape key
$(document).on('keydown', function (e) {
  if (e.key === "Escape") {
    $('.popover').each(function () {
      $(this).popover('hide');
      $(this).data('bs.popover').inState.click = false;
    });
  }
});

this.ckan.module('resource-view-embed', function ($) {
  var modal;
  var self;

  function initialize() {
    self = this;
    modal = $('#embed-'+this.options.id)
    $('body').append(modal);
    this.el.on('click', _onClick);
    $('textarea', modal).on('focus', _selectAllCode).on('mouseup', _preventClick);
    $('input', modal).on('keyup change', _updateValues);
    _updateEmbedCode();

    // Trap focus when modal is shown
    modal.on('shown.bs.modal', _trapFocus);
    modal.on('hidden.bs.modal', _restoreFocus);
  }

  function _onClick (event) {
    event.preventDefault();
    modal.modal('show');
  }

  function _selectAllCode () {
    $('textarea', modal).select();
  }

  function _updateValues () {
    self.options.width = $('[name="width"]', modal).val();
    self.options.height = $('[name="height"]', modal).val();
    _updateEmbedCode();
  }

  function _updateEmbedCode () {
    $('[name="code"]', modal).val(_embedCode());
  }

  function _preventClick (event) {
    event.preventDefault();
  }

  function _embedCode () {
    return '<iframe width="' + self.options.width + '" height="' + self.options.height + '" src="' + self.options.url + '" frameBorder="0"></iframe>';
  }

  // Trap focus
  function _trapFocus() {
    const focusableElements = modal.find('a, button, input, textarea');
    const firstElement = focusableElements.first();
    const lastElement = focusableElements.last();

    modal.on('keydown', function (e) {
      if (e.key === 'Tab') {
        if (e.shiftKey) { // Shift + Tab
          if (document.activeElement === firstElement[0]) {
            e.preventDefault();
            lastElement.focus();
          }
        } else { // Tab
          if (document.activeElement === lastElement[0]) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    });

    // Move focus to the modal
    firstElement.focus();
  }

  function _restoreFocus() {
    modal.off('keydown');
  }

  return {
    initialize: initialize,
    options: {
      id: 0,
      url: '#',
      width: 700,
      height: 400
    }
  }
});
