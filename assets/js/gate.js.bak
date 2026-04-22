/* =========================================================
   SHELL PORTAL GATE
   Isolated from DD portal — separate localStorage key,
   separate code, separate mechanism. A DD code leak cannot
   grant access here.
   ========================================================= */

(function () {
    'use strict';

    // NOTE: Code is hashed-ish via base64 + reversal. This is NOT
    // real security — it's a speed bump. The real protection is:
    //  1. Private subdomain (not linked from anywhere public)
    //  2. Code only shared with Shell via secure channel
    //  3. Separate storage key from DD portal so leaks don't cross
    //
    // Replace ACCESS_HASH below if code changes.
    // Current code: SHELL-SEA-2026
    // To generate a new hash in browser console:
    //   btoa('YOUR-CODE-HERE').split('').reverse().join('')

    var ACCESS_HASH = '=YjMwITLBV0UtwETFh0U';  // SHELL-SEA-2026
    var STORAGE_KEY = 'sm_shell_portal_access';
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
    window.ShellGate = {
        enforce: function () {
            if (sessionStorage.getItem(STORAGE_KEY) !== STORAGE_VALUE) {
                var current = window.location.pathname.split('/').pop() || 'index.html';
                if (current !== GATE_PATH) {
                    window.location.href = GATE_PATH;
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
            var ok = window.ShellGate.attempt(input.value);
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
