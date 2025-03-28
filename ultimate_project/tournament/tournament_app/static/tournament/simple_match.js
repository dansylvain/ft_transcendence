window.simplePlayers = []

/**========================================================================
 * !                              CODE CHANGES
 *   these functions were added.
 *   the function "receiveInvitation" was modified (see below)
 *========================================================================**/

let isPageVisible = !document.hidden;
let pendingInvitations = [];

document.addEventListener('visibilitychange', () => {
    isPageVisible = !document.hidden;
    if (isPageVisible) {
        // Si la page devient active, on traite les notifications en attente
        handlePendingInvitations();
    }
});


function handlePendingInvitations() {
    // Traite toutes les invitations en attente lorsque la page devient active
    pendingInvitations.forEach(invitation => {
        const { applicantId, socket } = invitation;
        const userConfirmed = confirm(`Vous avez une invitation de ${applicantId}`);
        sendConfirmation(socket, applicantId, userConfirmed);
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
        console.log("Notification permission not granted");
    }
}

function receiveInvitation(socket, applicantId) {
    console.log("I have had an invitation from: " + applicantId);
    
    if (isPageVisible) {
        // Si l'onglet est actif, demande la confirmation immédiatement
        const userConfirmed = confirm(`You have an invitation from ${applicantId}`);
        sendConfirmation(socket, applicantId, userConfirmed);
    } else {
        // Si l'onglet est en arrière-plan, stocke l'invitation en attente
        pendingInvitations.push({ socket, applicantId });
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
			fetch(
				`/match/match${dim.value}d/` +
				`?matchId=${match.id}&playerId=${window.selfId}`)
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

	console.log("MOVE SIMPLE PLAYER IN MATCH", match);

	if (!match.players)
		return;
	console.log("MOVE SIMPLE PLAYER IN MATCH after return");
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
				window.selectedElement.classList.remove("invitation-confirmed");
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

	console.log("UPDATE MATCH", matchs);

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

function sendConfirmation(socket, applicantId, response) {

	console.log(`i will send ${response} to applicant: ${applicantId}`);

	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "confirmation",
			response: response,
			applicantId: applicantId
		}));
}

function invitationCancelled(targetId) {

	console.log(`invitation with ${targetId} is cancelled`);

	alert(`invitation with ${targetId} is cancelled`);
	if (window.busyElement)	
		window.busyElement.classList.remove("invitation-waiting");
	window.busyElement = null;
	if (window.selectedElement)		
		window.selectedElement.classList.remove("invitation-confirmed");	
	window.selectedElement = null;
	window.selfMatchId = null;	
}

function selectedBusy() {

	alert("selectedBusy");
	if (window.busyElement)
		window.busyElement.classList.remove("invitation-waiting");
	window.busyElement = null;
}

function invitationRefused(targetId) {

	alert("refuse from target: "+ targetId + " " + window.busyElement.id);
	if (window.busyElement)
		window.busyElement.classList.remove("invitation-waiting");
	window.busyElement = null;
}

function invitationConfirmed(matchId, targetId) {

	window.selectedElement = document.getElementById("players")
		.querySelector(`[id='${targetId}']`);
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
	event.stopPropagation();
	if (!window.busyElement)
		window.busyElement = selected;
	window.busyElement.classList.add("invitation-waiting")
	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "playerClick",
			selectedId: Number(selected.id)
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



function setSelfId(selfId) {

	window.selfId = selfId;	
	document.getElementById("player").innerText = 
		"Je suis le joueur " + window.selfId;	
}

function invitation(socket, data) {

	switch (data.subtype)
	{
		case "back":				
			if (data.response === "selfBusy")
				alert("selfBusy");
			else if (data.response === "selectedBusy")
				selectedBusy();	
			break;
		case "demand":
			receiveInvitation(socket, data.applicantId);
			break;
		case "cancel":
			invitationCancelled(data.targetId);
			break;
		case "confirmation":		
			if (data.response)
				invitationConfirmed(data.matchId, data.targetId)
			else if (data.applicantId == window.selfId)		
				invitationRefused(data.targetId)
			break;	
		default:
			break;	
	}
}

function onSimpleMatchMessage(event, socket) {

	console.log("Message reçu :", event.data);
	const data = JSON.parse(event.data);
	
	switch (data.type)
	{
		case "selfAssign":
			setSelfId(data.selfId);
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
	console.log("UPDATE PLAYERS ", playersUp);

	updateSimpleWinPlayers(socket, playersUp);
	updateSimplePlayersCont(playersUp);
}

function updateSimpleWinPlayers(socket, playersUp)
{
	console.log("UPDATE SIMPLE WIN PLAYERS ", playersUp);

	playersUp.forEach(plyUp => {
		if (window.simplePlayers.every(el => el.id != plyUp.playerId))
		{
			const newPlayerEl = createSimplePlayerElement(socket, plyUp.playerId);
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

	console.log("UPDATE SIMPLE PLAYERS CONT ", playersUp);

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

function createSimplePlayerElement(socket, playerId) {

	console.log("CREATE PL ELEMENT ", playerId);
	const div = document.createElement("div");
	div.className = "user";
	div.textContent = `user: ${playerId}`;
	div.id = playerId;	
	if (playerId === window.selfId)
		div.classList.add("self-player");
	div.onclick = event => sendPlayerClick(socket, event, div);	  
	return div;
}

function initSimpleMatch() {
	
	console.log("INIT SIMPLE MATCH");	
	if (typeof closeTournamentSocket === 'function') 
		closeTournamentSocket();
	else 
		console.log("closeTournamentSocket is not define");
	
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
        window.pidom = "localhost:8443";

	console.log("INIT SIMPLE MATCH");
    if (window.simpleMatchSocket)
        window.simpleMatchSocket.close();
    window.simpleMatchSocket = new WebSocket(
        `wss://${window.pidom}/ws/tournament/${window.user_id}/`
    );
	window.simpleMatchSocket.onopen = () => {
		console.log("Connexion Simple Match établie 😊");	
	}
	window.simpleMatchSocket.onclose = () => {
		console.log("Connexion Simple Match disconnected 😈");
	};	
	window.simpleMatchSocket.onmessage = event =>
		onSimpleMatchMessage(event, window.simpleMatchSocket);
}
