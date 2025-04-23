
window.targetBall = window.targetBall || [0, 0];
window.targetPads = window.targetPads || [0, 0];

function quitMatch()
{
	document.body.classList.remove("match-active");
	window.gameStartTimestamp = undefined; 	
	removeKeyBoardEvent();
	cancelMatchAnimations();
	manualCloseMatchWss();
	delMatchScript();
	delMatch();
}
window.quitMatch = quitMatch;

function manualCloseMatchWss()
{
	window.stopFlag = true;
	const closeMatchWs = (socket)=> {
		if (socket && socket.readyState === WebSocket.OPEN)			
			socket.close(3666);		
	};
	closeMatchWs(window.matchSocket);
	closeMatchWs(window.matchSocket2);
}

function delMatchScript()
{
	const scripts = document.querySelectorAll("script.match-script");		
	scripts.forEach(oldScript => oldScript.remove());	
}

function delMatch()
{
	document.getElementById('match')?.remove();  
	document.getElementById('rules-overlay')?.remove();    	 
}

function displayGiveUp(visible)
{
	const giveUp = document.getElementById("quit-match-button");

	if (giveUp)
	{
		if (visible)
			giveUp.style.display = "block";
		else
			giveUp.style.display = "none";	
	}	
}

function cancelMatchAnimations()
{
	if (typeof pongUpdate?.pongAnim === "number")
		cancelAnimationFrame(pongUpdate.pongAnim);
	if (typeof addKeyBoardEvent?.keyBoardAnim === "number")
		cancelAnimationFrame(addKeyBoardEvent.keyBoardAnim);
	if (typeof startCountdown?.countAnim === "number")
		cancelAnimationFrame(startCountdown.countAnim);
}

function stopMatch(matchId)
{	
	removeKeyBoardEvent();
	cancelMatchAnimations();
	displayGiveUp(false);		
	window.gameStartTimestamp = undefined; 	
	if (window.selfMatchId == matchId)
		sendStopMatch(matchId);	
	setTimeout(manualCloseMatchWss, 1000);		
}
window.stopMatch = stopMatch;

function sendStopMatch(matchId)
{
	fetch(`/match/stop-match/${window.playerId}/${matchId}/`)
		.then(response => {
			if (!response.ok) 
				throw new Error(`Error HTTP! Status: ${response.status}`);		  
			return response.text();
		})
		.then(()=> window.selfMatchId = null)
		.catch(error => console.log(error))
}

function removeKeyBoardEvent()
{
	if (typeof addKeyBoardEvent?.keyDown === "function") 
		document.removeEventListener("keydown", addKeyBoardEvent.keyDown);
	if (typeof addKeyBoardEvent?.keyUp === "function") 
		document.removeEventListener("keyup", addKeyBoardEvent.keyUp);
}

function addKeyBoardEvent()
{
	addKeyBoardEvent.keysPressed = {};   
	addKeyBoardEvent.keyBoardAnim = null;
	addKeyBoardEvent.keyDown = (e)=> {
		e.preventDefault();
        if (!addKeyBoardEvent.keysPressed[e.key])
            addKeyBoardEvent.keysPressed[e.key] = true;  
        if (!addKeyBoardEvent.keyBoardAnim)
            addKeyBoardEvent.keyBoardAnim = requestAnimationFrame(sendCommands);        
	};
	addKeyBoardEvent.keyUp = (e)=> {
		e.preventDefault();
        delete addKeyBoardEvent.keysPressed[e.key];
        if (Object.keys(addKeyBoardEvent.keysPressed).length === 0)
		{
            cancelAnimationFrame(addKeyBoardEvent.keyBoardAnim);
            addKeyBoardEvent.keyBoardAnim = null;
        }
    };
	document.addEventListener("keydown", addKeyBoardEvent.keyDown);
	document.addEventListener("keyup", addKeyBoardEvent.keyUp);
}

