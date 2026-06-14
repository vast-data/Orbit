/* theme_dark_default.js — VastOrbit docs theme policy:
 *   1. Default theme is DARK (first visit, or any stale "auto" state).
 *   2. The sun/moon toggle switches strictly dark <-> light. No "auto".
 *
 * Why a script: Furo has no config for either behavior — its toggle is
 * hardwired to cycle auto -> light -> dark and defaults to auto.
 *
 * Install: save to _static/js/theme_dark_default.js and add
 * "js/theme_dark_default.js" to html_js_files in conf.py (order with the
 * other entries does not matter; part 1 runs at parse time in <head>,
 * before Furo's body script applies the theme, so there is no light flash).
 */

/* 1 ── Default to dark, and convert any lingering "auto" to dark.
       Runs synchronously while the <head> is parsed — before first paint. */
(function () {
  try {
    var t = localStorage.getItem("theme");
    if (t === null || t === "auto") {
      localStorage.setItem("theme", "dark");
    }
  } catch (e) {
    /* localStorage unavailable (private mode + strict settings): Furo will
       fall back to auto; nothing else we can safely do. */
  }
})();

/* 2 ── Two-state toggle: intercept the theme button in the CAPTURE phase,
       before Furo's own click handler, and flip dark <-> light directly. */
document.addEventListener(
  "click",
  function (e) {
    var btn = e.target.closest ? e.target.closest(".theme-toggle") : null;
    if (!btn) return;
    e.preventDefault();
    e.stopImmediatePropagation(); /* Furo's auto-cycling handler never runs */

    var next = document.body.dataset.theme === "light" ? "dark" : "light";
    document.body.dataset.theme = next;
    try {
      localStorage.setItem("theme", next);
    } catch (e2) {}
  },
  true /* capture phase = we run before Furo's bubbling listener */
);