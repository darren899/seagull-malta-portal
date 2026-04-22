/* =========================================================
   MALTA PORTAL GATE
   Isolated from DD / Shell portals — separate localStorage
   key, separate code. A DD or Shell code leak cannot grant
   access here.
   ========================================================= */

(function () {
    'use strict';

    // NOTE: Code is obfuscated via base64 + reversal. This is NOT
    // real security — it's a speed bump. The real protection is:
    //  1. Private subdomain (not linked from anywhere public)
    //  2. Code only shared via secure channel
    //  3. Separate storage key from other portals so leaks don't cross
    //
    // Replace ACCESS_HASH below if code changes.
    // Current code: MALTA-SEA-2026
    // To generate a new hash in browser console:
    //   btoa('YOUR-CODE-HERE').split('').reverse().join('')

    var ACCESS_HASH = '=YjMwITLBV0UtEEVMFUT';  // MALTA-SEA-2026
    var STORAGE_KEY = 'sm_malta_portal_access';
    var STORAGE_VALUE = 'granted';
    var GATE_PATH = 'gate.html';

    function hashCode(str) {
        try {
            return btoa(str.toUpperCase().trim()).split('').reverse().join('');
        } catch (e) {
            return '';
        }
    }

    // --- Entry: redirect to gate if not authorised ---
    window.MaltaGate = {
        enforce: function () {
            if (sessionStorage.getItem(STORAGE_KEY) !== STORAGE_VALUE) {
                var current = window.location.pathname.split('/').pop() || 'index.html';
                if (current !== GATE_PATH) {
                    window.location.href = 'gate.html';
                }
            }
        },

        attempt: function (code) {
            if (hashCode(code) === ACCESS_HASH) {
                sessionStorage.setItem(STORAGE_KEY, STORAGE_VALUE);
                return true;
            }
            return false;
        },

        clear: function () {
            sessionStorage.removeItem(STORAGE_KEY);
        }
    };

    // --- Gate page UI wiring ---
    document.addEventListener('DOMContentLoaded', function () {
        var form = document.getElementById('gate-form');
        if (!form) return;

        var input = document.getElementById('gate-code');
        var error = document.getElementById('gate-error');

        form.addEventListener('submit', function (ev) {
            ev.preventDefault();
            var ok = window.MaltaGate.attempt(input.value);
            if (ok) {
                error.classList.remove('is-visible');
                window.location.href = 'index.html';
            } else {
                error.classList.add('is-visible');
                input.value = '';
                input.focus();
            }
        });
    });
})();
