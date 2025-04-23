
window.players = []
window.websockets = []

function initTournamentDomain()
{
	if (
		window.location.hostname === "localhost" ||
		window.location.hostname === "127.0.0.1"
	)
        window.pidom = "localhost:8443";
	else
		window.pidom = window.location.hostname + ":8443";
}

function initTournament()
{	
	initTournamentDomain();
	closeWsTournament();	
    window.tournamentSocket = new WebSocket(
        `wss://${window.pidom}/ws/tournament/tournament/` + 
		`${window.selfId}/${window.selfName}/${window.selfId}/`
    );
	window.tournamentSocket.onmessage = event =>
		onTournamentMessage(event, window.tournamentSocket);
}

function messagePopUp(titre, url, text, traduction, start_var, end_var)
{
	const options = {
		title: titre,
		html:
			`<span>${start_var}</span><span data-translate="${traduction}">` +
			`${text}</span><span>${end_var}</span>`,
		imageUrl: url,
		imageWidth: 300,
		imageHeight: 300,
		imageAlt: 'GIF fun'
	};

	if (url == "https://dansylvain.github.io/pictures/trumpDance.webp")
	{
		options.backdrop = `
			rgba(2, 243, 14, 0.64)
			url("https://dansylvain.github.io/pictures/final-conf.gif")
			center center/cover
			no-repeat
			fixed
		`;
	}
	Swal.fire(options);
}

function connectNewPlayer(playerId, playerName)
{
	if (!playerId)
	{
        messagePopUp(
			'💥 Oops! 💥',
			'https://dansylvain.github.io/pictures/travolta.webp',
			": Player name already exists!",
			": Player name already exists!", playerName, ""
		);			
		window.websockets = window.websockets.filter(
			ws => ws.playerId !== undefined
		);	
		return;
	}
	const ws = window.websockets.find(ws => ws.playerName === playerName);	
	ws.playerId = playerId;
	const socket = new WebSocket(
        `wss://${window.pidom}/ws/tournament/tournament/` +
		`${playerId}/${playerName}/${window.selfId}/`
    );
	ws.socket = socket;
	socket.onclose = () => {			
		window.websockets = window.websockets.filter(
			ws => ws.socket !== socket
		);	
	};	
} 
  
function newPlayer(socket)
{  
	const playerName = document.getElementById("player-name").value;

	if (playerName.trim() === "")	
        return messagePopUp(
			'🔤 Oops! 🔤',
			'https://dansylvain.github.io/pictures/travolta.webp',
			"Enter a name!", "Enter a name!", "", ""
		);	
	if (window.websockets.length >= 3)
        return messagePopUp(
			'🚫 Oops! 🚫', 'https://dansylvain.github.io/pictures/marioNo.webp',
			"You can't create more than three players!",
			"You can't create more than three players!", "", ""
		);	
	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "newPlayer",
			playerName: playerName			
		}));
	window.websockets.push({playerName: playerName});
}
  
function newTournament(socket)
{  
	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "newTournament"			
		}));
}

function enterTournament(socket, tournamentId)
{
	const scripts = Array.from(document.getElementsByTagName("script"));
	 
	if (scripts.some(script => script.className === "match-script")) 	
		return;	
	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "enterTournament",
			tournamentId: tournamentId			
		}));
}

function closeWsTournament()
{
	const closeWs = socket => {
		if (socket && socket.readyState === WebSocket.OPEN)	
			socket.close();					
	};
    closeWs(window.tournamentSocket);
    window.websockets?.forEach(ws => closeWs(ws.socket));
}
window.closeWsTournament = closeWsTournament;

function onTournamentMessage(event, socket)
{
	const data = JSON.parse(event.data);
	
	switch (data.type)
	{
		case "tournamentResult":
			tournamentResult(data);
		break;
		case "newPlayerId":
			connectNewPlayer(data.playerId, data.playerName);
		break;
		case "playerList":		
			window.playersList = data.players;
			updatePlayers(socket, data.players);
			updateTournamentsPlayers(window.tournamentList);
			updateMatchsPlayers(window.pack);
			break;
		default:				
			sequelSwitch(data, socket);
	}
}

