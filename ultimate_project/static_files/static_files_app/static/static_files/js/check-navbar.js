document.body.addEventListener("htmx:afterSettle", () => {
    const navbarAbsent = !document.getElementById("navbar");
    const isHomeUrl = window.location.pathname === "/home/";

    if (navbarAbsent && isHomeUrl) {
        // console.log ("%c************ there is no navbar!", "color: red");
        htmx.ajax('GET', '/home/', {
        target: 'body',
        pushURL: '/home/',
        headers: {
            'HX-Login-Success': 'true'
          }
        });
    }
});

window.addEventListener('popstate', function (event) {
    // console.log("%c************* reload HTMX", 'color: red');
    htmx.ajax('GET', window.location.pathname, {
      target: 'body',
      swap: 'innerHTML',
      headers: {
        'HX-Login-Success': 'true'
      }
    });
  });