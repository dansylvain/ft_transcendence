
window.players = []
window.websockets = []

function initTournament() {
		
	if (typeof closeSimpleMatchSocket === 'function') 
		closeSimpleMatchSocket();
	else 
		console.log("closeSimpleMatch not define");
	
	if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
        window.pidom = "localhost:8443";
	else
		window.pidom = window.location.hostname + ":8443";

	console.log("INIT TOURNAMENT");
    if (window.tournamentSocket)
        window.tournamentSocket.close();
    window.tournamentSocket = new WebSocket(
        `wss://${window.pidom}/ws/tournament/tournament/${window.selfId}/${window.selfName}/${window.selfId}/`
    );
	window.tournamentSocket.onopen = () => {
		console.log("Connexion Tournament établie 😊");		
	}
	window.tournamentSocket.onclose = () => {
		console.log("Connexion Tournament disconnected 😈");
		alert("Connexion Tournament disconnected 😈");
	};	
	window.tournamentSocket.onmessage = event =>
		onTournamentMessage(event, window.tournamentSocket);
}

function messagePopUp(titre, url, text, traduction, start_var, end_var)
{
    Swal.fire({
        title: titre,
        html: `<span>${start_var}</span><span data-translate="${traduction}">${text}</span><span>${end_var}</span>`,
        imageUrl: url,
        imageWidth: 300,
        imageHeight: 300,
        imageAlt: 'GIF fun'
      });
}

function connectNewPlayer(playerId, playerName)
{
	console.log("CONNECT NEW PLAYER ", playerId, " ", playerName);

	if (!playerId)
	{
        messagePopUp('Oops!', 'https://dansylvain.github.io/pictures/travolta.webp', ": Player name already exists!", ": Player name already exists!", playerName, "")
		// alert("player name yet exist!");
		console.log(window.websockets);
		window.websockets = window.websockets.filter(ws => ws.playerId !== undefined);	
		console.log(window.websockets);
		return;
	}
	const ws = window.websockets.find(ws => ws.playerName === playerName);	
	ws.playerId = playerId;
	console.log("ws id ", ws.playerName, ws.playerId);
	const socket = new WebSocket(
        `wss://${window.pidom}/ws/tournament/tournament/${playerId}/${playerName}/${window.selfId}/`
    );
	ws.socket = socket;
	socket.onopen = () => {
		console.log(`Connexion Tournament ${playerName} établie 😊`);	
	}
	socket.onclose = () => {
		console.log(`Connexion Tournament ${playerName} disconnected 😈`);
		alert(`Connexion Tournament ${playerName} disconnected 😈`);
		console.log(window.websockets);
		window.websockets = window.websockets.filter(ws => ws.socket !== socket);
		console.log(window.websockets);
	};	
	socket.onmessage = event =>
		{};// onTournamentMessage(event, window.tournamentSocket);	
} 

function sanitizeInput(input) {
	input.value = input.value.replace(/[^a-zA-Z0-9]/g, "");
}
  
function newPlayer(socket) {
  
	const playerName = document.getElementById("player-name").value;
	if (playerName.trim() === "")
	{
        messagePopUp('Oops!', 'https://dansylvain.github.io/pictures/travolta.webp', "Enter a name!", "Enter a name!", "", "")

		// alert("enter a name!");
		return;
	}
	if (window.websockets.length >= 8)
	{
        messagePopUp('Oops!', 'https://dansylvain.github.io/pictures/marioNo.webp', "You can't create more than three players!", "You can't create more than three players!", "", "")

		// alert("you can't create more than three players!");
		return;
	}
	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "newPlayer",
			playerName: playerName			
		}));
	window.websockets.push({playerName: playerName});
}
  
function newTournament(socket) {
  
	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "newTournament"			
		}));
}

