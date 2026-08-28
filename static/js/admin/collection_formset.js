/**
 * Add another item to CMS About / FAQ ModelFormSets.
 */
(function () {
  function nextIndex(totalInput) {
    var n = parseInt(totalInput.value, 10);
    return Number.isFinite(n) ? n : 0;
  }

  function refreshLocale(root) {
    var switcher = root && root.querySelector("[data-locale-switcher]");
    if (!switcher) return;
    var active = switcher.querySelector("[data-locale].is-active");
    var locale = active ? active.getAttribute("data-locale") : "uk";
    root.querySelectorAll("[data-locale-field]").forEach(function (el) {
      var loc = el.getAttribute("data-locale-field");
      el.hidden = loc !== locale && loc !== "all";
    });
  }

  function initCollection(root) {
    if (!root || root.dataset.collectionReady === "1") return;
    root.dataset.collectionReady = "1";

    var list = root.querySelector("[data-collection-list]");
    var tmpl = root.querySelector("[data-collection-empty]");
    var btn = root.querySelector("[data-collection-add]");
    var total = root.querySelector('input[name$="-TOTAL_FORMS"]');
    if (!list || !tmpl || !btn || !total) return;

    btn.addEventListener("click", function (e) {
      e.preventDefault();
      var idx = nextIndex(total);
      var html = tmpl.innerHTML.replace(/__prefix__/g, String(idx));
      var wrap = document.createElement("div");
      wrap.innerHTML = html.trim();
      var card = wrap.firstElementChild;
      if (!card) return;
      list.appendChild(card);
      total.value = String(idx + 1);

      var active = card.querySelector('input[name$="-is_active"]');
      if (active && active.type === "checkbox") active.checked = true;

      refreshLocale(root.closest("[data-locale-root]") || document);
      card.scrollIntoView({ behavior: "smooth", block: "nearest" });
      var first = card.querySelector("input[type='text'], textarea");
      if (first) first.focus();
    });
  }

  function boot() {
    document.querySelectorAll("[data-collection-root]").forEach(initCollection);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