function sequelSwitch(data, socket)
{
	switch (data.type)
	{		
		case "tournamentList":
			updatePlayers(socket, window.playersList);
			window.tournamentList = data.tournaments; 
			updateTournaments(socket, data.tournaments);
			break;
		case "linkMatch":
			linkMatch(data);			
			break;
		case "matchResult":
			matchResult(data);			
			break;
		case "matchsPlayersUpdate":		
			updatePlayersCont(window.playersList)
			updateTournamentsPlayers(window.tournamentList);
			window.pack = data.pack;
			updateMatchsPlayers(data.pack);			
			break;
		default:				
			break;
	}
}

function areMyPlayersPlayInSomeMatch(data)
{
	return data.matchs.some(match =>
		areMyPlayersIn([match.linkMatch.p1Id, match.linkMatch.p2Id])
	);
}

function castDictToListId(players)
{
	return players.map(player => player['playerId']);
}

function areMyPlayersInTournament(data)
{
	return (window.tournamentList && window.tournamentList.some(tour => 
		tour.tournamentId == data.tournamentId
		&& areMyPlayersIn(castDictToListId(tour.players))	
	));
}
			
function tournamentResult(data)
{	
	if (!(areMyPlayersPlayInSomeMatch(data) || areMyPlayersInTournament(data)))
		return;
    messagePopUp(
		'🏆 Yeah! 🏆', 'https://dansylvain.github.io/pictures/trumpDance.webp',
		" won the tournament!", " won the tournament!", data.winnerName, ""
	);	
}

function updatePlayers(socket, playersUp)
{
	updateWinPlayers(socket, playersUp);
	updatePlayersCont(playersUp);
}

function updateWinPlayers(socket, playersUp)
{
	playersUp.forEach(plyUp => {
		if (window.players.every(el => el.id != plyUp.playerId))
		{
			const newPlayerEl = createPlayerElement(
				socket, plyUp.playerId, plyUp.playerName);
			window.players.push(newPlayerEl);
		}	
	});
	window.players = window.players.filter(winPly => {
		if (playersUp.every(el => el.playerId != winPly.id))				
			return winPly.remove(), false
		else
			return true;				
	});
}

function createPlayerElement(socket, playerId, playerName)
{
	const div = document.createElement("div");
	div.className = "user";
	div.textContent = playerName;
	div.id = playerId;
	const ws = window.websockets.find(ws => ws.playerId == playerId);	
	if (playerId == window.selfId)	
		div.classList.add("self-player");	
	else if (ws)
		div.classList.add("phantom");
	dragPlayer(div);
	return div;
}

function dropPlayersZone()
{
	const players = document.getElementById("players");
	if (!players)
		return;
	removeOldEventListener(players);
	players.dragOver = function(e) {e.preventDefault();};
	players.drop = function(e) {
		e.preventDefault();
		const elementId = e.dataTransfer.getData("text/plain");
		const ws = window.websockets.find(el => el.playerId == elementId);	
		if (!ws && window.selfId != elementId)
		{
            messagePopUp('🚷 Oops! 🚷',
				'https://dansylvain.github.io/pictures/marioNo.webp',
				"Not your player!", "Not your player!", "", "");
			return;
		}
		if (ws)			
			quitTournament(ws.socket);
		else if (window.selfId == elementId)
			quitTournament(window.tournamentSocket);
		document.getElementById("clone")?.remove();	
	};
	addNewEventListener(players);	
}

function dropTrash()
{
	const trash = document.getElementById("trash");
	if (!trash)
		return;
	removeOldEventListener(trash);
	trash.dragOver = function(e) {e.preventDefault();};
	trash.drop = function(e) {
		e.preventDefault();
		const elementId = e.dataTransfer.getData("text/plain");
		const ws = window.websockets.find(el => el.playerId == elementId);	
		if (!ws && window.selfId != elementId)
		{
            messagePopUp('🚷 Oops! 🚷',
				'https://dansylvain.github.io/pictures/marioNo.webp',
				"Not your player!", "Not your player!", "", "");			
		}
		else if (window.selfId == elementId)	
		{
			messagePopUp('🚯 Oops! 🚯',
				'https://dansylvain.github.io/pictures/marioNo.webp',
				"You can't drop yourself!", "You can't drop yourself!", "", "");			
		}
		else
			cloneDisappear(e, ws);	
	};
	addNewEventListener(trash);	
}

