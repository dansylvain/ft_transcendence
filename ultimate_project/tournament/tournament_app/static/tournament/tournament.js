
window.players = []
websockets = []

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
        `wss://${window.pidom}/ws/tournament/tournament/${window.selfId}/${window.selfName}/`
    );
	window.tournamentSocket.onopen = () => {
		console.log("Connexion Tournament établie 😊");	
	}
	window.tournamentSocket.onclose = () => {
		console.log("Connexion Tournament disconnected 😈");
	};	
	window.tournamentSocket.onmessage = event =>
		onTournamentMessage(event, window.tournamentSocket);
}

function connectNewPlayer(playerId, playerName)
{
	console.log("CONNECT NEW PLAYER ", playerId, " ", playerName);

	if (!playerId)
	{
		alert("player name yet exist!");
		console.log(websockets);
		websockets = websockets.filter(ws => ws.playerId !== undefined);	
		console.log(websockets);
		return;
	}
	const ws = websockets.find(ws => ws.playerName === playerName);	
	ws.playerId = playerId;
	console.log("ws id ", ws.playerName, ws.playerId);
	const socket = new WebSocket(
        `wss://${window.pidom}/ws/tournament/tournament/${playerId}/${playerName}/`
    );
	ws.socket = socket;
	socket.onopen = () => {
		console.log(`Connexion Tournament ${playerName} établie 😊`);	
	}
	socket.onclose = () => {
		console.log(`Connexion Tournament ${playerName} disconnected 😈`);
		console.log(websockets);
		websockets = websockets.filter(ws => ws.socket !== socket);
		console.log(websockets);
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
		alert("enter a name!");
		return;
	}
	if (websockets.length >= 3)
	{
		alert("you can't create more than three players!");
		return;
	}
	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({
			type: "newPlayer",
			playerName: playerName			
		}));
	websockets.push({playerName: playerName});
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
	websockets.forEach(ws => ws.socket.close());    
}

function onTournamentMessage(event, socket) {

	console.log("Message reçu :", event.data);
	const data = JSON.parse(event.data);
	
	switch (data.type)
	{
		// case "selfAssign":
		// 	setSelfId(data.selfId);
		// 	break;
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
	const ws = websockets.find(ws => ws.playerId == playerId);	
	if (playerId == window.selfId)
	{
		div.classList.add("self-player");
		div.onclick = event => {
			event.stopPropagation();
			quitTournament(socket);	
		}		
	}
	else if (ws)
		phantomPlayer(div, playerId, ws);
	dragPlayer(div);
	return div;
}

function phantomPlayer(div, playerId, ws) {

	const playersCont = document.getElementById("players");
	div.classList.add("phantom");
	div.onclick =  event => {
		event.stopPropagation();
		const players = [...playersCont.children]
		if (players.some(el => el.id == playerId))		
			ws.socket.close();
		else
			quitTournament(ws.socket)	
	}
}

function dragPlayer(div) {

	div.draggable = true;
	div.addEventListener("dragstart",
		e => {console.log("dans drag"); e.dataTransfer.setData("text/plain", e.target.id);});
}

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
			console.log("GO To UTP ULKR ", value);
			updateTournamentsPlayers(tournamentsUp);
			updateLinkMatchAndResult(tournamentsUp);
		}
	}));
}

function addToTournaments(socket, tournamentsContainer, tournament) {

	console.log("ADD TO TOURNAMENT ", tournamentsContainer, " : ", tournament);

	const div = document.createElement("div");	
	div.className = "tournament";
	div.textContent = `tournament: ${tournament.tournamentId}`;
	div.id = tournament.tournamentId;
	div.className = "tournament-cont"
	// div.onclick = () => enterTournament(socket, tournament.tournamentId);
	const overlayPattern = document.createElement("div");
	overlayPattern.id = "overlay-pattern";
	const playersCont = document.createElement("div");
	playersCont.id = "players-cont";
	div.appendChild(playersCont);
	div.appendChild(overlayPattern);
	dropTournament(div, tournament.tournamentId);
	tournamentsContainer.appendChild(div);	
}

