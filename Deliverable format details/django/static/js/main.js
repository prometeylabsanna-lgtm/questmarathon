/* Квест-марафон — минимальный JS: hamburger menu toggle. No dependencies. */
(function () {
  "use strict";

  var burger = document.getElementById("qm-burger");
  var overlay = document.getElementById("qm-menu-overlay");

  if (!burger || !overlay) return;

  function openMenu() {
    overlay.hidden = false;
    burger.setAttribute("aria-expanded", "true");
  }

  function closeMenu() {
    overlay.hidden = true;
    burger.setAttribute("aria-expanded", "false");
  }

  burger.addEventListener("click", function () {
    if (overlay.hidden) {
      openMenu();
    } else {
      closeMenu();
    }
  });

  overlay.addEventListener("click", function (event) {
    if (event.target === overlay) closeMenu();
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !overlay.hidden) closeMenu();
  });
})();
