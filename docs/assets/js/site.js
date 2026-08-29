(function () {
  "use strict";

  function normalizedPath(path) {
    return path.replace(/\/index\.html$/, "/").replace(/\.html$/, "/");
  }

  function closeNavigation(button, sidebar) {
    sidebar.classList.remove("open");
    button.setAttribute("aria-expanded", "false");
  }

  document.addEventListener("DOMContentLoaded", function () {
    var button = document.querySelector(".nav-toggle-btn");
    var sidebar = document.querySelector(".sidebar");

    if (button && sidebar) {
      button.addEventListener("click", function () {
        var isOpen = sidebar.classList.toggle("open");
        button.setAttribute("aria-expanded", String(isOpen));
      });

      sidebar.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
          closeNavigation(button, sidebar);
        });
      });

      document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
          closeNavigation(button, sidebar);
        }
      });
    }

    var currentPath = normalizedPath(window.location.pathname);
    document.querySelectorAll(".nav-link").forEach(function (link) {
      var linkPath = normalizedPath(new URL(link.href, window.location.origin).pathname);
      if (linkPath === currentPath) {
        link.classList.add("active");
        link.setAttribute("aria-current", "page");
      }
    });
  });
}());