function dropTournament(div, tournamentId) {

	div.addEventListener("dragover", e => e.preventDefault());
	div.addEventListener("drop", e => {
		console.log("dans drop");
		e.preventDefault();
		const elementId = e.dataTransfer.getData("text/plain");
		const ws = websockets.find(el => el.playerId == elementId);	
		if (!ws && window.selfId != elementId)
		{
			alert("not your player");
			return;
		}
		if (ws)
			enterTournament(ws.socket, tournamentId);
		else
			enterTournament(window.tournamentSocket, tournamentId);
	});
}

// function dropMatch(lk, div, overlay) {

// 	div.addEventListener("dragover", e => e.preventDefault());
// 	div.addEventListener("drop", e => {
// 		console.log("dans drop");
// 		e.preventDefault();
// 		e.stopPropagation();
// 		const elementId = e.dataTransfer.getData("text/plain");

// 		const socket = websockets.find(el => el.playerId == elementId);	
// 		if (!socket)
// 		{
// 			alert("not your player MAN");
// 			return;
// 		}
// 		// enterTournament(socket.socket, tournamentId);
		
// 		enterMatch(lk, div, overlay, socket.playerId, socket.playerName)
// 	});
// }

function catchPlayersInMatch(lk, playerId, playerName)
{
	const wss = websockets.filter(
		ws => ws.playerId == lk.p1Id || ws.playerId == lk.p2Id);
	if (window.selfId == lk.p1Id || window.selfId == lk.p2Id)
		wss.push({playerId: window.selfId, playerName: window.selfName,
			socket:window.tournamentSocket});
	let player2Id = 0;
	let player2Name = "";
	let socket = window.tournamentSocket;
	console.log("CATCH", socket, " ", window.tournamentSocket);
	if (wss.length >= 1)
	{
		playerId = wss[0].playerId;
		playerName = wss[0].playerName;
		socket = wss[0].socket;
	}
	if (wss.length == 2)
	{
		player2Id = wss[1].playerId;
		player2Name = wss[1].playerName;
	}
	enterTournament(socket, lk.tournamentId);
	if (player2Id)
		enterTournament(wss[1].socket, lk.tournamentId);
	return [playerId, playerName, player2Id, player2Name];
}

// function enterMatch(lk, div, overlay, playerId, playerName) {
// 	const scripts = Array.from(document.getElementsByTagName("script"));
// 	scripts.forEach(el => {console.log("SCRIPTNAME: ", el.src)});
// 	if (scripts.some(script => script.className === "match-script")) {
// 		console.log("DEJA SCRIPT");
// 		return; // Ne pas exécuter fetch si un script "match-script" existe déjà
// 	};
// 	if (window.selfId == lk.p1Id || window.selfId == lk.p2Id)
// 	{
// 		window.selfMatchId = lk.matchId;
// 		// localMatch.classList.add("next-match");
// 	}
// 	const [playerIdLLL, playerNameLLL, player2Id, player2Name] = catchPlayersInMatch(
// 		lk, playerId, PlayerName)

// 	fetch(
// 		`/match/match${dim.value}d/` +
// 		`?matchId=${lk.matchId}` +
// 		`&playerId=${playerId}&playerName=${playerName}` +
// 		`&player2Id=${player2Id}&player2Name=${player2Name}`
// 	)
// 	.then(response => {
// 		if (!response.ok) 
// 			throw new Error(`Error HTTP! Status: ${response.status}`);		  
// 		return response.text();
// 	})
// 	.then(data => {
// 		const oldScripts = document.querySelectorAll("script.match-script");			
// 		oldScripts.forEach(oldScript => oldScript.remove());
// 		window.actualScriptTid = lk.tournamentId;//?
// 		loadTournamentHtml(data, overlay);	
// 	})
// 	.catch(error => console.log(error))
// };

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

