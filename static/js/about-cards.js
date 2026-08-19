/* About cards: smooth cycle + phone-ring on scroll, swipe and tap. */
(function () {
  "use strict";

  var track = document.querySelector(".qm-about-track");
  if (!track) return;

  var cards = track.querySelectorAll(".qm-about-card");
  if (!cards.length) return;

  var index = 0;
  var locked = false;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var pointer = { x: 0, y: 0, moved: false };

  function isCompact() {
    return window.matchMedia("(max-width: 767px)").matches;
  }

  function ring(card) {
    if (reduced || !card) return;
    card.classList.remove("is-ringing");
    void card.offsetWidth;
    card.classList.add("is-ringing");
  }

  function setActive(next, scrollIntoView, forceRing) {
    var wrapped = (next + cards.length) % cards.length;
    var changed = wrapped !== index;
    index = wrapped;
    cards.forEach(function (card, n) {
      card.classList.toggle("is-active", n === index);
      if (n !== index) card.classList.remove("is-ringing");
    });
    if (changed || forceRing) {
      ring(cards[index]);
    }
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
    setActive(index + dir, true, false);
    window.setTimeout(function () {
      locked = false;
    }, reduced ? 80 : 720);
  }

  cards.forEach(function (card, n) {
    card.addEventListener("animationend", function (event) {
      if (event.animationName !== "qm-about-ring") return;
      card.classList.remove("is-ringing");
    });
    card.addEventListener("webkitAnimationEnd", function () {
      card.classList.remove("is-ringing");
    });

    card.addEventListener("pointerdown", function (event) {
      pointer.x = event.clientX;
      pointer.y = event.clientY;
      pointer.moved = false;
    });

    card.addEventListener("pointermove", function (event) {
      if (Math.abs(event.clientX - pointer.x) > 12 || Math.abs(event.clientY - pointer.y) > 12) {
        pointer.moved = true;
      }
    });

    card.addEventListener("pointerup", function () {
      if (pointer.moved) return;
      setActive(n, true, true);
    });

    card.addEventListener("keydown", function (event) {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      setActive(n, true, true);
    });

    if (!card.hasAttribute("tabindex")) {
      card.setAttribute("tabindex", "0");
    }
  });

  track.addEventListener(
    "wheel",
    function (event) {
      var dy = event.deltaY;
      var dx = event.deltaX;
      if (Math.abs(dy) < 8 && Math.abs(dx) < 8) return;
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
        setActive(best, false, false);
      }, 90);
    },
    { passive: true }
  );
})();
