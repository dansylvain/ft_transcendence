window.simplePlayers = []

/**========================================================================
 * !                              CODE CHANGES
 *   these functions were added.
 *   the function "receiveInvitation" was modified (see below)
 *========================================================================**/

var isPageVisible = isPageVisible || !document.hidden;
var pendingInvitations = pendingInvitations || [];

document.addEventListener('visibilitychange', () => {
    isPageVisible = !document.hidden;
    if (isPageVisible) {
        // Si la page devient active, on traite les notifications en attente
        handlePendingInvitations();
    }
});

async function invitationPopup(socket, applicantId, applicantName)
{
    const result = await Swal.fire({
        title: 'Oops!',
        text: ' You have an invitation!',
        imageUrl: 'https://github.com/dansylvain/pictures/blob/main/non-je-ne-contracte-pas.gif?raw=true',
        imageWidth: 300,
        imageHeight: 300,
        imageAlt: 'GIF fun',
        showCancelButton: true,
        confirmButtonText: 'Accept',
        cancelButtonText: 'Decline',
      });
    //   console.log("RESULT: ", result, result.isConfirmed)
    // const userConfirmed = confirm(`You have an invitation from ${applicantName}`);
    sendConfirmation(socket, applicantId, applicantName, result.isConfirmed);
}

function handlePendingInvitations() {
    // Traite toutes les invitations en attente lorsque la page devient active
    pendingInvitations.forEach(invitation => {
        const { applicantId, applicantName, socket } = invitation;
        invitationPopup(socket, applicantId, applicantName);
    });

    // Vide la file d'attente une fois les invitations traitées
    pendingInvitations = [];
}

function showNotification(message, applicantId) {
    if (Notification.permission === "granted") {
        new Notification(message);
    } else if (Notification.permission !== "denied") {
        // Demande la permission si elle n'a pas encore été accordée ni refusée
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                new Notification(message);
            }
        });
    } else {
        // console.log("Notification permission not granted");
    }
}

function receiveInvitation(socket, applicantId, applicantName) {
    // console.log("I have had an invitation from: " + applicantName);
    
    if (isPageVisible) {
        // Si l'onglet est actif, demande la confirmation immédiatement
        invitationPopup(socket, applicantId, applicantName);
    } else {
        // Si l'onglet est en arrière-plan, stocke l'invitation en attente
        pendingInvitations.push({socket, applicantId, applicantName});
        // showNotification(`You have an invitation from ${applicantId}`, applicantId);
    }
}

// function receiveInvitation(socket, applicantId) {

// 	console.log("i have had and invitation from: " + applicantId)

// 	confirm(`you have an invitation from ${applicantId}`)
// 	? sendConfirmation(socket, applicantId, true)	
// 	: sendConfirmation(socket, applicantId, false);
// }

/**========================================================================
 *!                           END OF CHANGES
 *========================================================================**/

function loadSimpleMatchHtml(data, target) {

	const oldScripts = document.querySelectorAll("script.match-script");			
	oldScripts.forEach(oldScript => oldScript.remove());	
	const overlay = document.getElementById(target);
	overlay.innerHTML = data;
	const scripts = overlay.getElementsByTagName("script");
	
	for (const script of scripts) {
		
		const newScript = document.createElement("script");
		newScript.className = script.className;
		if (script.src) {	
			newScript.src = script.src + "?t=" + Date.now();
			newScript.async = true;  
			newScript.onload = script.onload;
		} else 			
		newScript.textContent = script.textContent;		
		document.body.appendChild(newScript); 
	}
}

