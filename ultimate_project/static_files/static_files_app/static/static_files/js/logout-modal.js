function logoutUser() {
    fetch("/auth/logout/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "same-origin",
    }).then((response) => {
      htmx
        .ajax("GET", "/login/", {
          target: "body",
          swap: "outerHTML",
          headers: { "HX-Login-Success": "true" },
        })
        .then(function () {
          history.pushState(null, "", "/login/");
        });
    });
  }