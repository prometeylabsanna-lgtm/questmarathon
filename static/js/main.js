/* Квест-марафон — минимальный JS: hamburger menu toggle. No dependencies. */
(function () {
  "use strict";

  var burger = document.getElementById("qm-burger");
  var overlay = document.getElementById("qm-menu-overlay");

  if (!burger || !overlay) return;

  var labelOpen = burger.getAttribute("aria-label") || "Меню";
  var labelClose = burger.getAttribute("data-label-close") || "Закрити меню";

  function openMenu() {
    overlay.hidden = false;
    burger.setAttribute("aria-expanded", "true");
    burger.setAttribute("aria-label", labelClose);
    document.body.classList.add("qm-menu-open");
  }

  function closeMenu() {
    overlay.hidden = true;
    burger.setAttribute("aria-expanded", "false");
    burger.setAttribute("aria-label", labelOpen);
    document.body.classList.remove("qm-menu-open");
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

(function () {
  "use strict";

  var items = document.querySelectorAll(".qm-faq__item");
  if (!items.length) return;

  items.forEach(function (item) {
    item.addEventListener("toggle", function () {
      if (!item.open) return;
      items.forEach(function (other) {
        if (other !== item) other.open = false;
      });
    });
  });
})();