function setSelfMatchId() {

	const matchsContainer = document.getElementById("matchs");
	const matchElements = [...matchsContainer.children];
	const dim = document.getElementById("dim");

    matchElements.forEach(match => {		
		if (match.id == window.selfMatchId)
			match.classList.add("self-match");					
        match.onclick = function() {
            // console.log("AVANT ", window.selfName, " ", )
			fetch(
				`/match/match${dim.value}d/` +
				`?matchId=${match.id}&playerId=${window.selfId}&playerName=${window.selfName}&player2Id=${-window.selfId}&player2Name=${window.player2Name}`)
			.then(response => {
				if (!response.ok) 
					throw new Error(`Error HTTP! Status: ${response.status}`);		  
				return response.text();
			})
			.then(data => loadSimpleMatchHtml(data, "overlay-match"))
			.catch(error => console.log(error))
		};					
	});
}
// matchWebsockets = []
// function newMatchPlayer(socket) {
  
// 	const playerName = document.getElementById("match-player-name").value;
// 	if (playerName.trim() === "")
// 	{
// 		alert("enter a name!");
// 		return;
// 	}
// 	if (socket.readyState === WebSocket.OPEN) 
// 		socket.send(JSON.stringify({
// 			type: "newPlayer",
// 			playerName: playerName			
// 		}));
// 	matchWebsockets.push({playerName: playerName});
// }

// function connectNewMatchPlayer(playerId, playerName) {

// 	console.log("CONNECT NEW PLAYER ", playerId, " ", playerName);
// 	const ws = websockets.find(ws => ws.playerName === playerName);	
// 	ws.playerId = playerId;
// 	console.log("ws id ", ws.playerName, ws.playerId);
// 	const socket = new WebSocket(
//         `wss://${window.pidom}/ws/tournament/simple-match/${window.selfId}/${window.selfName}/`
//     );
// 	ws.socket = socket;
// 	socket.onopen = () => {
// 		console.log(`Connexion Tournament ${playerName} établie 😊`);	
// 	}
// 	socket.onclose = () => {
// 		console.log(`Connexion Tournament ${playerName} disconnected 😈`);
// 	};	
// 	socket.onmessage = event =>
// 		{};// onTournamentMessage(event, window.tournamentSocket);	
// } 
// function movePlayerInMatch(socket, matchElement, match) {
	
// 	const playersContainer = document.getElementById("players");
// 	const playerElements = [...playersContainer.children];
// 	const matchPlayerElements = [...matchElement.children];

// 	if (match.players)
// 	{		
// 		// match.players.forEach(p => console.log("foriche ", p.playerId))
// 		playerElements.slice().reverse().forEach(player => {

// 			if (match.players.some(p => p.playerId == player.id) &&
// 				matchPlayerElements.every(p => p.id != player.id))
// 			{				
// 				// const clone = player.cloneNode(true)
// 				// clone.onclick = player.onclick;
// 				// matchElement.appendChild(clone);	
// 				matchElement.appendChild(player);	
// 			}		
// 		});
// 		matchPlayerElements.slice().reverse().forEach(player => {
// 			if (match.players.every(el => el.playerId != player.id))
// 			{
// 				playersContainer.appendChild(player);
// 				// addPlayerToContainer(socket, playersContainer, player.id);	
// 				// player.remove();			
// 			}			
// 		});
// 	}	
// }

function moveSimplePlayerInMatch(matchElement, match) {

	// console.log("MOVE SIMPLE PLAYER IN MATCH", match);

	if (!match.players)
		return;
	// console.log("MOVE SIMPLE PLAYER IN MATCH after return");
	match.players.forEach(ply => {
		const winPly = window.simplePlayers.find(el => el.id == ply.playerId);
		if (winPly)
			matchElement.appendChild(winPly);
	});	
}

function addToMatchs(socket, matchsContainer, match) {
  	
	const div = document.createElement("div");
	div.className = "match";
	div.textContent = `match: ${match.matchId}`;
	div.id = match.matchId;
    matchsContainer.appendChild(div);
	moveSimplePlayerInMatch(div, match);
}

