(function () {
  var STORAGE_KEY = "sfr-lang";
  var supported = ["de", "en"];

  function detect() {
    var stored = null;
    try { stored = localStorage.getItem(STORAGE_KEY); } catch (e) {}
    if (stored && supported.indexOf(stored) !== -1) return stored;
    var nav = (navigator.language || "de").slice(0, 2).toLowerCase();
    return supported.indexOf(nav) !== -1 ? nav : "de";
  }

  function apply(lang) {
    document.documentElement.setAttribute("lang", lang);
    document.querySelectorAll("[data-setlang]").forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-setlang") === lang);
    });
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
  }

  document.addEventListener("DOMContentLoaded", function () {
    apply(detect());
    document.querySelectorAll("[data-setlang]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        apply(btn.getAttribute("data-setlang"));
      });
    });
  });
})();
