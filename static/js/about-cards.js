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
    window.clearTimeout(activateTimer);
    activateTimer = window.setTimeout(function () {
      turn(cards[index]);
    }, isCompact() ? 220 : 140);
  }

  var frame = document.querySelector(".qm-frame.qm-about");

  function scrollHost() {
    return isCompact() && frame ? frame : track;
  }

  function lastCardInView(root) {
    var lastIndex = cards.length - 1;
    var rect = cards[lastIndex].getBoundingClientRect();
    var seen = Math.min(rect.bottom, root.bottom) - Math.max(rect.top, root.top);
    if (seen < 40) return false;
    return (
      rect.top < root.top + root.height * 0.64 ||
      seen >= rect.height * 0.42
    );
  }

  function focusCard() {
    var host = scrollHost();
    var lastIndex = cards.length - 1;
    var max = host.scrollHeight - host.clientHeight;
    var root = host.getBoundingClientRect();
    if (host.scrollTop <= 16) return 0;
    if (max > 0 && host.scrollTop >= max - 72) return lastIndex;
    if (index >= lastIndex - 1 && lastCardInView(root)) return lastIndex;

    var bandTop = root.top + Math.min(56, root.height * 0.1);
    var bandBottom = root.top + root.height * 0.48;
    var best = 0;
    var bestScore = -1;
    cards.forEach(function (card, n) {
      var rect = card.getBoundingClientRect();
      var overlap = Math.min(rect.bottom, bandBottom) - Math.max(rect.top, bandTop);
      if (overlap > bestScore) {
        bestScore = overlap;
        best = n;
      }
    });
    return best;
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
  var userScrolling = false;
  var settleTimer;
  var activateTimer;
  var stepTimer;
  var lastTop = 0;
  var lockMs = reduced ? 80 : 1100;

  function markScrolling() {
    var top = scrollHost().scrollTop;
    if (Math.abs(top - lastTop) > 2) userScrolling = true;
    lastTop = top;
    window.clearTimeout(settleTimer);
    settleTimer = window.setTimeout(function () {
      userScrolling = false;
    }, 160);
  }

  function stepMobileToward(target) {
    if (target === index) return;
    var next = target > index ? index + 1 : index - 1;
    switchLock = true;
    setActive(next, true);
    window.clearTimeout(stepTimer);
    stepTimer = window.setTimeout(function () {
      switchLock = false;
      var again = focusCard();
      if (again === index) return;
      var lastIndex = cards.length - 1;
      var edgeSnap =
        (again === lastIndex && index === lastIndex - 1) ||
        (again === 0 && index === 1);
      if (!userScrolling && !edgeSnap) return;
      stepMobileToward(again);
    }, lockMs);
  }

  function onScroll() {
    if (!isCompact()) return;
    markScrolling();
    if (ticking || switchLock) return;
    ticking = true;
    window.requestAnimationFrame(function () {
      ticking = false;
      if (switchLock || !userScrolling) return;
      var target = focusCard();
      if (target === index) return;
      stepMobileToward(target);
    });
  }

  function onScrollEnd() {
    if (!isCompact() || switchLock) return;
    var target = focusCard();
    var lastIndex = cards.length - 1;
    if (target !== lastIndex && target !== 0) return;
    if (target === index) return;
    stepMobileToward(target);
  }

  function bindScroll(el) {
    if (!el) return;
    el.addEventListener("scroll", onScroll, { passive: true });
    el.addEventListener("scrollend", onScrollEnd, { passive: true });
  }

  bindScroll(frame);
  bindScroll(track);

  var compactMq = window.matchMedia("(max-width: 767px)");
  function onCompactChange() {
    setActive(index, false);
  }
  if (compactMq.addEventListener) {
    compactMq.addEventListener("change", onCompactChange);
  } else if (compactMq.addListener) {
    compactMq.addListener(onCompactChange);
  }

  function clearTimers() {
    window.clearTimeout(settleTimer);
    window.clearTimeout(activateTimer);
    window.clearTimeout(stepTimer);
    cards.forEach(function (card) {
      window.clearTimeout(card._turnTimer);
      window.clearTimeout(card._hoverTimer);
    });
  }

  window.addEventListener("pagehide", clearTimers);

  setActive(0, false);
})();