function updateTournamentsPlayers(tournamentsUp)
{
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

	const dim = document.getElementById("dim");
	const tournament = document.getElementById("tournaments").querySelector(
		`[id='${lk.tournamentId}']`
	);
	if (!tournament)
	{
		console.log("je sors de link match parceque tournament est faux");
		return;
	}
	const overlay = tournament.querySelector("#overlay-match");
	const localMatch = tournament.querySelector(`#${lk.localMatchId}`);
	if (!localMatch)
	{
		console.log("je sors de link match parceque localMatch est faux");
		return;
	}
	overlay.style = "transform:translate(-180px, 200px);"
	const localP1 = localMatch.querySelector(`#pl1`);
	const localP2 = localMatch.querySelector(`#pl2`);
	if (localP1.innerText.trim() !== "p1" && localP1.innerText.trim() !== "p2")
	{
		console.log("je sors de link match parceque p1 ou p2 ne sont pas vide");
		return;
	}
	localP1.innerText = lk.p1Name;
	localP2.innerText = lk.p2Name;
	// if (window.selfId == lk.p1Id || window.selfId == lk.p2Id)
	const ws = websockets.find(ws => ws.playerId == lk.p1Id || ws.playerId == lk.p2Id)
	console.log("WAIBECHAUSETTE ", ws);
	if (window.selfId == lk.p1Id || window.selfId == lk.p2Id || ws)
	{
		window.selfMatchId = lk.matchId;
		localMatch.classList.add("next-match");
	}
	else
		localMatch.classList.add("spec-match");

	localMatch.onclick = function() {
		const scripts = Array.from(document.getElementsByTagName("script"));
		scripts.forEach(el => {console.log("SCRIPTNAME: ", el.src)});
		if (scripts.some(script => script.className === "match-script")) {
			console.log("DEJA SCRIPT");
			return; // Ne pas exécuter fetch si un script "match-script" existe déjà
		};
		const ws = websockets.find(ws => ws.playerId == lk.p1Id || ws.playerId == lk.p2Id)
		console.log("WAIBECHAUSETTE ", ws);
		if (window.selfId == lk.p1Id || window.selfId == lk.p2Id || ws)
		{
			window.selfMatchId = lk.matchId;
			// localMatch.classList.add("next-match");
		}
		const [playerId, playerName, player2Id, player2Name] = catchPlayersInMatch(
			lk, window.selfId, window.selfName)
		fetch(
			`/match/match${dim.value}d/` +
			`?matchId=${lk.matchId}` +
			`&playerId=${playerId}&playerName=${playerName}` +
			`&player2Id=${player2Id}&player2Name=${player2Name}`
		)		
		// fetch(
		// 	`/match/match${dim.value}d/` +
		// 	`?matchId=${lk.matchId}&playerId=${window.selfId}&playerName=${window.selfName}`)
		.then(response => {
			if (!response.ok) 
				throw new Error(`Error HTTP! Status: ${response.status}`);		  
			return response.text();
		})
		.then(data => {
			const oldScripts = document.querySelectorAll("script.match-script");			
			oldScripts.forEach(oldScript => oldScript.remove());
			window.actualScriptTid = lk.tournamentId;
			loadTournamentHtml(data, overlay);
		})
		.catch(error => console.log(error))
	};
	// dropMatch(lk, localMatch, overlay)
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
	if (rsl.winnerId === rsl.p1Id)
	{
		localP1.classList.add("winner");
		localP2.classList.add("looser");
	}
	else if (rsl.winnerId === rsl.p2Id)
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

// function updatePlayers2(socket, players) {
// 	console.log("UPDATE PLAYER");
//     const playersContainer = document.getElementById("players");
// 	let playerElements = [...playersContainer.children];	
	
// 	const tournamentsContainer = document.getElementById("tournaments");
// 	let tournamentElements = [...tournamentsContainer.children];

// 	tournamentElements.slice().reverse().forEach(tournament => {
// 		const playersCont = tournament.querySelector("#players-cont");
// 		[...playersCont.children].slice().reverse().forEach(player =>{
// 			if (players.every(el => el.playerId != player.id))
// 			{
// 				window.players = window.players.filter(el => {
// 					if (el.id === player.id)				
// 						return el.remove(), false
// 					else
// 						return true;				
// 				});			
// 			}
// 		});
// 	});
// 		// findPlayer = searchPlayerInTournaments(player.playerId);
// 		// console.log("find player: ", findPlayer);
// 		// if (findPlayer)
// 		// 	findPlayer.remove();
	
// 	playerElements = [...playersContainer.children];	
// 	playerElements.slice().reverse().forEach(player => {	
// 		if (players.every(el => el.playerId != player.id))	
// 		{
// 			window.players = window.players.filter(el => {
// 				if (el.id === player.id)				
// 					return el.remove(), false
// 				else
// 					return true;				
// 			});
// 			// playersContainer.removeChild(player);									
// 		}	
// 	});
// 	playerElements = [...playersContainer.children];
// 	players.forEach(player => {	
// 		if (playerElements.every(el => el.id != player.playerId) &&
// 			!searchPlayerInTournaments(player.playerId)
// 		)		
// 			addPlayerToContainer(socket, playersContainer, player.playerId);		
// 	});	
// }

// function searchPlayerInTournaments(playerId) {

// 	const tournamentsContainer = document.getElementById("tournaments");
// 	let tournamentElements = [...tournamentsContainer.children];

// 	for (const tournament of tournamentElements) { 
// 		const playersCont = tournament.querySelector("#players-cont");       
//         for (const player of [...playersCont.children]) {
//             if (player.id == playerId) {
//                 return player; 
//             }
//         }
//     }
// 	return null
// }

// function addPlayerToContainer(socket, container, playerId) {

// 	const div = document.createElement("div");
// 	div.className = "user";
// 	div.textContent = `user: ${playerId}`;
// 	div.id = playerId;	
// 	if (playerId === window.selfId)
// 	{
// 		div.classList.add("self-player");
// 		div.onclick = event => {
// 			event.stopPropagation();
// 			quitTournament(socket);
// 			// tournamentId = Number(event.currentTarget.parentElement.id)
// 		}		
// 	}
// 	// else	
// 	// 	div.onclick = event =>	sendPlayerClick(socket, event, div);	
//     container.appendChild(div);
// 	window.players.push(div);
// }



// function updateTournaments2(socket, tournamentListUpdate) {
// 	console.log("UPDATE TOURNAMENT");
//     const tournamentsContainer = document.getElementById("tournaments");
// 	let tournamentElements = [...tournamentsContainer.children];
		
// 	removeTournaments(
// 		socket, tournamentListUpdate, tournamentsContainer, tournamentElements);

// 	tournamentListUpdate.forEach(tourUp => {

// 		if (tournamentElements.every(el => el.id != tourUp.tournamentId))		
// 			addToTournaments(socket, tournamentsContainer, tourUp);

// 		// tournamentElements = [...tournamentsContainer.children];		
// 		// tournamentElements.forEach(tourEl => {
// 		// 	if (tourEl.id == tourUp.tournamentId)
// 		// 	{
// 		// 		const playersCont = tourEl.querySelector("#players-cont");			
// 				movePlayersInTournaments(tournamentsContainer, tourUp);
// 		// 	}
// 		// });
		
// 		if (tourUp.matchs.length > 0)
// 		{
// 			getPattern(tourUp.tournamentId);
// 			setTimeout(()=>{
// 				tourUp.matchs.forEach(match => {
// 					if (match.linkMatch)
// 					{
// 						console.log("MATCHSSS ", match)				
// 						lk = match.linkMatch;
// 						linkMatch(lk.tournamentId, lk.localMatchId, lk.matchId, lk.p1Id, lk.p2Id);
// 					}
// 					if (match.matchResult)
// 					{
// 						console.log("match Reuslt EXISTE mouquate");
// 						// mres = match.matchResult;
// 						matchResult(match.matchResult);			
		
// 					}
// 					else {
// 						console.log("match Reuslt nexiste pas mouquate");
// 					}
// 				});
// 			}, 3000);		
// 		}	
// 	});
// 	// setSelfMatchId();	
// }

// function removeTournaments(socket, tournaments, tournamentsContainer, tournamentElements) {

// 	// const playersContainer = document.getElementById("players");

// 	tournamentElements.slice().reverse().forEach(tournament => {
// 		if (tournaments.every(el => el.tournamentId != tournament.id)) {
// 			// if (match.id == window.selfMatchId)
// 			// {
// 			// 	if (window.busyElement)
// 			// 		window.busyElement.classList.remove("invitation-waiting");
// 			// 	window.busyElement = null;
// 			// 	window.selectedElement.classList.remove("invitation-confirmed");
// 			// 	window.selectedElement = null;
// 			// 	window.selfMatchId = null;
// 			// }
// 			// [...match.children].forEach(player => {
// 			// 	playersContainer.appendChild(player);
// 			// });
// 			tournamentsContainer.removeChild(tournament);		
// 		}
// 	});
// }



// function movePlayersInTournaments(tournamentsContainer, tourUp) {
// 	tournamentElements = [...tournamentsContainer.children];		
// 	tournamentElements.forEach(tourEl => {
// 		if (tourEl.id == tourUp.tournamentId)
// 		{
// 			const playersCont = tourEl.querySelector("#players-cont");			
// 			const playerElements = [...playersCont.children];
// 			tourUp.players.forEach(plyUp => {
// 				if (playerElements.every(el => el.id != plyUp.playerId))
// 				{
// 					const winPly = window.players.find(el => el.id == plyUp.playerId);
// 					if (winPly)
// 						playersCont.appendChild(winPly);
// 				}
// 			});	
// 		}
// 	});

// }

// function movePlayerInTournament2(tournamentElement, tournament) {
	
// 	const playersContainer = document.getElementById("players");
// 	const playerElements = [...playersContainer.children];
// 	const tournamentPlayerElements = [...tournamentElement.children];
// 	const tournamentsContainer = document.getElementById("tournaments");
// 	const tournamentElements = [...tournamentsContainer.children];

// 	if (tournament.players)
// 	{
// 		playerElements.slice().reverse().forEach(player => { // je met le joueur ds le bon tournois depuis cont player si ny est pas deja 
// 			if (tournament.players.some(p => p.playerId == player.id) &&
// 				tournamentPlayerElements.every(p => p.id != player.id))
// 			{
// 				console.log("appendchild to tournois; id:", player.id," ", tournamentElement.id);
// 				tournamentElement.appendChild(player);
// 			}			
// 			else
// 			{
				
// 				tournamentElements.slice().reverse().forEach(tourn => {
// 					const playersCont = tourn.querySelector("#players-cont");
// 					console.log("type: ", typeof(tourn));
// 					[...playersCont.children].slice().reverse().forEach(player2 =>{

// 						if (tournament.players.some(p => p.playerId == player2.id) &&
// 						tournamentPlayerElements.every(p => p.id != player2.id))			
// 						{
// 							console.log("appendchild to tournois; id:", player2.id," ", tournamentElement.id);
// 							tournamentElement.appendChild(player2);
// 						}
// 					});									
// 				});
// 			}						
// 		});
// 		if (playerElements.length === 0)
// 		{
// 			console.log("player est faux");
// 			tournamentElements.slice().reverse().forEach(tourn => {
// 				console.log("type: ", typeof(tourn));
// 				const playersCont = tourn.querySelector("#players-cont");
// 				[...playersCont.children].slice().reverse().forEach(player2 =>{
					
// 					if (tournament.players.some(p => p.playerId == player2.id) &&
// 					tournamentPlayerElements.every(p => p.id != player2.id))			
// 				{
// 					console.log("appendchild to tournois; id:", player2.id," ", tournamentElement.id);
// 					tournamentElement.appendChild(player2);
// 				}
// 			});									
// 		});
// 		}


// 		tournamentPlayerElements.slice().reverse().forEach(player => { // je met le joueur du tournois ds cont player 
// 			if (tournament.players.every(el => el.playerId != player.id))// && player.id != "overlay-pattern"))
// 			{
// 				console.log("appendchild to cont player; id:", player.id, " ", tournamentElement.id);
// 				playersContainer.appendChild(player);	// ou alors le bon tournois!				
// 			}			
// 		});
// 	}
// 	else // si le tournois est vide
// 	{
// 		tournamentPlayerElements.slice().reverse().forEach(player => {	// je met tous les joueur du tournois ds cont player 					
// 			// if (player.id != "overlay-pattern")
// 			// {
// 				console.log("appendchild to cont player from void; id:", player.id, " ", tournamentElement.id);
// 				playersContainer.appendChild(player);	// ou alors le bon tournois!				
// 			// }
// 				// ou alors le bon tournois!				
// 		});
// 	}
// }



