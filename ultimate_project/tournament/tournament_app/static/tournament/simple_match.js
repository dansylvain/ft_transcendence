
window.simplePlayers = []

var isPageVisible = isPageVisible || !document.hidden;
var pendingInvitations = pendingInvitations || [];

document.addEventListener('visibilitychange', () => {
    isPageVisible = !document.hidden;
    if (isPageVisible)        
        handlePendingInvitations();    
});

async function invitationPopup(socket, applicantId, applicantName)
{
    const result = await Swal.fire({
        title: '🎮 Yeah! 🎮',
        html:
			`<span>${applicantName}</span><span data-translate="` + 
			` has sent you an invitation!"> has sent you an invitation!</span>`,
        text: ' You have an invitation!',
        imageUrl: 'https://dansylvain.github.io/pictures/thumbs.webp',
        imageWidth: 300,
        imageHeight: 300,
        imageAlt: 'GIF fun',
        showCancelButton: true,
        confirmButtonText: 'Accept',
        cancelButtonText: 'Decline',
		confirmButtonColor: '#3cc13b',
		cancelButtonColor: '#d33',
    });
    sendConfirmation(socket, applicantId, applicantName, result.isConfirmed);
}

function handlePendingInvitations()
{
    pendingInvitations.forEach(invitation => {
        const { applicantId, applicantName, socket } = invitation;
        invitationPopup(socket, applicantId, applicantName);
    });
    pendingInvitations = [];
}

function showNotification(message, applicantId)
{
    if (Notification.permission === "granted") 
        new Notification(message);
    else if (Notification.permission !== "denied")
	{
        Notification.requestPermission().then(permission => {
            if (permission === "granted") 
                new Notification(message);            
        });
    }	   
}

function receiveInvitation(socket, applicantId, applicantName)
{    
    if (isPageVisible)
        invitationPopup(socket, applicantId, applicantName);
    else
        pendingInvitations.push({socket, applicantId, applicantName});   
}

function delSimpleMatchScript()
{
	const scripts = document.querySelectorAll("script.match-script");		
	scripts.forEach(oldScript => oldScript.remove());	
}

function loadSimpleMatchHtml(data, target)
{
	delSimpleMatchScript();	
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

function enterMatch(match)
{
	const dim = document.getElementById("dim");
	let player2Id = 0;
	let player2Name = "";	
	if (match.multy)
	{
		player2Id = -window.selfId;
		player2Name = match.otherName;
	}
	fetch(
		`/match/match${dim.value}d/` +
		`?matchId=${match.matchId}` +
		`&playerId=${window.selfId}&playerName=${window.selfName}` +
		`&player2Id=${player2Id}&player2Name=${player2Name}`
	)
	.then(response => {
		if (!response.ok) 
			throw new Error(`Error HTTP! Status: ${response.status}`);		  
		return response.text();
	})
	.then(data =>{
		setSelfMatchId(match);
		loadSimpleMatchHtml(data, "overlay-match");
	}) 
	.catch(error => console.log(error));	
}

function isMyMatch(match)
{
	return window.selfId == match.playerId || window.selfId == match.otherId;
}

function setSelfMatchId(match)
{	
	if (isMyMatch(match))
		window.selfMatchId = match.matchId;
	else
		window.selfMatchId = null;
}

function moveSimplePlayerInMatch(matchElement, match)
{
	if (!match.players)
		return;
	match.players.forEach(ply => {
		const winPly = window.simplePlayers.find(el => el.id == ply.playerId);
		if (winPly)
			matchElement.appendChild(winPly);
	});	
}

function addToMatchs(matchsContainer, match)
{  	
	const div = document.createElement("div");
	div.className = "match";
	div.textContent = `match: ${match.matchId}`;
	div.id = match.matchId;
	if (isMyMatch(match))
	{
		div.classList.add("self-match");	
		div.selfMatch = true;
	}
	div.onclick = ()=> enterMatch(match);
    matchsContainer.appendChild(div);
	moveSimplePlayerInMatch(div, match);
}

function removeMatchs(matchs, matchsContainer, matchElements)
{
	matchElements.slice().reverse().forEach(match => {
		if (matchs.every(el => el.matchId != match.id))
		{			
			if (match.selfMatch)
			{
				if (window.busyElement)
					window.busyElement.classList.remove("invitation-waiting");
				window.busyElement = null;
				if (window.selectedElement)	
					window.selectedElement.classList.remove(
						"invitation-confirmed");
				window.selectedElement = null;
			}		
			matchsContainer.removeChild(match);		
		}
	});
}

function updateMatchs(socket, matchs)
{
    const matchsContainer = document.getElementById("matchs");
	let matchElements = [...matchsContainer.children];
		
	removeMatchs(matchs, matchsContainer, matchElements);
	matchElements = [...matchsContainer.children];
	matchs.forEach(match => {	
		if (matchElements.every(el => el.id != match.matchId))		
			addToMatchs(matchsContainer, match);
		else			
			matchElements.forEach(el => {
				if (el.id == match.matchId)
					moveSimplePlayerInMatch(el, match);
			});	
	});
}

function sendConfirmation(socket, applicantId, applicantName, response)
{
	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "confirmation",
			response: response,
			applicantId: applicantId
		}));
}

