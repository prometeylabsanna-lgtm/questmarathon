/* About cards: 3D turn on tap/click only. Mobile = vertical snap. */
(function () {
  "use strict";

  var track = document.querySelector(".qm-about-track");
  if (!track) return;

  var cards = track.querySelectorAll(".qm-about-card");
  if (!cards.length) return;

  var index = 0;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var pointer = { x: 0, y: 0, moved: false };

  function canHover() {
    return window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  }

  function isCompact() {
    return window.matchMedia("(max-width: 767px)").matches;
  }

  function turn(card) {
    if (reduced || !card) return;
    if (card.classList.contains("is-turning")) return;
    card.classList.add("is-turning");
    window.clearTimeout(card._turnTimer);
    card._turnTimer = window.setTimeout(function () {
      card.classList.remove("is-turning");
    }, isCompact() ? 1800 : 1100);
  }

  function setActive(next, withTurn) {
    var last = cards.length - 1;
    var wrapped = Math.max(0, Math.min(last, next));
    if (wrapped === index) {
      if (withTurn) turn(cards[index]);
      return;
    }
    index = wrapped;
    cards.forEach(function (card, n) {
      card.classList.toggle("is-active", n === index);
      card.classList.toggle("is-left", !isCompact() && n < index);
      card.classList.toggle("is-right", !isCompact() && n > index);
      if (n !== index) {
        window.clearTimeout(card._turnTimer);
        card.classList.remove("is-turning");
      }
    });
    if (!withTurn) return;
    window.setTimeout(function () {
      turn(cards[index]);
    }, isCompact() ? 220 : 140);
  }

  function mostVisibleCard() {
    var lastIndex = cards.length - 1;
    var max = track.scrollHeight - track.clientHeight;
    if (track.scrollTop <= 12) return 0;
    if (max > 0 && track.scrollTop >= max - 28) return lastIndex;

    var root = track.getBoundingClientRect();
    var lastRect = cards[lastIndex].getBoundingClientRect();
    var lastSeen = Math.min(lastRect.bottom, root.bottom) - Math.max(lastRect.top, root.top);
    if (lastSeen > lastRect.height * 0.5) return lastIndex;

    var best = 0;
    var bestDist = Infinity;
    cards.forEach(function (card, n) {
      var dist = Math.abs(card.getBoundingClientRect().top - (root.top + 10));
      if (dist < bestDist) {
        bestDist = dist;
        best = n;
      }
    });
    return best;
  }

  function pickMobileCard() {
    var lastIndex = cards.length - 1;
    var raw = mostVisibleCard();
    if (raw > index + 1) return index + 1;
    if (raw < index - 1) return index - 1;
    if (raw === lastIndex) return raw;
    if (raw > index) {
      var root = track.getBoundingClientRect();
      var chosen = cards[raw].getBoundingClientRect();
      if (chosen.top > root.top + root.height * 0.3) return index;
    }
    return raw;
  }

  cards.forEach(function (card, n) {
    card.addEventListener("mouseenter", function () {
      if (!canHover()) return;
      window.clearTimeout(card._hoverTimer);
      card._hoverTimer = window.setTimeout(function () {
        setActive(n, true);
      }, 90);
    });

    card.addEventListener("mouseleave", function () {
      window.clearTimeout(card._hoverTimer);
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
      setActive(n, true);
    });

    card.addEventListener("keydown", function (event) {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      setActive(n, true);
    });

    if (!card.hasAttribute("tabindex")) {
      card.setAttribute("tabindex", "0");
    }
  });

  var ticking = false;
  var switchLock = false;
  var settleTimer;
  track.addEventListener(
    "scroll",
    function () {
      if (!isCompact()) return;
      window.clearTimeout(settleTimer);
      settleTimer = window.setTimeout(function () {
        switchLock = false;
        var settled = mostVisibleCard();
        if (settled === index) return;
        setActive(settled, settled > index);
      }, 280);

      if (ticking || switchLock) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        ticking = false;
        if (switchLock) return;
        var next = pickMobileCard();
        if (next === index) return;
        switchLock = true;
        setActive(next, next > index);
        window.setTimeout(function () {
          switchLock = false;
        }, reduced ? 80 : 680);
      });
    },
    { passive: true }
  );

  setActive(0, false);
})();