function removeMatchs(socket, matchs, matchsContainer, matchElements) {

	// const playersContainer = document.getElementById("players");

	matchElements.slice().reverse().forEach(match => {
		if (matchs.every(el => el.matchId != match.id)) {
			if (match.id == window.selfMatchId)
			{
				if (window.busyElement)
					window.busyElement.classList.remove("invitation-waiting");
				window.busyElement = null;
				if (window.selectedElement)	
					window.selectedElement.classList.remove(
						"invitation-confirmed");
				window.selectedElement = null;
				window.selfMatchId = null;
			}
			// [...match.children].forEach(player => {
			// 	playersContainer.appendChild(player);
			// });
			matchsContainer.removeChild(match);		
		}
	});
}

function updateMatchs(socket, matchs) {

	// console.log("UPDATE MATCH", matchs);

    const matchsContainer = document.getElementById("matchs");
	let matchElements = [...matchsContainer.children];
		
	removeMatchs(socket, matchs, matchsContainer, matchElements);
	matchElements = [...matchsContainer.children];
	matchs.forEach(match => {	
		if (matchElements.every(el => el.id != match.matchId))		
			addToMatchs(socket, matchsContainer, match);
		else			
			matchElements.forEach(el => {
				if (el.id == match.matchId)
					moveSimplePlayerInMatch(el, match);
			});	
	});
	setSelfMatchId();	
}

// function updateSimpleMatchPlayers(plys) {

// 	console.log("MATCH SIMPLE PLAYERS UPDATE ", plys);	

// 	// const tournament = document.getElementById("tournaments").querySelector(
// 	// 	`[id='${plys.tournamentId}']`
// 	// );
// 	// if (!tournament)
// 	// 	return;
	
// 	const localMatch = tournament.querySelector(`#${plys.localMatchId}`);
// 	if (!localMatch)
// 		return;

// 	const localP1 = localMatch.querySelector(`#pl1`);
// 	const localP2 = localMatch.querySelector(`#pl2`);
// 	const specCont = localMatch.querySelector(`#specs`);

// 	const specs = [...specCont.children]

// 	plys.players.forEach(player => {	
// 		if (specs.every(el => el.id != player.playerId))
// 		{		
// 			const winPly = window.players.find(el => el.id == player.playerId);
// 			if (plys.p1Id == winPly.id)
// 			{			
// 				localP1.appendChild(winPly);
// 			}
// 			else if (plys.p2Id == winPly.id)
// 			{		
// 				localP2.appendChild(winPly);
// 			}
// 			else
// 			{
// 				specCont.appendChild(winPly);
// 			}
// 		}
// 	});
// }

function sendConfirmation(socket, applicantId, applicantName, response) {

	// console.log(`i will send ${response} to applicant: ${applicantName}`);

	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "confirmation",
			response: response,
			applicantId: applicantId
		}));
}

function invitationCancelled(targetName) {

	// console.log(`invitation with ${targetName} is cancelled`);

    messagePopUp('https://github.com/dansylvain/pictures/blob/main/non-je-ne-contracte-pas.gif?raw=true', `invitation with ${targetName} is cancelled`)
	// alert(`invitation with ${targetName} is cancelled`);
	if (window.busyElement)	
		window.busyElement.classList.remove("invitation-waiting");
	window.busyElement = null;
	if (window.selectedElement)		
		window.selectedElement.classList.remove("invitation-confirmed");	
	window.selectedElement = null;
	window.selfMatchId = null;	
}

function selectedBusy() {

    messagePopUp('https://github.com/dansylvain/pictures/blob/main/non-je-ne-contracte-pas.gif?raw=true', "selectedBusy")

	// alert("selectedBusy");
	if (window.busyElement)
		window.busyElement.classList.remove("invitation-waiting");
	window.busyElement = null;
}

function invitationRefused(targetName) {

    messagePopUp('https://github.com/dansylvain/pictures/blob/main/non-je-ne-contracte-pas.gif?raw=true', ' ne contracte pas...')

    if (window.busyElement)
		window.busyElement.classList.remove("invitation-waiting");
	window.busyElement = null;
}