function cloneDisappear(e, ws)
{
	const clone = document.getElementById("clone");
	clone.style.left = `${e.clientX - clone.offsetWidth / 2}px`;
	clone.style.top = `${e.clientY - clone.offsetHeight / 2}px`;
	clone.style.position = "fixed";
	clone.style.opacity = "1";
	clone.classList.add("disappear");
	setTimeout(()=>{
		if (ws.socket && ws.socket.readyState === WebSocket.OPEN)	
			ws.socket.close();	
		clone.remove();	
	}, 500);
}

function dropMatch(div, lk, overlay)
{
	removeOldEventListener(div);
	div.dragOver = function(e) {e.preventDefault();};
	div.drop = function(e) {
		e.preventDefault();
		const elementId = e.dataTransfer.getData("text/plain");
		enterTournamentMatch(lk, overlay);
	}
	addNewEventListener(div);	
}

function removeOldEventListener(div)
{
	if (div.drop)
	{
		div.removeEventListener("dragover", div.dragOver);
		div.removeEventListener("drop", div.drop);
	}
}

function addNewEventListener(div)
{
	div.addEventListener("dragover", div.dragOver);
	div.addEventListener("drop", div.drop);
}

dropTrash();
dropPlayersZone();

window.addEventListener('DOMContentLoaded', ()=> {
	dropTrash();
	dropPlayersZone();
});

document.body.addEventListener('htmx:afterSwap', ()=> {
	dropTrash();
	dropPlayersZone();   
});

function dragPlayer(div)
{
	div.draggable = true;
	div.addEventListener("dragstart",
		e => {
			e.dataTransfer.setData("text/plain", e.target.id);
			const clone = div.cloneNode(true);
			clone.id = "clone";
			clone.style.borderRadius = "12px";	
			const rect = div.getBoundingClientRect();
			clone.style.width = `${rect.width * 0.9}px`;
			clone.style.position = "absolute";
			clone.style.top = "-100";
			clone.style.left = "-100";
			document.body.appendChild(clone);		  
			const offsetX = clone.offsetWidth / 2;
			const offsetY = clone.offsetHeight / 2;
			e.dataTransfer.setDragImage(clone, offsetX, offsetY);		
		} );
}

function quitTournament(socket)
{
	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "quitTournament"						
		}));
}

function updatePlayersCont(playersUp)
{
	const playersCont = document.getElementById("players");
	const playerElements = [...playersCont.children];

	playersUp.forEach(plyUp => {
		if (playerElements.every(el => el.id != plyUp.playerId))
		{
			const winPly = window.players.find(el => el.id == plyUp.playerId);
			playersCont.appendChild(winPly);
		}	
	});
}

function updateTournaments(socket, tournamentsUp)
{
	const tournamentsCont = document.getElementById("tournaments");
	const tournamentEls = [...tournamentsCont.children];
	const patternPromises = [];
	tournamentsUp.forEach(tourUp => {
		if (tournamentEls.every(el => el.id != tourUp.tournamentId))
			addToTournaments(tournamentsCont, tourUp);
		if (tourUp.matchs.length > 0)			
			patternPromises.push(getPattern(tourUp.tournamentId));			
	});
	tournamentEls.slice().reverse().forEach(tourEl => {
		if (tournamentsUp.every(el => el.tournamentId != tourEl.id))
		{
			if (tourEl.id == window.actualScriptTid)
				delTournamentMatchScript();	
			tournamentsCont.removeChild(tourEl);		
		}
	});
	updateTournamentsPlayers(tournamentsUp);
	patternPromises.forEach(promise => promise.then(value => {
		if (value)
		{		
			updateTournamentsPlayers(tournamentsUp);
			updateLinkMatchAndResult(tournamentsUp);
		}
	}));
}

function addToTournaments(tournamentsContainer, tournament)
{
	const div = document.createElement("div");	
	div.className = "tournament";	
	div.id = tournament.tournamentId;
	div.className = "tournament-cont";
	const overlayPattern = document.createElement("div");
	overlayPattern.id = "overlay-pattern";
	const playersCont = document.createElement("div");
	playersCont.id = "players-cont";
	div.appendChild(playersCont);
	div.appendChild(overlayPattern);
	dropTournament(div, tournament.tournamentId);
	tournamentsContainer.appendChild(div);	
}

