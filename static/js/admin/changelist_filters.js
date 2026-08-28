/**
 * Top changelist filters: submit GET form when a select changes.
 */
(function () {
  function bindForm(form) {
    if (!form || form.dataset.bound === "1") return;
    form.dataset.bound = "1";

    form.addEventListener("change", function (e) {
      var t = e.target;
      if (!t || (t.tagName !== "SELECT" && t.type !== "select-one")) return;
      form.requestSubmit ? form.requestSubmit() : form.submit();
    });
  }

  function boot() {
    document.querySelectorAll("form.qm-admin-filters[data-auto-submit]").forEach(bindForm);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