function messagePopUp(url, text)
{
    Swal.fire({
        title: 'Oops!',
        text: text,
        imageUrl: url,
        imageWidth: 300,
        imageHeight: 300,
        imageAlt: 'GIF fun',
      });
}

function invitationConfirmed(matchId, targetId) {

    // document.getElementById("response").innerHTML = '<img id="myGif" src="https://media1.tenor.com/m/A-ozELwp694AAAAC/thumbs-thumbs-up-kid.gif" alt="gif marrant">';
	// setTimeout(() => {
    //     document.getElementById("myGif")?.remove();
    //   }, 3000);
    
    window.selectedElement = document.getElementById("players")
		.querySelector(`[id='${targetId}']`)
	if (window.selectedElement)
	{
		window.busyElement = window.selectedElement
		window.busyElement.classList.remove("invitation-waiting");
		window.selectedElement.classList.add("invitation-confirmed")	
	}
	window.selfMatchId = matchId;
}

function sendPlayerClick(socket, event, selected)
{
	window.selectedElement = selected;
	event.stopPropagation();
	if (!window.busyElement)
		window.busyElement = selected;
	window.busyElement.classList.add("invitation-waiting")
	let name = selected.name;
	const input = document.getElementById("match-player-name");
	
	if (selected.id == window.selfId)
	{		
		name = input.value;
		if (name.trim() === "" && input.style.display === "block")
		{
            messagePopUp('https://github.com/dansylvain/pictures/blob/main/non-je-ne-contracte-pas.gif?raw=true', "enter a name for second player")

			// alert("enter a name for second player");			
			return;
		}
		input.style.display = "block";	
	}
	else
		input.style.display = "none";	
	if (name.trim() === "")
		return;		
	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "playerClick",
			selectedId: Number(selected.id),
			selectedName: name
		}));
}

// function selfInvitation(event, socket)
// {
// 	event.stopPropagation();
// }

// function addPlayerToContainer(socket, container, playerId) {

// 	const div = document.createElement("div");
// 	div.className = "user";
// 	div.textContent = `user: ${playerId}`;
// 	div.id = playerId;	
// 	if (playerId === window.selfId)
// 		div.classList.add("self-player");
// 	// 	div.onclick = event => {
// 	// 		selfInvitation(event, socket)
// 	// 		event.stopPropagation();
// 	// 		alert("you can't choose yourself");
// 	// 	}		
// 	// }
// 	// else	
// 	div.onclick = event => sendPlayerClick(socket, event, div);	
//     container.appendChild(div);
// }

// function updatePlayers(socket, players) {

//     const playersContainer = document.getElementById("players");
// 	let playerElements = [...playersContainer.children];	
  
// 	playerElements.slice().reverse().forEach(player => {	
// 		if (players.every(el => el.playerId != player.id))		
// 			playersContainer.removeChild(player);					
// 	});
// 	playerElements = [...playersContainer.children];
// 	players.forEach(player => {	
// 		if (playerElements.every(el => el.id != player.playerId))		
// 			addPlayerToContainer(socket, playersContainer, player.playerId);		
// 	});	
// }



// function setSelfId(selfId) {

// 	window.selfId = selfId;	
// 	document.getElementById("player").innerText = 
// 		"Je suis le joueur " + window.selfId + " " + window.user_name;	
// }

function invitation(socket, data) {

	switch (data.subtype)
	{
		case "back":				
			if (data.response === "selfBusy")
                messagePopUp('https://github.com/dansylvain/pictures/blob/main/non-je-ne-contracte-pas.gif?raw=true', "selfBusy")
				// alert("selfBusy");
			else if (data.response === "selectedBusy")
				selectedBusy();	
			break;
		case "demand":
			receiveInvitation(socket, data.applicantId, data.applicantName);
			break;
		case "cancel":
			invitationCancelled(data.targetName);
			break;
		case "confirmation":		
			if (data.response)
				invitationConfirmed(data.matchId, data.targetId)
			else if (data.applicantId == window.selfId)		
				invitationRefused(data.targetName)
			break;	
		default:
			break;	
	}
}

