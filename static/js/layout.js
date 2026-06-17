/* Salezy layout engine: customizer, sidebar, dark-mode, preloader, nav accordion.
   Layout choices persist in localStorage and are re-applied on every page load. */
(function () {
  "use strict";

  var STORE = "salezy-layout";
  var DEFAULTS = {
    sidebar: "vertical", bsTheme: "light", layoutWidth: "fluid", layoutPosition: "fixed",
    topbar: "light", sidebarSize: "default", sidebarColor: "light", dir: "ltr", preloader: "enable"
  };
  // settings key -> the <html> attribute it drives
  var ATTR = {
    sidebar: "data-sidebar", bsTheme: "data-bs-theme", layoutWidth: "data-layout-width",
    layoutPosition: "data-layout-position", topbar: "data-topbar", sidebarSize: "data-sidebar-size",
    sidebarColor: "data-sidebar-color", dir: "dir", preloader: "data-preloader"
  };

  function load() {
    try { return Object.assign({}, DEFAULTS, JSON.parse(localStorage.getItem(STORE) || "{}")); }
    catch (e) { return Object.assign({}, DEFAULTS); }
  }
  function save(s) { try { localStorage.setItem(STORE, JSON.stringify(s)); } catch (e) {} }

  function apply(s) {
    var html = document.documentElement;
    Object.keys(ATTR).forEach(function (k) { html.setAttribute(ATTR[k], s[k]); });
    html.classList.toggle("dark", s.bsTheme === "dark");
    syncCustomizer(s);
    syncThemeToggle(s);
  }

  function syncCustomizer(s) {
    document.querySelectorAll(".opt[data-key]").forEach(function (btn) {
      btn.classList.toggle("active", s[btn.getAttribute("data-key")] === btn.getAttribute("data-value"));
    });
  }
  function syncThemeToggle(s) {
    document.querySelectorAll("[data-theme-toggle] .lucide, [data-theme-toggle] i").forEach(function () {});
  }

  // expose for inline onclicks / other scripts
  var state = load();
  window.Layout = {
    set: function (key, value) { state[key] = value; save(state); apply(state); refreshIcons(); },
    get: function () { return state; },
    reset: function () { state = Object.assign({}, DEFAULTS); save(state); apply(state); refreshIcons(); },
    toggleTheme: function () { this.set("bsTheme", state.bsTheme === "dark" ? "light" : "dark"); }
  };

  function refreshIcons() { if (window.lucide && window.lucide.createIcons) window.lucide.createIcons(); }

  // apply ASAP (before DOMContentLoaded for the attrs already in <html>)
  apply(state);

  document.addEventListener("DOMContentLoaded", function () {
    apply(state);
    refreshIcons();

    // ---- preloader ----
    var pre = document.getElementById("preloader");
    if (pre) { window.addEventListener("load", function () { setTimeout(function () { pre.classList.add("hidden"); }, 250); }); }

    // ---- sidebar collapse (desktop) / drawer (mobile) ----
    var sidebarToggle = document.querySelector("[data-sidebar-toggle]");
    if (sidebarToggle) {
      sidebarToggle.addEventListener("click", function () {
        if (window.innerWidth <= 1024) { document.body.classList.toggle("sidebar-open"); }
        else { document.body.classList.toggle("sidebar-toggle-collapsed"); }
      });
    }
    var backdrop = document.querySelector(".sidebar-backdrop");
    if (backdrop) backdrop.addEventListener("click", function () { document.body.classList.remove("sidebar-open"); });

    // ---- nav accordion ----
    document.querySelectorAll(".nav-group > .nav-link[data-accordion]").forEach(function (link) {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        var grp = link.closest(".nav-group");
        var wasOpen = grp.classList.contains("open");
        // single-open accordion
        document.querySelectorAll(".nav-group.open").forEach(function (g) { if (g !== grp) g.classList.remove("open"); });
        grp.classList.toggle("open", !wasOpen);
      });
    });
    // auto-open the group holding the active link
    var active = document.querySelector(".nav-sub a.active");
    if (active) { var g = active.closest(".nav-group"); if (g) g.classList.add("open"); }

    // ---- theme quick toggle ----
    document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
      b.addEventListener("click", function () { window.Layout.toggleTheme(); });
    });

    // ---- customizer open/close ----
    var cz = document.getElementById("customizer");
    var ov = document.getElementById("customizer-overlay");
    function openCz() { if (cz) cz.classList.add("open"); if (ov) ov.classList.add("show"); }
    function closeCz() { if (cz) cz.classList.remove("open"); if (ov) ov.classList.remove("show"); }
    document.querySelectorAll("[data-customizer-open]").forEach(function (b) { b.addEventListener("click", openCz); });
    document.querySelectorAll("[data-customizer-close]").forEach(function (b) { b.addEventListener("click", closeCz); });
    if (ov) ov.addEventListener("click", closeCz);

    // ---- customizer options ----
    document.querySelectorAll(".opt[data-key]").forEach(function (btn) {
      btn.addEventListener("click", function () { window.Layout.set(btn.getAttribute("data-key"), btn.getAttribute("data-value")); });
    });
    var resetBtn = document.querySelector("[data-customizer-reset]");
    if (resetBtn) resetBtn.addEventListener("click", function () { window.Layout.reset(); });

    // ---- auto-dismiss flash messages ----
    document.querySelectorAll(".messages .alert").forEach(function (a) {
      setTimeout(function () { a.style.transition = "opacity .4s"; a.style.opacity = "0"; setTimeout(function () { a.remove(); }, 400); }, 6000);
    });
  });
})();
