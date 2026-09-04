/* FED-LINk — documentation site behaviour (public/js/script.js).
   Progressive enhancement only: the docs render fine without JS. */

(function () {
  "use strict";

  // Highlight the current page in the nav, if ids are present.
  var here = window.location.pathname.split("/").pop() || "index.md";
  document.querySelectorAll(".site-nav a").forEach(function (link) {
    var target = link.getAttribute("href").split("/").pop();
    if (target === here) link.classList.add("active");
  });

  // Open external links in a new tab so the docs stay open.
  document.querySelectorAll("main a[href^='http']").forEach(function (link) {
    if (link.host !== window.location.host) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    }
  });

  // Copy-to-clipboard buttons for CLI snippets: <pre data-copyable>.
  document.querySelectorAll("pre[data-copyable]").forEach(function (pre) {
    var button = document.createElement("button");
    button.type = "button";
    button.textContent = "Copy";
    button.className = "copy-button";
    button.addEventListener("click", function () {
      navigator.clipboard.writeText(pre.innerText).then(function () {
        button.textContent = "Copied!";
        setTimeout(function () { button.textContent = "Copy"; }, 1500);
      });
    });
    pre.appendChild(button);
  });
})();
