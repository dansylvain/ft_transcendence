
function sendInvitation(socket, choosenId) {
	
	console.log("i will send invitation to choosenId: " + choosenId);

	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({type: "invitation", choosenId: choosenId}))
}

function sendConfirmation(socket, applicantId) {

	console.log("i will send confirmation to applicant: " + applicantId);

	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({type: "confirmation", response: "yes", applicantId: applicantId}))
}

function sendMatchId(socket, matchId, choosenId) {

	console.log("i will send matchId: " + matchId + " to choosen: " + choosenId);

	if (socket.readyState === WebSocket.OPEN) 
		socket.send(JSON.stringify({matchId: matchId, choosenId: choosenId}))
}

function updateUsersList(socket, players) {

    const usersContainer = document.getElementById("users");
    usersContainer.innerHTML = "";

    players.forEach(user => {

    	const div = document.createElement("div");
    	div.className = "user";
    	div.textContent = `user: ${user.playerId}`;
		
		if (user.playerId === window.selfId)
		{
			div.style.backgroundColor = 'violet'
			div.onclick = function() {
				alert("you can't choose yourself");
			};
		}
		else
		{
    		div.onclick = function() {
				console.log(`my choice: ${user.playerId}`);
				window.select = user.playerId;
				this.style.backgroundColor = 'red';
				sendInvitation(socket, window.select);
    		};
		}
    	usersContainer.appendChild(div);
    });
	// elements = document.getElementsByClassName("user");

	// Array.from(elements).forEach( element => {

	// 	element.addEventListener("click", event => {
	// 		console.log("ye" + window.select);
	// 		console.log(`choice: {{user.playerId}}`); window.select ='{{ user.playerId }}';
	// 		this.style.backgroundColor = 'red';
	// 		sendInvitation(socket, window.select);
	// 	});
	// });
}

function setSelfId(selfId) {
	window.selfId = selfId;
	document.getElementById("player").innerText = 
	"Je suis le joueur " + window.selfId;
	
  	window.select = null;


}

function receiveInvitation(socket, host) {

	console.log("i have had and invitation from: " + host)

	sendConfirmation(socket, host);
}

function askMatchId(choosenId) {

	document.body.addEventListener("htmx:configRequest", function(evt) {

		if (evt.detail.elt.id === "startMatchButton" && window.select !== null){
			evt.detail.path = "/tournament/start-match/?selfid=" + window.selfId + "&select=" + choosenId;
		}
	});
}

function receiveConfirmation(choosenId, response) {

	console.log("i have had and confirmation from: " + choosenId
		+ ", the answer is :" + response);

	askMatchId(choosenId);
}

function receiveMatchId(matchId) {
	console.log("i have had and matchId: " + matchId)
	document.body.addEventListener("htmx:configRequest", function(evt) {
		if (evt.detail.elt.id === "startMatchButton"){
			evt.detail.path = `/tournament/start-match/?matchId=${matchId}`;
		}
	});
}

function initTournamentWs() {

	if (window.rasp == "true")
		window.tournamentSocket = new WebSocket(`wss://${window.pidom}/ws/match/${window.matchId}/`);//!
	else
		window.tournamentSocket = new WebSocket(`ws://localhost:8000/ws/tournament/`);

	window.tournamentSocket.onopen = () => {
		console.log("Connexion Tournament établie 😊");	
	}
	window.tournamentSocket.onclose = () => {
		console.log("Connexion Tournament disconnected 😈");	
	};
	
	window.tournamentSocket.onmessage = (event) => {

		console.log("Message reçu :", event.data);
		const data = JSON.parse(event.data);
		
		if (data.type == "selfAssign")			
			setSelfId(data.selfId);		
		else if (data.type == "playerList")
			updateUsersList(window.tournamentSocket, data.players);
		else if (data.type == "invitation")		
			receiveInvitation(window.tournamentSocket, data.player);		
		else if (data.type == "confirmation")		
			receiveConfirmation(data.choosen, data.response);		
		else if (data.matchId)		
			receiveMatchId(data.matchId);
	};	
}

