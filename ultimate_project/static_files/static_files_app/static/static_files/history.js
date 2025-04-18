window.addEventListener("beforeunload", () => {
    // console.log("URL sauvegardée avec history.state et sessionStorage");
	stopMatch();
    let currentURL = window.location.href;
    history.replaceState({ lastVisitedPage: currentURL }, "");
    sessionStorage.setItem("lastVisitedPage", currentURL);
  });