// function enterLocalsPlayerOnTournament(socket, tournamentId) {
// 	// const scripts = Array.from(document.getElementsByTagName("script"));
//     // scripts.forEach(el => {console.log("SCRIPTNAME: ", el.src)});
// 	// if (scripts.some(script => script.className === "match-script")) {
// 	// 	console.log("DEJA SCRIPT");
// 	// 	return; // Ne pas exécuter fetch si un script "match-script" existe déjà
// 	// };
// 	console.log("ENTER LOCALS TOURNAMENT: ", tournamentId);
// 	if (socket.readyState === WebSocket.OPEN) 
// 		socket.send(JSON.stringify({
// 			type: "enterTournament",
// 			tournamentId: tournamentId			
// 		}));
// }

function enterTournament(socket, tournamentId) {
	const scripts = Array.from(document.getElementsByTagName("script"));
    scripts.forEach(el => {console.log("SCRIPTNAME: ", el.src)});
	if (scripts.some(script => script.className === "match-script")) {
		console.log("DEJA SCRIPT");
		return; // Ne pas exécuter fetch si un script "match-script" existe déjà
	};
	console.log("entertournement: ", socket, " ", tournamentId);
	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "enterTournament",
			tournamentId: tournamentId			
		}));
}

function closeTournamentSocket() {
	
	if (typeof stopMatch === 'function')
		stopMatch(window.selfMatchId);
    if (
		window.tournamentSocket && 
		window.tournamentSocket.readyState === WebSocket.OPEN
	)
	window.tournamentSocket.close();
	window.websockets.forEach(ws => ws.socket.close());    
}

function onTournamentMessage(event, socket) {

	console.log("Message reçu :", event.data);
	const data = JSON.parse(event.data);
	
	switch (data.type)
	{
		// case "selfAssign":
		// 	setSelfId(data.selfId);
		// 	break;
		
		case "tournamentResult":
			tournamentResult(data);
		break;
		case "newPlayerId":
			connectNewPlayer(data.playerId, data.playerName);
		break;
		case "playerList":
			console.log("case playerlist");
			window.playersList = data.players;
			updatePlayers(socket, data.players);

			updateTournamentsPlayers(window.tournamentList);
			updateMatchsPlayers(window.pack);
			break;
		case "tournamentList":
			console.log("case tournamentlist");
			updatePlayers(socket, window.playersList);
			window.tournamentList = data.tournaments; 
			updateTournaments(socket, data.tournaments);
			break;
		case "linkMatch":
			console.log("case linkmatch");
			linkMatch(data);			
			break;
		case "matchResult":
			console.log("case matchresult");
			matchResult(data);			
			break;
		case "matchsPlayersUpdate":
			console.log("case matchPlayersUpdate");
			updatePlayersCont(window.playersList)
			updateTournamentsPlayers(window.tournamentList);
			window.pack = data.pack;
			updateMatchsPlayers(data.pack);			
			break;
		// case "closeMatch":
		// 	console.log("case closematch");
		// 	if (window.matchSocket && window.matchSocket.readyState === WebSocket.OPEN)
		// 	{					
		// 		window.stopFlag = true
		// 		window.matchSocket.close(3666);
		// 	}
		// 	break;
		default:				
			break;
	}
}

// function setSelfId(selfId) {

// 	window.selfId = selfId;	
// 	document.getElementById("player").innerText = 
// 		"Je suis le joueur " + window.selfId;	
// }

function tournamentResult(data)
{
	console.log('%%%%%%%%%%%%%%%%% tournamentResult: &&&&&&&&&&&&&&&&&&&&&&&&&&');
	console.log(data);
	// if (window.selfMatchId === data.)
    messagePopUp('Yeah!', 'https://dansylvain.github.io/pictures/trumpDance.webp', " won the tournament!", " won the tournament!", data.winnerName, "")	// Le tournoi est terminé
	console.log("TOURNAMENT RESULT ", data);
}

function updatePlayers(socket, playersUp)
{
	console.log("UPDATE PLAYERS ", playersUp);

	updateWinPlayers(socket, playersUp);
	updatePlayersCont(playersUp);
}

