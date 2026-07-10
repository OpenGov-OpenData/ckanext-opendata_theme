/* Client-side success flash for the data dictionary edit form.
 *
 * Why this exists
 * ---------------
 * Saving the data dictionary does a POST -> h.flash_success() -> 302 redirect
 * back to the same URL (Post/Redirect/Get).  When CKAN runs across multiple
 * Kubernetes pods with non-shared sessions, the flash cookie set by the pod
 * that handled the POST is often not read by the pod that serves the redirect
 * GET, so the success message is lost until a later navigation.
 *
 * This module is a pod-routing-agnostic STOPGAP: on submit it records a flag in
 * sessionStorage, and on the next page load it renders the success alert itself
 * -- but only if the server-side flash isn't already present.  Once the real
 * shared-session fix lands, the server flash shows up, guard #3 suppresses this
 * one, and the module can be removed cleanly.
 *
 * Attach via a marker element inside the dictionary <form>:
 *   <span data-module="data-dict-flash" data-module-message="..."></span>
 */
this.ckan.module('data-dict-flash', function ($) {
  return {
    options: {
      message: ''
    },

    /* ── state ────────────────────────────────────────────────── */
    _key: null,      // sessionStorage key, scoped to this dictionary URL
    _$form: null,    // the enclosing dictionary <form>

    /* Time within which a stored flag is trusted as "just submitted".
     * A PRG redirect completes in ~1-2s; 10s leaves headroom while bounding
     * the residual false-positive (POST fails, user manually navigates back
     * to the GET URL while the flag is still live).  This cannot be fully
     * eliminated client-side without server cooperation -- accepted trade-off
     * for a temporary stopgap. */
    FRESHNESS_MS: 10000,

    /* ── lifecycle ────────────────────────────────────────────── */

    initialize: function () {
      $.proxyAll(this, /_on/);

      this._key = 'ckanext-opendata:data-dict-flash:' + window.location.pathname;

      // Read-then-clear: pull the stored value, then remove it immediately so a
      // flag never survives into an unrelated later reload, regardless of
      // whether we decide to render below.
      var raw = this._read();
      this._clear();

      this._$form = this.el.closest('form');
      if (this._$form.length) {
        this._$form.on('submit.dataDictFlash', this._onSubmit);
      }

      if (this._shouldRender(raw)) {
        this._renderSuccess();
      }
    },

    teardown: function () {
      if (this._$form && this._$form.length) {
        this._$form.off('.dataDictFlash');
      }
      this._$form = null;
      // Intentionally leave any rendered alert in place.
    },

    /* ── submit handling ──────────────────────────────────────── */

    _onSubmit: function () {
      // There is a single `save` button; binding at form level also covers
      // Enter-to-submit.
      this._write({ t: Date.now() });
    },

    /* ── render decision ──────────────────────────────────────── */

    /* Render the synthetic success alert only if ALL guards hold. */
    _shouldRender: function (payload) {
      // 1. Flag present and parseable.
      if (!payload || typeof payload.t !== 'number') {
        return false;
      }

      // 2. Freshness window.
      if (Date.now() - payload.t > this.FRESHNESS_MS) {
        return false;
      }

      // 3. Server-flash dedupe: if the server already rendered a success flash
      //    (i.e. the shared-session fix has landed), do nothing.
      if ($('.flash-messages .alert-success').length) {
        return false;
      }

      // 4. Error-markup guard: never claim success when the page shows errors.
      if ($('.error-explanation, .alert-danger, .alert-error, .control-group.error').length) {
        return false;
      }

      return true;
    },

    _renderSuccess: function () {
      var $container = $('.flash-messages');
      // Core always renders this container; treat absence as purely defensive.
      if (!$container.length) {
        return;
      }

      var $alert = $('<div class="alert fade in alert-success" role="alert"></div>')
        .text(this.options.message);

      $container.append($alert);

      // Pass through core's notify helper so the alert gets the same dismiss
      // button and Bootstrap wiring as server-rendered flashes. It lives on the
      // module sandbox (notify.js does ckan.sandbox.extend({notify: notify})).
      if (this.sandbox.notify && this.sandbox.notify.initialize) {
        this.sandbox.notify.initialize($alert);
      }
    },

    /* ── sessionStorage helpers (defensive against disabled storage) ─ */

    _read: function () {
      try {
        var raw = window.sessionStorage.getItem(this._key);
        return raw ? JSON.parse(raw) : null;
      } catch (e) {
        return null;
      }
    },

    _write: function (payload) {
      try {
        window.sessionStorage.setItem(this._key, JSON.stringify(payload));
      } catch (e) {
        // Storage unavailable/full: nothing to do -- stopgap simply no-ops.
      }
    },

    _clear: function () {
      try {
        window.sessionStorage.removeItem(this._key);
      } catch (e) {
        // ignore
      }
    }
  };
});
