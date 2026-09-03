(function () {
  var supported = ["de", "en"];

  function fromUrl() {
    var m = /[?&]lang=(de|en)\b/.exec(window.location.search);
    return m ? m[1] : null;
  }

  function fromBrowser() {
    var nav = (navigator.language || "de").slice(0, 2).toLowerCase();
    return supported.indexOf(nav) !== -1 ? nav : "de";
  }

  function isInternal(href) {
    return href && !/^(https?:|mailto:|tel:|#)/.test(href);
  }

  function withLang(href, lang) {
    var parts = href.split("#");
    var base = parts[0].replace(/([?&])lang=(de|en)(&|$)/, function (m, p1, p2, p3) {
      return p3 ? p1 : "";
    });
    base = base.replace(/[?&]$/, "");
    base += (base.indexOf("?") !== -1 ? "&" : "?") + "lang=" + lang;
    return parts.length > 1 ? base + "#" + parts[1] : base;
  }

  function apply(lang) {
    document.documentElement.setAttribute("lang", lang);
    var buttons = document.querySelectorAll("[data-setlang]");
    for (var i = 0; i < buttons.length; i++) {
      var b = buttons[i];
      var active = b.getAttribute("data-setlang") === lang;
      b.classList.toggle("active", active);
      b.setAttribute("aria-pressed", active ? "true" : "false");
    }
    var links = document.querySelectorAll("a[href]");
    for (var j = 0; j < links.length; j++) {
      var a = links[j];
      var href = a.getAttribute("href");
      if (isInternal(href)) a.setAttribute("href", withLang(href, lang));
    }
    if (window.history && window.history.replaceState) {
      var url = withLang(window.location.pathname + window.location.search, lang) + window.location.hash;
      window.history.replaceState(null, "", url);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    apply(fromUrl() || fromBrowser());
    var buttons = document.querySelectorAll("[data-setlang]");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener("click", function (e) {
        apply(e.currentTarget.getAttribute("data-setlang"));
      });
    }
  });
})();