function invitationCancelled(targetName)
{
    messagePopUp(
		'❌ Oops! ❌',
		'https://dansylvain.github.io/pictures/non-je-ne-contracte-pas.webp',
		"Invitation cancelled!", "Invitation cancelled!", "", ""
	);
	if (window.busyElement)	
		window.busyElement.classList.remove("invitation-waiting");
	window.busyElement = null;
	if (window.selectedElement)		
		window.selectedElement.classList.remove("invitation-confirmed");	
	window.selectedElement = null;
}

function selectedBusy()
{
    messagePopUp(
		'🫷 Oops! 🫸',
		'https://dansylvain.github.io/pictures/busy.webp',
		"The player is busy...", "The player is busy...", "", ""
	);
	if (window.busyElement)
		window.busyElement.classList.remove("invitation-waiting");
	window.busyElement = null;
}

function selfBusy()
{
	messagePopUp(
		'⏳ Oops! ⏳',
		'https://dansylvain.github.io/pictures/busy.webp',
		"You are busy...", "You are busy...", "", ""
	);
}

function invitationRefused(targetName)
{
    messagePopUp(
		'❌ Oops! ❌',
		'https://dansylvain.github.io/pictures/non-je-ne-contracte-pas.webp',
		"Invitation cancelled!", "Invitation cancelled!", "", ""
	);
    if (window.busyElement)
		window.busyElement.classList.remove("invitation-waiting");
	window.busyElement = null;
}

function messagePopUp(titre, url, text, traduction, start_var, end_var)
{
    Swal.fire({
        title: titre,
        html:
			`<span>${start_var}</span><span data-translate="${traduction}">` +
			`${text}</span><span>${end_var}</span>`,
        imageUrl: url,
        imageWidth: 300,
        imageHeight: 300,
        imageAlt: 'GIF fun'
    });
}

function invitationConfirmed(matchId, targetId)
{      
    window.selectedElement = document.getElementById("players")
		.querySelector(`[id='${targetId}']`)
	if (window.selectedElement)
	{
		window.busyElement = window.selectedElement;
		window.busyElement.classList.remove("invitation-waiting");
		window.selectedElement.classList.add("invitation-confirmed");	
	}
}

function newLocalMatch()
{
	const input = document.getElementById("match-player-name");		
	const name = input.value;

	if (name.trim() === "" && !window.busyElement)
	{
		messagePopUp(
			'Oops!', 'https://dansylvain.github.io/pictures/travolta.webp',
			"Enter a name for the second player",
			"Enter a name for the second player", "", "");		
		return;
	}
	sendPlayerClick(window.simpleMatchSocket, window.selfId, name);		
}

function playerClick(socket, event, selected)
{
	event.stopPropagation();
	if (selected.id == window.selfId)
		return;
	if (!window.busyElement)
		window.busyElement = selected;
	window.busyElement.classList.add("invitation-waiting");
	sendPlayerClick(socket, selected.id, selected.name);
}

function sendPlayerClick(socket, selectedId, selectedName)
{
	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "playerClick",
			selectedId: Number(selectedId),
			selectedName: selectedName
		}));
}

function invitation(socket, data)
{
	switch (data.subtype)
	{
		case "back":	   		
			if (data.response === "selfBusy")
				selfBusy();		
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

function onSimpleMatchMessage(event, socket)
{
	const data = JSON.parse(event.data);
	
	switch (data.type)
	{
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
			invitation(socket, data);
			break;
		default:				
			break;
	}
}

function closeWsSimpleMatch()
{
	const closeWs = socket => {
		if (socket && socket.readyState === WebSocket.OPEN)	
			socket.close();					
	}; 
    closeWs(window.simpleMatchSocket);   
}
window.closeWsSimpleMatch = closeWsSimpleMatch;

function updateSimplePlayers(socket, playersUp)
{
	updateSimpleWinPlayers(socket, playersUp);
	updateSimplePlayersCont(playersUp);
}

function updateSimpleWinPlayers(socket, playersUp)
{
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
			return winPly.remove(), false;
		else
			return true;				
	});
}

function updateSimplePlayersCont(playersUp)
{
	const playersCont = document.getElementById("players");
	const playerElements = [...playersCont.children];

	playersUp.forEach(plyUp => {
		if (playerElements.every(el => el.id != plyUp.playerId))
		{
			const winPly = window.simplePlayers.find(
				el => el.id == plyUp.playerId
			);
			playersCont.appendChild(winPly);
		}	
	});
}

function createSimplePlayerElement(socket, playerId, playerName)
{
	const div = document.createElement("div");
	div.className = "user";
	div.textContent = playerName;
	div.id = playerId;
	div.name = playerName;	
	if (playerId == window.selfId)
		div.classList.add("self-player");
	div.onclick = event => playerClick(socket, event, div);	  
	return div;
}

function initSimpleMatchDomain()
{
	if (
		window.location.hostname === "localhost" ||
		window.location.hostname === "127.0.0.1"
	)
        window.pidom = "localhost:8443";
	else
		window.pidom = window.location.hostname + ":8443";
}

function initSimpleMatch()
{	
	window.busyElement = null;	
	initSimpleMatchDomain();
	closeWsSimpleMatch();	
    if (window.simpleMatchSocket)
        window.simpleMatchSocket.close();
    window.simpleMatchSocket = new WebSocket(
        `wss://${window.pidom}/ws/tournament/simple-match/` + 
		`${window.selfId}/${window.selfName}/`
    );
	window.simpleMatchSocket.onmessage = event =>
		onSimpleMatchMessage(event, window.simpleMatchSocket);
}
