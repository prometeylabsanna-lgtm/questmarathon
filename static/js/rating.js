/* Rating image lightbox — no dependencies. */
(function () {
  "use strict";

  var openBtn = document.querySelector("[data-rating-lightbox]");
  var dialog = document.getElementById("qm-rating-lightbox");
  if (!openBtn || !dialog) return;

  var img = dialog.querySelector(".qm-rating-lightbox__img");
  var closeBtn = dialog.querySelector("[data-rating-lightbox-close]");
  var lastFocus = null;

  function openLightbox() {
    var src = openBtn.getAttribute("data-src") || "";
    if (!src || !img) return;
    lastFocus = document.activeElement;
    img.src = src;
    img.alt = openBtn.querySelector("img")
      ? openBtn.querySelector("img").getAttribute("alt") || ""
      : "";
    dialog.hidden = false;
    document.body.classList.add("qm-lightbox-open");
    if (closeBtn) closeBtn.focus();
  }

  function closeLightbox() {
    dialog.hidden = true;
    if (img) {
      img.removeAttribute("src");
      img.alt = "";
    }
    document.body.classList.remove("qm-lightbox-open");
    if (lastFocus && typeof lastFocus.focus === "function") {
      lastFocus.focus();
    }
  }

  openBtn.addEventListener("click", openLightbox);

  if (closeBtn) {
    closeBtn.addEventListener("click", closeLightbox);
  }

  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) closeLightbox();
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !dialog.hidden) {
      event.preventDefault();
      closeLightbox();
    }
  });
})();