function onSimpleMatchMessage(event, socket) {

	// console.log("Message reçu :", event.data);
	const data = JSON.parse(event.data);
	
	switch (data.type)
	{
		// case "selfAssign":
		// 	setSelfId(data.selfId);
		// 	break;
		case "newPlayerId":
			connectNewMatchPlayer(data.playerId, data.playerName);
		break;
		case "playerList":
			window.simplePlayersList = data.players;		
			updateSimplePlayers(socket, data.players);
			break;
		case "matchList":
			updateSimplePlayersCont(window.simplePlayersList);
			updateMatchs(socket, data.matchs);
			break;
		case "invitation":
			invitation(socket, data)
			break;
		default:				
			break;
	}
}

function closeSimpleMatchSocket() {

	if (typeof stopMatch === 'function')
		stopMatch(window.selfMatchId);
    if (
		window.simpleMatchSocket && 
		window.simpleMatchSocket.readyState === WebSocket.OPEN
	)
        window.simpleMatchSocket.close();    
}

function updateSimplePlayers(socket, playersUp)
{
	// console.log("UPDATE PLAYERS ", playersUp);

	updateSimpleWinPlayers(socket, playersUp);
	updateSimplePlayersCont(playersUp);
}

function updateSimpleWinPlayers(socket, playersUp)
{
	// console.log("UPDATE SIMPLE WIN PLAYERS ", playersUp);

	playersUp.forEach(plyUp => {
		if (window.simplePlayers.every(el => el.id != plyUp.playerId))
		{
			const newPlayerEl = createSimplePlayerElement(
				socket, plyUp.playerId, plyUp.playerName);
			window.simplePlayers.push(newPlayerEl);
		}	
	});
	window.simplePlayers = window.simplePlayers.filter(winPly => {
		if (playersUp.every(el => el.playerId != winPly.id))				
			return winPly.remove(), false
		else
			return true;				
	});
}

function updateSimplePlayersCont(playersUp) {

	// console.log("UPDATE SIMPLE PLAYERS CONT ", playersUp);

	const playersCont = document.getElementById("players");
	const playerElements = [...playersCont.children];

	playersUp.forEach(plyUp => {
		if (playerElements.every(el => el.id != plyUp.playerId))
		{
			const winPly = window.simplePlayers.find(el => el.id == plyUp.playerId);
			playersCont.appendChild(winPly);
		}	
	});
}

function createSimplePlayerElement(socket, playerId, playerName) {

	// console.log("CREATE PL ELEMENT ", playerId);
	const div = document.createElement("div");
	div.className = "user";
	div.textContent = playerName;
	div.id = playerId;
	div.name = playerName;	
	if (playerId == window.selfId)
		div.classList.add("self-player");
	div.onclick = event => sendPlayerClick(socket, event, div);	  
	return div;
}

function initSimpleMatch() {
	
	// console.log("INIT SIMPLE MATCH");	
	if (typeof closeTournamentSocket === 'function') 
		closeTournamentSocket();
	else 
		// console.log("closeTournamentSocket is not define");
	
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
        window.pidom = "localhost:8443";
	else
		window.pidom = window.location.hostname + ":8443";

	// console.log("INIT SIMPLE MATCH");
    if (window.simpleMatchSocket)
        window.simpleMatchSocket.close();
    window.simpleMatchSocket = new WebSocket(
        `wss://${window.pidom}/ws/tournament/simple-match/${window.selfId}/${window.selfName}/`
    );
	window.simpleMatchSocket.onopen = () => {
        // console.log("Connexion Simple Match établie 😊");	
	}
	window.simpleMatchSocket.onclose = () => {
		// console.log("Connexion Simple Match disconnected 😈");
	};	
	window.simpleMatchSocket.onmessage = event =>
		onSimpleMatchMessage(event, window.simpleMatchSocket);
}
