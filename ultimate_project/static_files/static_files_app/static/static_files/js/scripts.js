
  window.addEventListener("beforeunload", () => {
    let currentURL = window.location.href;
    history.replaceState({ lastVisitedPage: currentURL }, "");
    sessionStorage.setItem("lastVisitedPage", currentURL);
  });

  function stopMatchHtmx() {
    fetch(`/match/stop-match/${window.selfId}/${window.selfMatchId}/`)
      .then(response => {
        if (!response.ok)
          throw new Error(`Error HTTP! Status: ${response.status}`);
        return response.text();
      })
      .catch(error => console.log(error))
  }

  function interceptUrlChanges() {
    const originalReplaceState = history.replaceState;

    history.replaceState = function (state, title, url) {
      originalReplaceState.apply(history, arguments);
    };
  }
  let recentlyNavigated = false;
  interceptUrlChanges();

  function handleNavigation() {
    if (recentlyNavigated) return;

    recentlyNavigated = true;
    setTimeout(() => recentlyNavigated = false, 100);     

    window.quitMatch?.(window.selfMatchId);
    window.quitMatch3D?.(window.selfMatchId);
    window.closeWsTournament?.();
    window.closeWsSimpleMatch?.();
  }
  
  window.addEventListener('popstate', handleNavigation);
  window.addEventListener('htmx:afterSwap', handleNavigation);