function sendCommands()
{
	const socket = window.matchSocket;
	const socket2 = window.matchSocket2; 

	if (socket.readyState === WebSocket.OPEN)
	{
		if (addKeyBoardEvent.keysPressed["ArrowUp"]) 				
			socket.send(JSON.stringify({action: 'move', dir: 'up'}));
		
		if (addKeyBoardEvent.keysPressed["ArrowDown"]) 				
			socket.send(JSON.stringify({action: 'move', dir: 'down'}));            
	}
	if (socket2 && socket2.readyState === WebSocket.OPEN)
	{
		if (addKeyBoardEvent.keysPressed["+"]) 
			socket2.send(JSON.stringify({action: 'move', dir: 'up'}));            
		if (addKeyBoardEvent.keysPressed["Enter"]) 
			socket2.send(JSON.stringify({action: 'move', dir: 'down'}));            
	}
	addKeyBoardEvent.keyBoardAnim = requestAnimationFrame(sendCommands); 
}

function startCountdown(delay)
{
	const loaderElement = document.querySelector(".loader");
	if (loaderElement)
		loaderElement.style.opacity = "1";

    const countdownEl = document.querySelector('.countdown');
    const countdownEndsAt = window.gameStartTimestamp * 1000 + delay * 1000;

	function updateCountdown() {
        const now = Date.now();
        const remaining = Math.ceil((countdownEndsAt - now) / 1000);

        if (remaining > 0) {
            countdownEl.textContent = remaining;
            startCountdown.countAnim = requestAnimationFrame(updateCountdown);
        } else if (remaining > -1) {
            countdownEl.textContent = "GO!";
			startCountdown.countAnim = requestAnimationFrame(updateCountdown);
        } else {
            loaderElement.style.opacity = "0";
            window.gameStartTimestamp = undefined;
        }
    }
	updateCountdown();
}

function displayPlayersInfos(data, score)
{
	if (!data.names)
		return;
	score.innerText = data.score[0] + " | " + data.score[1];	
	const left = document.getElementById("inst-left");
	const rght = document.getElementById("inst-right");
	if (window.selfMatchId != window.matchId)	
		assignInfos(left, rght, data.names[0], data.names[1]);				
	else if (window.player2Id != 0)	
		assignInfos(left, rght, data.names[0] + "<br> keys: ↑ / ↓",
			data.names[1] + "<br> keys: enter / +");		
	else if (data.plyIds)
	{
		if (window.playerId == data.plyIds[0])		
			assignInfos(left, rght, data.names[0] + "<br> keys: ↑ / ↓",
				data.names[1]);
		else		
			assignInfos(left, rght, data.names[0],
				data.names[1] + "<br> keys: ↑ / ↓");	
	}	
}

function assignInfos(left, rght, leftInfo, rghtInfo)
{
	left.innerHTML = leftInfo;
	rght.innerHTML = rghtInfo;
}

tog = true;
function movePads(data, pads, match)
{
	const matchRect = match.getBoundingClientRect();
	 
	if (!data.ball)
		return;
	if (tog)
	{
		tog = true;
		pads.p1.style.display = "block";
		pads.p2.style.display = "block";
		pads.ball.style.display = "block";
	}
	pads.ball.style.top = -(matchRect.width / 100);
	pads.ball.style.width = (matchRect.width / 100) * 2;
	pads.ball.style.height = (matchRect.height / 100) * 2;		       
	window.targetPads[0] = data.yp1 * (matchRect.height / 100);
	window.targetPads[1] = data.yp2 * (matchRect.height / 100);
	window.targetBall[0] = data.ball[0] * (matchRect.width / 100);
	window.targetBall[1] = data.ball[1] * (matchRect.height / 100);	
}

function onMatchWsMessage(event, pads, elements, waitingState)
{	
	const data = JSON.parse(event.data);

	startDelay(data);
	displayPlayersInfos(data, elements.score);	
	setEnd(data, elements.endCont, elements.end, elements.spec);
	setWaiting(data, elements.waiting, waitingState);
	movePads(data, pads, elements.match);
}

function startDelay(data)
{
	if (data.timestamp && !data.state)
	{
		if (window.gameStartTimestamp === undefined)
		{
			window.gameStartTimestamp = data.timestamp;           
            startCountdown(data.delay);
		}				
		return;
	}
}

