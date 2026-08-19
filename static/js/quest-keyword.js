/* Native required balloon follows OS language; use UI locale instead. */
(function () {
  "use strict";

  var input = document.getElementById("id_keyword");
  if (!input) return;

  var requiredMsg = input.getAttribute("data-required-msg") || "";

  function syncValidity() {
    if (input.validity.valueMissing) {
      input.setCustomValidity(requiredMsg);
      return;
    }
    input.setCustomValidity("");
  }

  input.addEventListener("invalid", syncValidity);
  input.addEventListener("input", function () {
    input.setCustomValidity("");
  });
})();