function updateWinPlayers(socket, playersUp)
{
	console.log("UPDATE WIN PLAYERS ", playersUp);

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
	console.log("CREATE PL ELEMENT ", playerId);

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

// function phantomPlayer(div) {

// 	const playersCont = document.getElementById("players");
// 	div.classList.add("phantom");

// 	// dropTrash();
// 	// dropPlayersZone();
// 	// div.onclick =  event => {
// 	// 	event.stopPropagation();
// 	// 	const players = [...playersCont.children]
// 	// 	if (players.some(el => el.id == playerId))		
// 	// 		ws.socket.close();
// 	// 	else
// 	// 		quitTournament(ws.socket)	
// 	// }
// }

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
            messagePopUp('Oops!',
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
            messagePopUp('Oops!',
				'https://dansylvain.github.io/pictures/marioNo.webp',
				"Not your player!", "Not your player!", "", "");			
		}
		else if (window.selfId == elementId)	
		{
			messagePopUp('Oops!',
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

function dragPlayer(div) {

	div.draggable = true;
	div.addEventListener("dragstart",
		e => {
			e.dataTransfer.setData("text/plain", e.target.id);
			const clone = div.cloneNode(true);
			clone.id = "clone";
			clone.style.borderRadius = "12px";	
			const rect = div.getBoundingClientRect();
			clone.style.width = `${rect.width * 0.85}px`;
			clone.style.position = "absolute";
			clone.style.top = "-100";
			clone.style.left = "-100";
			document.body.appendChild(clone);		  
			const offsetX = clone.offsetWidth / 2;
			const offsetY = clone.offsetHeight / 2;
			e.dataTransfer.setDragImage(clone, offsetX, offsetY);		
		} );
}

// function allQuitTournament() 
// {
// 	console.log("ALL QUIT TOURNAMENT");
// 	window.websockets.forEach(ws => quitTournament(ws.socket));
// 	quitTournament(window.tournamentSocket);	
// }

function quitTournament(socket) {
	
	console.log("QUIT TOURNAMENT");

	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "quitTournament"						
		}));
}

function updatePlayersCont(playersUp) {

	console.log("UPDATE PLAYERS CONT ", playersUp);

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

	console.log("UPDATE TOURNAMENTS ", tournamentsUp);

	const tournamentsCont = document.getElementById("tournaments");
	const tournamentEls = [...tournamentsCont.children];
	const patternPromises = [];

	tournamentsUp.forEach(tourUp => {
		if (tournamentEls.every(el => el.id != tourUp.tournamentId))
			addToTournaments(socket, tournamentsCont, tourUp);
		if (tourUp.matchs.length > 0)			
			patternPromises.push(getPattern(tourUp.tournamentId));			
	});
	tournamentEls.slice().reverse().forEach(tourEl => {
		if (tournamentsUp.every(el => el.tournamentId != tourEl.id)) {
			if (tourEl.id == window.actualScriptTid)
			{
				const oldScripts = document.querySelectorAll("script.match-script");			
				oldScripts.forEach(oldScript => oldScript.remove());
			}
			tournamentsCont.removeChild(tourEl);		
		}
	});

	updateTournamentsPlayers(tournamentsUp);
	// updateLinkMatchAndResult(tournamentsUp);
	patternPromises.forEach(promise => promise.then(value =>{
		console.log("NEW PROMISE REC ", value);
		if (value)
		{
			// setTimeout(()=>{

				console.log("GO To UTP ULKR ", value);
				updateTournamentsPlayers(tournamentsUp);
				updateLinkMatchAndResult(tournamentsUp);
			// }, 2000);
		}
	}));
}

