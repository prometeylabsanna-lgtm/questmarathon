/* About cards: scroll cycles which card is slightly larger. */
(function () {
  "use strict";

  var track = document.querySelector(".qm-about-track");
  if (!track) return;

  var cards = track.querySelectorAll(".qm-about-card");
  if (!cards.length) return;

  var index = 0;
  var locked = false;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function isCompact() {
    return window.matchMedia("(max-width: 767px)").matches;
  }

  function setActive(next, scrollIntoView) {
    index = (next + cards.length) % cards.length;
    cards.forEach(function (card, n) {
      card.classList.toggle("is-active", n === index);
    });
    if (scrollIntoView && isCompact()) {
      cards[index].scrollIntoView({
        inline: "center",
        block: "nearest",
        behavior: reduced ? "auto" : "smooth",
      });
    }
  }

  function step(dir) {
    if (locked) return;
    locked = true;
    setActive(index + dir, true);
    window.setTimeout(function () {
      locked = false;
    }, reduced ? 80 : 380);
  }

  track.addEventListener(
    "wheel",
    function (event) {
      var dy = event.deltaY;
      var dx = event.deltaX;
      if (Math.abs(dy) < 6 && Math.abs(dx) < 6) return;
      event.preventDefault();
      step(dy + dx > 0 ? 1 : -1);
    },
    { passive: false }
  );

  track.addEventListener("keydown", function (event) {
    if (event.key === "ArrowRight" || event.key === "ArrowDown") {
      event.preventDefault();
      step(1);
    }
    if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
      event.preventDefault();
      step(-1);
    }
  });

  var scrollTimer;
  track.addEventListener(
    "scroll",
    function () {
      if (!isCompact()) return;
      window.clearTimeout(scrollTimer);
      scrollTimer = window.setTimeout(function () {
        var mid = track.getBoundingClientRect().left + track.clientWidth / 2;
        var best = index;
        var bestDist = Infinity;
        cards.forEach(function (card, n) {
          var box = card.getBoundingClientRect();
          var dist = Math.abs(box.left + box.width / 2 - mid);
          if (dist < bestDist) {
            bestDist = dist;
            best = n;
          }
        });
        setActive(best, false);
      }, 70);
    },
    { passive: true }
  );
})();
