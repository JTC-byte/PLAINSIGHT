// The first-load guard. A classic script, so it runs even when the page's module
// graph does not arrive: one dropped static file leaves a module page blank, and
// this script is the only code that still runs then. app.js says it started by
// dispatching "plainsight:started". If it has not, on the module's error event
// or after 15 seconds, the guard reloads the page once; when this load is
// already that reload, it shows a calm panel with a reload button instead, so
// it can never loop. It stores nothing: whether this load is a reload is read
// from the browser's own navigation entry (doctrine/EGRESS.md EG-3).
(function () {
  var started = false;
  var handled = false;
  window.addEventListener("plainsight:started", function () { started = true; });

  function navigationType() {
    try {
      var entry = performance.getEntriesByType("navigation")[0];
      return entry ? entry.type : "";
    } catch (e) {
      return "";
    }
  }

  function panel() {
    var pane = document.getElementById("tab");
    if (!pane) return;
    pane.textContent = "";
    var card = document.createElement("div");
    card.className = "boot-card";
    var text = document.createElement("p");
    text.textContent = "The page did not finish loading: one of its files did not arrive. The case is unaffected. Reload to try again.";
    var button = document.createElement("button");
    button.className = "btn primary";
    button.type = "button";
    button.textContent = "Reload the page";
    button.addEventListener("click", function () { location.reload(); });
    card.appendChild(text);
    card.appendChild(button);
    pane.appendChild(card);
    var page = document.getElementById("page");
    if (page) page.setAttribute("aria-busy", "false");
  }

  function recover() {
    if (started || handled) return;
    handled = true;
    if (navigationType() !== "reload") {
      location.reload();
      return;
    }
    panel();
  }

  var module = document.getElementById("app-module");
  if (module) module.addEventListener("error", recover);
  setTimeout(recover, 15000);
})();
