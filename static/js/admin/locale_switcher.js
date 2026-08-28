/**
 * Admin locale switcher: UA | RU tabs.
 * Hides fields / formset columns by data-locale or name suffix _uk / _ru.
 */
(function () {
  function initRoot(root) {
    if (!root || root.dataset.localeReady === "1") return;
    root.dataset.localeReady = "1";

    var switcher = root.querySelector("[data-locale-switcher]");
    if (!switcher) return;

    var buttons = switcher.querySelectorAll("[data-locale]");
    var targets = root.querySelectorAll("[data-locale-field]");

    function apply(locale) {
      buttons.forEach(function (btn) {
        var active = btn.getAttribute("data-locale") === locale;
        btn.classList.toggle("is-active", active);
        btn.setAttribute("aria-pressed", active ? "true" : "false");
      });
      targets.forEach(function (el) {
        var loc = el.getAttribute("data-locale-field");
        el.hidden = loc !== locale && loc !== "all";
      });
      try {
        localStorage.setItem("qm_admin_locale", locale);
      } catch (e) {}
    }

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        apply(btn.getAttribute("data-locale"));
      });
    });

    var saved = "uk";
    try {
      saved = localStorage.getItem("qm_admin_locale") || "uk";
    } catch (e) {}
    apply(saved === "ru" ? "ru" : "uk");
  }

  function boot() {
    document.querySelectorAll("[data-locale-root]").forEach(initRoot);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