function dropTournament(div, tournamentId)
{
	div.addEventListener("dragover", e => e.preventDefault());
	div.addEventListener("drop", e => {	
		e.preventDefault();
		const elementId = e.dataTransfer.getData("text/plain");
		const ws = window.websockets.find(el => el.playerId == elementId);	
		if (!ws && window.selfId != elementId)
		{
            messagePopUp('🚷 Oops! 🚷',
				'https://dansylvain.github.io/pictures/marioNo.webp',
				"Not your player!", "Not your player!", "", "")
			return;
		}
		if (ws)
			enterTournament(ws.socket, tournamentId);
		else
			enterTournament(window.tournamentSocket, tournamentId);
		document.getElementById("clone")?.remove();
	});
}

function catchPlayersInMatch(lk)
{
	const wscopy = window.websockets.map( ws => ({...ws}))
	wscopy.push({playerId: window.selfId, playerName: window.selfName,
		socket:window.tournamentSocket});
	const p1 = wscopy.find(ws => ws.playerId == lk.p1Id);
	const p2 = wscopy.find(ws => ws.playerId == lk.p2Id);
	if (p1)
		enterTournament(p1.socket, lk.tournamentId);
	if (p2)
		enterTournament(p2.socket, lk.tournamentId);
	if (!p1 && !p2)
		return [window.selfId, window.selfName, 0, ""];
	else if (p1 && p2)
		return [p1.playerId, p1.playerName, p2.playerId, p2.playerName];
	else if (p1)
		return [p1.playerId, p1.playerName, 0, ""];
	else if (p2)
		return [p2.playerId, p2.playerName, 0, ""];
}

function getPattern(tournamentId)
{
	const tournament = document.getElementById("tournaments").querySelector(
		`[id='${tournamentId}']`);
	if (!tournament)
		return Promise.resolve(false);
	const overlay = tournament.querySelector("#overlay-pattern");
	if (!overlay) 
		return Promise.resolve(false);
	if (overlay.innerHTML.trim() !== "")
		return Promise.resolve(true);
	return fetch(`/tournament/tournament-pattern/${tournamentId}/`)
	.then(response => {
		if (!response.ok) 
			throw new Error(`Error HTTP! Status: ${response.status}`);		  
		return response.text();
	})
	.then(data => {return loadTournamentHtml(data, overlay), true})
	.catch(error => console.log(error));			
}

function updateTournamentsPlayers(tournamentsUp)
{
	if (!tournamentsUp)
		return;

	const tournamentsCont = document.getElementById("tournaments");
	const tournamentEls = [...tournamentsCont.children];

	tournamentsUp.forEach(tourUp => {
		const tourEl = tournamentEls.find(el => el.id == tourUp.tournamentId)
		if (tourEl)
		{
			const playersCont = tourEl.querySelector("#players-cont");
			const playerElements = [...playersCont.children];
			tourUp.players.forEach(plyUp => {
				if (playerElements.every(el => el.id != plyUp.playerId))
				{
					const winPly = window.players.find(
						el => el.id == plyUp.playerId);
					if (winPly)
						playersCont.appendChild(winPly);
				}
			});
		}	
	});
}

function updateLinkMatchAndResult(tournamentsUp)
{
	tournamentsUp.forEach(tourUp => {
		tourUp.matchs.forEach(matchUp => {
			if (matchUp.linkMatch)			
				linkMatch(matchUp.linkMatch);
			if (matchUp.matchResult)				
				matchResult(matchUp.matchResult);
			if (matchUp.matchPlayersUpdate)				
				updateMatchPlayers(matchUp.matchPlayersUpdate);
		});
	});
}

function linkMatch(lk)
{
	const tournament = document.getElementById("tournaments").querySelector(
		`[id='${lk.tournamentId}']`
	);
	if (!tournament)
		return;	
	const localMatch = tournament.querySelector(`#${lk.localMatchId}`);
	if (!localMatch)
		return;	
	const overlay = tournament.querySelector("#overlay-match");
	const localP1 = localMatch.querySelector(`#pl1`);
	const localP2 = localMatch.querySelector(`#pl2`);
	localP1.innerText = lk.p1Name;
	localP2.innerText = lk.p2Name;
	setNextMatch(lk, localMatch);	
	if (lk.p1Id && lk.p2Id)
	{
		localMatch.onclick = ()=> enterTournamentMatch(lk, overlay);
		dropMatch(localMatch, lk, overlay);	
	}
}

function setNextMatch(lk, localMatch)
{	
	if (areMyPlayersIn([lk.p1Id, lk.p2Id]))	
	{
		localMatch.classList.remove("spec-match");
		localMatch.classList.add("next-match");	
	}
	else
	{
		localMatch.classList.remove("next-match");
		localMatch.classList.add("spec-match");
	}
}