function setEnd(data, endCont, end, spec)
{
	if (data.state == "end")
	{	
        let url;
        if (window.selfName == data.winnerName)
            url = "https://dansylvain.github.io/pictures/sdurif.webp";
		else if (spec.style.display != "none")
		{
			url = "https://dansylvain.github.io/pictures/tennis.webp";
			spec.style.display = "none";
		}
		else 
			url = "https://dansylvain.github.io/pictures/MacronExplosion.webp";
		end.innerHTML = `The winner is: ${data.winnerName} <br> 
		Score: ${data.score[0]} : ${data.score[1]} <br> 
		<img src="${url}" 
		alt="Winner GIF" 
		class="winner-gif">
		`;		
		endCont.classList.add("end-cont");
		endCont.style.display = "block";
		window.gameStartTimestamp = undefined;	
	}
}

function setWaiting(data, waiting, waitingState)
{
	if (waitingState[0] != data.state) 
	{
		waitingState[0] = data.state;	
		if (waiting) 
		{
			if (data.state == "waiting")			
				waiting.classList.remove("no-waiting");
			else			
				waiting.classList.add("no-waiting");			
		}			
	}
}

function setSpec(spec)
{	
	if (!spec)
		return;	
	if (window.selfMatchId != window.matchId)
	{
		spec.style.display = "block";
		displayGiveUp(false);			
	}
	else
	{
		spec.style.display = "none";
		displayGiveUp(true);		
	}	
}

function pongUpdate(pads)
{
	pads.ball.style.transform =
		`translate(${window.targetBall[0]}px, ${window.targetBall[1]}px)`;		
	pads.p1.style.transform = `translateY(${window.targetPads[0]}px)`;
	pads.p2.style.transform = `translateY(${window.targetPads[1]}px)`;
	pongUpdate.pongAnim = requestAnimationFrame(()=> pongUpdate(pads));
}

function initSecPlayer()
{
	if (window.player2Id != 0)	
		window.matchSocket2 = createWebSocket(window.player2Id);	
}

function initDomain()
{
	if (
		window.location.hostname === "localhost" ||
		window.location.hostname === "127.0.0.1"
	)
        window.pidom = "localhost:8443";
	else
		window.pidom = window.location.hostname + ":8443";
}

function createWebSocket(playerId)
{
	return new WebSocket(
        `wss://${window.pidom}/ws/match/${window.matchId}/` +
        `?playerId=${playerId}`);
}

function closeMatchWssOnEnter()
{
	const socket = window.matchSocket;
	const socket2 = window.matchSocket2;	

	const closeMatchWsOnEnter = socket => {
		if (socket && socket.readyState === WebSocket.OPEN && window.antiLoop)	
			return socket.close(), true;
		return false;			
	};
	const ret = closeMatchWsOnEnter(socket); 
	const ret2 = closeMatchWsOnEnter(socket2);
	return (ret || ret2); 
}

function initMatchWs()
{
	if (closeMatchWssOnEnter())
		return;    
	initDomain();
	window.antiLoop = true;
	const [pads, elements] = get_match_elements();	
	setSpec(elements.spec);	
	initFirstPlayer(pads, elements);	
	initSecPlayer();	
	addKeyBoardEvent();
	pongUpdate(pads);	
}

function initFirstPlayer(pads, elements)
{
	let waitingState = ["waiting"];
	
    window.matchSocket = createWebSocket(window.playerId);
	window.matchSocket.onclose = event => matchWsDisconnectStrategy(event);
	window.matchSocket.onmessage = event => onMatchWsMessage(
		event, pads, elements, waitingState);
}

function matchWsDisconnectStrategy(event)
{	
	removeKeyBoardEvent();
	window.antiLoop = false;	
	if (event.code !== 3000 && !window.stopFlag)		
		initMatchWs();	
	window.stopFlag = false;
}

function get_match_elements()
{
	const pads = {
		p1: document.getElementById("p1"),
		p2: document.getElementById("p2"),
		ball: document.getElementById("ball")	
	};
	const elements = {		
		waiting: document.getElementById("waiting"),
		endCont: document.getElementById("end-cont"),
		end: document.getElementById("end"),
		left: document.getElementById("inst-left"),
		rght: document.getElementById("inst-right"),
		score: document.getElementById("score"),
		spec: document.getElementById("spec"),
		match: document.getElementById("match")
	};
	return [pads, elements];
}
