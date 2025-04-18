function stopMatch()
{
	fetch(`/match/stop-match/${window.selfId}/${window.selfMatchId}/`)
	.then(response => {
		if (!response.ok) 
			throw new Error(`Error HTTP! Status: ${response.status}`);		  
		return response.text();
	})
	// .then(data => console.log(data))
	.catch(error => console.log(error))
}

  function closeWebsockets() {

    // console.log("########### closing websockets #######");
    if (typeof closeSimpleMatchSocket === "function") closeSimpleMatchSocket();
    if (typeof closeTournamentSocket === "function") closeTournamentSocket();
  }

  closeWebsockets();
  function interceptUrlChanges() {
    const originalReplaceState = history.replaceState;

    history.replaceState = function (state, title, url) {
      originalReplaceState.apply(history, arguments);
      closeWebsockets();
    };
  }
  
  interceptUrlChanges();