function addToTournaments(socket, tournamentsContainer, tournament) {

	console.log("ADD TO TOURNAMENT ", tournamentsContainer, " : ", tournament);

	const div = document.createElement("div");	
	div.className = "tournament";
	// div.textContent = `tournament: ${tournament.tournamentId}`;
	div.id = tournament.tournamentId;
	div.className = "tournament-cont"
	// div.onclick = () => enterTournament(socket, tournament.tournamentId);
	const overlayPattern = document.createElement("div");
	overlayPattern.id = "overlay-pattern";
	const playersCont = document.createElement("div");
	playersCont.id = "players-cont";
	// const close = createTournamentClose(div);
	// div.appendChild(close);
	div.appendChild(playersCont);
	div.appendChild(overlayPattern);
	dropTournament(div, tournament.tournamentId);
	tournamentsContainer.appendChild(div);	
}

// function createTournamentClose(tournament)
// {
// 	const div = document.createElement("div");
// 	div.innerText = "Close";
// 	div.onclick = ()=> {
// 		tournament.style.display = "none";
// 		allQuitTournament(tournamentId);
// 	}
// 	return div	
// }

function dropTournament(div, tournamentId) {

	div.addEventListener("dragover", e => e.preventDefault());
	div.addEventListener("drop", e => {	
		e.preventDefault();
		const elementId = e.dataTransfer.getData("text/plain");
		const ws = window.websockets.find(el => el.playerId == elementId);	
		if (!ws && window.selfId != elementId)
		{
            messagePopUp('Oops!',
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

// function dropMatch(lk, div, overlay) {

// 	div.addEventListener("dragover", e => e.preventDefault());
// 	div.addEventListener("drop", e => {
// 		console.log("dans drop");
// 		e.preventDefault();
// 		e.stopPropagation();
// 		const elementId = e.dataTransfer.getData("text/plain");

// 		const socket = window.websockets.find(el => el.playerId == elementId);	
// 		if (!socket)
// 		{
// 			alert("not your player MAN");
// 			return;
// 		}
// 		// enterTournament(socket.socket, tournamentId);
		
// 		enterMatch(lk, div, overlay, socket.playerId, socket.playerName)
// 	});
// }

function catchPlayersInMatch(lk)
{
	const wscopy = window.websockets.map( ws => ({...ws}))
	wscopy.push({playerId: window.selfId, playerName: window.selfName,
		socket:window.tournamentSocket});
	const p1 = wscopy.find(ws => ws.playerId == lk.p1Id);
	const p2 = wscopy.find(ws => ws.playerId == lk.p2Id);
	console.log("CATCH PLAYER ", p1, " and ", p2);
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

function getPattern(tournamentId) {

	console.log("GET PATTERN ", tournamentId);

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

function updateTournamentsPlayers(tournamentsUp) {

	if (!tournamentsUp)
		return;
	console.log("UPDATE TOURNAMENTS PLAYERS ", tournamentsUp);

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

function updateLinkMatchAndResult(tournamentsUp) {

	console.log("UPDATE LINK AND MATCH RESULT ", tournamentsUp);

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
	console.log("LINK MATCH ", lk);
	const patternPromises = [];
	const tournament = document.getElementById("tournaments").querySelector(
		`[id='${lk.tournamentId}']`
	);
	if (!tournament)
	{
		console.log("je sors de link match parceque tournament est faux");
		return;
	}
	const overlay = tournament.querySelector("#overlay-match");
	// setTimeout(()=>{

		const localMatch = tournament.querySelector(`#${lk.localMatchId}`);
		if (!localMatch)
		{
			patternPromises.push(getPattern(lk.tournamentId));	
			patternPromises.forEach(promise => promise.then(value =>{
				console.log("NEW PROMISE REC INSIDE LE DEDANS ", value);
				if (value)
				{
					setTimeout(()=>{
						const localMatch = tournament.querySelector(`#${lk.localMatchId}`);
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
					}, 2000);
				}
			}));
			console.log("je sors de link match parceque localMatch est faux");
			return;
		}
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

	// }, 2000);
	
	
	
}

function setNextMatch(lk, localMatch)
{
	const ws = window.websockets.find(ws =>
		ws.playerId == lk.p1Id ||
		ws.playerId == lk.p2Id
	);
	if (window.selfId == lk.p1Id || window.selfId == lk.p2Id || ws)
	{
		console.log("ADD NEXT MATCH selfid ", window.selfId, " p1id ", lk.p1Id, " p2id ", lk.p2Id, " ws ", ws);
		localMatch.classList.remove("spec-match");
		localMatch.classList.add("next-match");	
	}
	else
	{
		console.log("ADD SPEC MATCH selfid ", window.selfId, " p1id ", lk.p1Id, " p2id ", lk.p2Id, " ws ", ws);
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
	console.log("TOURNAMENT TO ENTER IN MATCH : ", playerId, " ",  playerName, " ", player2Id, " ", player2Name);
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
		const oldScripts = document.querySelectorAll("script.match-script");			
		oldScripts.forEach(oldScript => oldScript.remove());
		window.actualScriptTid = lk.tournamentId;
		loadTournamentHtml(data, overlay);
	})
	.catch(error => console.log(error))
}

function isYetInMatch()
{	
	const scripts = [...document.getElementsByTagName("script")];

	if (scripts.some(script => script.className === "match-script"))	
		return console.log("DEJA SCRIPT"), true;
	return false;	
}

function setTournamentSelfMatchId(lk)
{
	const ws = window.websockets.find(ws =>
		ws.playerId == lk.p1Id ||
		ws.playerId == lk.p2Id
	)
	if (window.selfId == lk.p1Id ||	window.selfId == lk.p2Id ||	ws)	
		window.selfMatchId = lk.matchId;
	else
		window.selfMatchId = null;
}

function loadTournamentHtml(data, overlay) {
	
	const oldScripts = document.querySelectorAll("script.match-script");			
	oldScripts.forEach(oldScript => oldScript.remove());	
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
	console.log("MATCH RESULT ", rsl);

	const tournament = document.getElementById("tournaments").querySelector(
		`[id='${rsl.tournamentId}']`
	);
	if (!tournament)
		return;
	const localMatch = tournament.querySelector(`#${rsl.localMatchId}`);
	if (!localMatch)
		return;
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
	localMatch.onclick = "";
}

function updateMatchsPlayers(pack) {

	if (pack)
		pack.forEach(plys => updateMatchPlayers(plys));
}

function updateMatchPlayers(plys)
{
	console.log("MATCH PLAYERS UPDATE ", plys);	

	const tournament = document.getElementById("tournaments").querySelector(
		`[id='${plys.tournamentId}']`
	);
	if (!tournament)
		return;
	console.log("MATCH PLAYERS UPDATE TOURNMANTEE", tournament);	
	const localMatch = tournament.querySelector(`#${plys.localMatchId}`);
	if (!localMatch)
		return;
	console.log("MATCH PLAYERS UPDATE localmatch", localMatch);	
	const localP1 = localMatch.querySelector(`#pl1`);
	const localP2 = localMatch.querySelector(`#pl2`);
	const specCont = localMatch.querySelector(`#specs`);
	console.log("localp1", localP1);	
	console.log("localp2", localP2);	
	console.log("sepccont", specCont);
	const specs = [...specCont.children]

	plys.players.forEach(player => {
		console.log("foreachplayer ", player);	
		if (specs.every(el => el.id != player.playerId))
		{
			console.log("every ", player);	
			const winPly = window.players.find(el => el.id == player.playerId);
			console.log("winply ", winPly);	
			console.log("winply id ", winPly.id);	
			console.log("plys.p1Id ", plys.p1Id);	
			console.log("plys.p2Id ", plys.p2Id);	
			if (plys.p1Id == winPly.id)
			{
				console.log("plys.p1Id == winPly.id ");	
				localP1.appendChild(winPly);
			}
			else if (plys.p2Id == winPly.id)
			{
				console.log("plys.p2Id == winPly.id ");	
				localP2.appendChild(winPly);
			}
			else
			{
				console.log("else ");	
				specCont.appendChild(winPly);
			}
		}
	});
}
