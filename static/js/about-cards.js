/* About cards: smooth cycle + phone-ring on scroll, swipe and tap. */
(function () {
  "use strict";

  var track = document.querySelector(".qm-about-track");
  if (!track) return;

  var cards = track.querySelectorAll(".qm-about-card");
  if (!cards.length) return;

  var index = 0;
  var locked = false;
  var scrolling = false;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var pointer = { x: 0, y: 0, moved: false };
  var scrollMs = 1600;
  var stepMs = reduced ? 80 : 2400;

  function isCompact() {
    return window.matchMedia("(max-width: 767px)").matches;
  }

  function easeInOut(t) {
    return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  }

  function scrollToCard(card) {
    if (!card) return;
    if (reduced) {
      card.scrollIntoView({ inline: "center", block: "nearest", behavior: "auto" });
      return;
    }
    var start = track.scrollLeft;
    var box = card.getBoundingClientRect();
    var trackBox = track.getBoundingClientRect();
    var target = start + (box.left + box.width / 2) - (trackBox.left + trackBox.width / 2);
    var max = track.scrollWidth - track.clientWidth;
    if (target < 0) target = 0;
    if (target > max) target = max;
    var delta = target - start;
    if (Math.abs(delta) < 1) return;
    scrolling = true;
    var t0 = window.performance.now();
    function frame(now) {
      var p = Math.min(1, (now - t0) / scrollMs);
      track.scrollLeft = start + delta * easeInOut(p);
      if (p < 1) {
        window.requestAnimationFrame(frame);
        return;
      }
      scrolling = false;
    }
    window.requestAnimationFrame(frame);
  }

  function ring(card) {
    if (reduced || !card) return;
    card.classList.remove("is-ringing");
    void card.offsetWidth;
    card.classList.add("is-ringing");
  }

  function setActive(next, shouldScroll, forceRing) {
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
    if (shouldScroll && isCompact()) {
      scrollToCard(cards[index]);
    }
  }

  function step(dir) {
    if (locked) return;
    locked = true;
    setActive(index + dir, true, false);
    window.setTimeout(function () {
      locked = false;
    }, stepMs);
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
      if (!isCompact() || scrolling || locked) return;
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
