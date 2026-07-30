(function () {
  var prefix = "A21-REFRESH-1|";
  var compiler = "/compiler/";
  var windowMs = 15 * 60 * 1000;
  var locationObject = window.location || document.location;
  var path = locationObject && locationObject.pathname ? locationObject.pathname : "/";
  var now = new Date().getTime();
  var state = typeof window.name === "string" ? window.name : "";
  var count = 0;
  var first = 0;
  var pending = false;
  var parts;

  function write(nextCount, nextFirst, nextPending) {
    window.name = prefix + path + "|" + nextCount + "|" + nextFirst + "|" +
      (nextPending ? "1" : "0");
  }

  function read() {
    if (!state || state.indexOf(prefix) !== 0) {
      return false;
    }
    parts = state.substring(prefix.length).split("|");
    if (parts.length !== 4 || parts[0] !== path) {
      return false;
    }
    count = parseInt(parts[1], 10);
    first = parseInt(parts[2], 10);
    pending = parts[3] === "1";
    if (isNaN(count) || isNaN(first) || !pending) {
      return false;
    }
    if (first && (now < first || now - first > windowMs)) {
      return false;
    }
    return true;
  }

  try {
    // Do not overwrite a window name belonging to another application.
    if (state && state.indexOf(prefix) !== 0) {
      return;
    }

    if (!read()) {
      count = 0;
      first = 0;
    } else {
      count += 1;
    }

    if (count > 0 && !first) {
      first = now;
    }

    if (count >= 5) {
      // Prevent an immediate retrigger when the visitor returns from the
      // Compiler. The name was empty before this enhancement took control.
      window.name = "";
      if (window.location && window.location.replace) {
        window.location.replace(compiler);
      } else {
        window.location = compiler;
      }
      return;
    }

    write(count, first, false);

    function markUnload() {
      if (typeof window.name === "string" && window.name.indexOf(prefix) === 0) {
        write(count, first, true);
      }
    }

    if (window.addEventListener) {
      window.addEventListener("unload", markUnload, false);
    } else if (window.attachEvent) {
      window.attachEvent("onunload", markUnload);
    } else {
      window.onunload = markUnload;
    }
  } catch (ignore) {
    // Reading remains fail-open if a browser blocks window.name access.
  }
}());