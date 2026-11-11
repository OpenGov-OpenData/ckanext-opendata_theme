/* Copy a URL to the clipboard from a button.
 *
 *   <button data-module="copy-url" data-module-url="https://..."
 *           data-module-copied="Copied!" data-module-failed="Copy failed">
 *     <span data-copy-label>Copy URL</span>
 *   </button>
 *   <span role="status" aria-live="polite" data-copy-status></span>   (optional, next sibling)
 */
this.ckan.module('copy-url', function ($) {
  return {
    options: {
      url: '',
      copied: 'Copied!',
      failed: 'Copy failed'
    },

    initialize: function () {
      $.proxyAll(this, /_on/);
      this.el.on('click', this._onClick);
    },

    _onClick: function (event) {
      event.preventDefault();
      var self = this;
      this._copy(this.options.url).then(function () {
        self._notify(self.options.copied);
      }, function () {
        self._notify(self.options.failed);
      });
    },

    _copy: function (text) {
      if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
      }
      // Fallback for non-secure contexts / older browsers.
      var d = $.Deferred();
      var $tmp = $('<textarea readonly></textarea>')
        .css({position: 'fixed', top: 0, left: 0, opacity: 0})
        .val(text).appendTo(document.body);
      $tmp[0].select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      $tmp.remove();
      if (ok) { d.resolve(); } else { d.reject(); }
      return d.promise();
    },

    _notify: function (message) {
      var $label = this.el.find('[data-copy-label]');
      var original = this._original || (this._original = $label.text());
      $label.text(message);
      this.el.siblings('[data-copy-status]').text(message);
      clearTimeout(this._timer);
      this._timer = setTimeout(function () {
        $label.text(original);
      }, 2000);
    }
  };
});