function enterTournamentMatch(lk, overlay)
{
	if (isYetInMatch())
		return;	
	const [playerId, playerName, player2Id, player2Name] =
		catchPlayersInMatch(lk);
	const dim = document.getElementById("dim");
	fetch(
		`/match/match${dim.value}d/` +
		`?matchId=${lk.matchId}` +
		`&playerId=${playerId}&playerName=${playerName}` +
		`&player2Id=${player2Id}&player2Name=${player2Name}`
	)
	.then(response => {
		if (!response.ok) 
			throw new Error(`Error HTTP! Status: ${response.status}`);		  
		return response.text();
	})
	.then(data => {
		setTournamentSelfMatchId(lk);
		delTournamentMatchScript();
		window.actualScriptTid = lk.tournamentId;
		loadTournamentHtml(data, overlay);
	})
	.catch(error => console.log(error))
}

function isYetInMatch()
{	
	const scripts = [...document.getElementsByTagName("script")];

	if (scripts.some(script => script.className === "match-script"))	
		return true;
	return false;	
}

function areMyPlayersIn(playersId)
{
	return playersId.some(playerId => {
		if (window.selfId == playerId)
			return true;
		const ws = window.websockets.find(ws => ws.playerId == playerId);
		return !!ws;
	});
}

function setTournamentSelfMatchId(lk)
{		
	if (areMyPlayersIn([lk.p1Id, lk.p2Id]))	
		window.selfMatchId = lk.matchId;
	else
		window.selfMatchId = null;
}

function delTournamentMatchScript()
{
	const scripts = document.querySelectorAll("script.match-script");		
	scripts.forEach(oldScript => oldScript.remove());	
}

function loadTournamentHtml(data, overlay)
{	
	delTournamentMatchScript();	
	overlay.innerHTML = data;
	const scripts = overlay.getElementsByTagName("script");

	for (const script of scripts) 
	{		
		const newScript = document.createElement("script");
		newScript.className = script.className;
		if (script.src)
		{	
			newScript.src = script.src + "?t=" + Date.now();
			newScript.async = true;  
			newScript.onload = script.onload;
		} 
		else 			
			newScript.textContent = script.textContent;		
		document.body.appendChild(newScript); 
	}
}

function matchResult(rsl)
{
	const tournament = document.getElementById("tournaments").querySelector(
		`[id='${rsl.tournamentId}']`
	);
	if (!tournament)
		return;
	const localMatch = tournament.querySelector(`#${rsl.localMatchId}`);
	if (!localMatch)
		return;
	localMatch.onclick = "";
	addWinnerLooserClass(rsl, localMatch);
}

function addWinnerLooserClass(rsl, localMatch)
{
	const localP1 = localMatch.querySelector(`#pl1`);
	const localP2 = localMatch.querySelector(`#pl2`);

	if (rsl.winnerId && rsl.winnerId == rsl.p1Id)
	{
		localP1.classList.add("winner");
		localP2.classList.add("looser");
	}
	else if (rsl.winnerId && rsl.winnerId == rsl.p2Id)
	{
		localP2.classList.add("winner");
		localP1.classList.add("looser");
	}
	else
	{
		localP2.classList.add("undef");
		localP1.classList.add("undef");
	}
}

function updateMatchsPlayers(pack)
{
	if (pack)
		pack.forEach(plys => updateMatchPlayers(plys));
}

function updateMatchPlayers(plys)
{
	const tournament = document.getElementById("tournaments").querySelector(
		`[id='${plys.tournamentId}']`
	);
	if (!tournament)
		return;	
	const localMatch = tournament.querySelector(`#${plys.localMatchId}`);
	if (!localMatch)
		return;
	const localP1 = localMatch.querySelector(`#pl1`);
	const localP2 = localMatch.querySelector(`#pl2`);
	const specCont = localMatch.querySelector(`#specs`);
	const specs = [...specCont.children]
	plys.players.forEach(player => {	
		if (specs.every(el => el.id != player.playerId))
		{	
			const winPly = window.players.find(el => el.id == player.playerId);		
			if (plys.p1Id == winPly.id)
				localP1.appendChild(winPly);			
			else if (plys.p2Id == winPly.id)
				localP2.appendChild(winPly);			
			else			
				specCont.appendChild(winPly);			
		}
	});
}
