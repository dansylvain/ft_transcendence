
function stopMatch(matchId)
{
	const input = document.getElementById("match-player-name");
	if (input)
	{
		input.style.display = "none";
		input.value = "";
	}
	if (!matchId)
	{
		console.log("matchID EST NULLE");
		const oldScripts = document.querySelectorAll("script.match-script");
		console.log("olscript len", oldScripts.length);			
		oldScripts.forEach(oldScript =>{console.log("old: ", oldScript.src); oldScript.remove()});
		return;
	}
		
	if (window.selfMatchId == matchId)
	{	
		fetch(`/match/stop-match/${window.playerId}/${matchId}/`)
		.then(response => {
			if (!response.ok) 
				throw new Error(`Error HTTP! Status: ${response.status}`);		  
			return response.text();
		})
		.then(data => console.log(data))
		.catch(error => console.log(error))
	}
	else
		document.getElementById('match').remove()
	console.log("YOUHOUHOUHOU");
	// if (window.selfMatchId != window.matchId)
	// {
		// console.log("jypigequeuedalle");
		if (!window.matchSocket)
			console.log("LE WEBSOCKET ETS NULL.");
		else 
		{
			// console.log("je sais pas ce qu eje fou la");
			if (window.matchSocket.readyState === WebSocket.OPEN)
			{
				console.log("je vais envoyer 42");
				window.stopFlag = true
				window.matchSocket.close(3666);
				if (window.matchSocket2)
					window.matchSocket2.close(3666);
			} 
			else 
			{
				console.log("La WebSocket était déjà fermée.");
			}
			console.log("je nai pas plante");
		}
		console.log("toujours vivant");
		const oldScripts = document.querySelectorAll("script.match-script");
		console.log("olscript len", oldScripts.length);			
		oldScripts.forEach(oldScript =>{console.log("old: ", oldScript.src); oldScript.remove()});
	// }
	// else
	// 	console.log("pas spec!!");
	
}

// function setCommands(socket, socket2) {
	
// 	const keysPressed = {};
// 	document.addEventListener("keydown", function(event) {

// 		keysPressed[event.key] = true;
// 		// console.log("event :", event.key);
// 		if (socket.readyState === WebSocket.OPEN)
// 		{
// 			if (keysPressed[event.key] === true) 
// 			{
// 				event.preventDefault();
// 				socket.send(JSON.stringify({
// 					action: 'move', dir: 'up'}));
// 			} else if (keysPressed[event.key] === true) 
// 			{
// 				event.preventDefault();
// 				socket.send(JSON.stringify({
// 					action: 'move', dir: 'down'}));
// 			}
// 			if (socket2 && socket2.readyState === WebSocket.OPEN)
// 			{
// 				if (keysPressed[event.key] === true) 
// 				{
// 					event.preventDefault();
// 					socket2.send(JSON.stringify({
// 						action: 'move', dir: 'up'}));
// 				} else if (keysPressed[event.key] === true) 
// 				{
// 					event.preventDefault();
// 					socket2.send(JSON.stringify({
// 						action: 'move', dir: 'down'}));
// 				}
// 			}
// 		} 
// 	});
// 	document.addEventListener("keyup", event => {
// 		delete keysPressed[event.key];
// 	});
// }
// function setCommands(socket, socket2) {
//     const keysPressed = {};

//     document.addEventListener("keydown", function(event) {
//         keysPressed[event.key] = true; 

//         if (socket.readyState === WebSocket.OPEN) {
//             if (keysPressed["ArrowUp"]) { 
//                 event.preventDefault();
//                 socket.send(JSON.stringify({ action: 'move', dir: 'up' }));
//             }
//             if (keysPressed["ArrowDown"]) { 
//                 event.preventDefault();
//                 socket.send(JSON.stringify({ action: 'move', dir: 'down' }));
//             }
//         }

//         if (socket2 && socket2.readyState === WebSocket.OPEN) {
//             if (keysPressed["+"]) { 
//                 event.preventDefault();
//                 socket2.send(JSON.stringify({ action: 'move', dir: 'up' }));
//             }
//             if (keysPressed["Enter"]) { 
//                 event.preventDefault();
//                 socket2.send(JSON.stringify({ action: 'move', dir: 'down' }));
//             }
//         }
//     });

//     document.addEventListener("keyup", event => {
//         delete keysPressed[event.key];
//     });
// }

function setCommands(socket, socket2) {
    const keysPressed = {}; // Stocker les touches enfoncées
    let animationFrameId = null; // Stocke l'ID du requestAnimationFrame

    function sendCommands() {
        if (socket.readyState === WebSocket.OPEN) {
            if (keysPressed["ArrowUp"]) {
				
                socket.send(JSON.stringify({ action: 'move', dir: 'up' }));
            }
            if (keysPressed["ArrowDown"]) {
				
                socket.send(JSON.stringify({ action: 'move', dir: 'down' }));
            }
        }

        if (socket2 && socket2.readyState === WebSocket.OPEN) {
            if (keysPressed["+"]) {
                socket2.send(JSON.stringify({ action: 'move', dir: 'up' }));
            }
            if (keysPressed["Enter"]) {
                socket2.send(JSON.stringify({ action: 'move', dir: 'down' }));
            }
        }

        animationFrameId = requestAnimationFrame(sendCommands); // Appelle la fonction en boucle
    }

    document.addEventListener("keydown", function(event) {
		// event.preventDefault();
        if (!keysPressed[event.key]) { // Empêche d'ajouter plusieurs fois la même touche
            keysPressed[event.key] = true;
        }
        
        if (!animationFrameId) { // Démarre l'animation seulement si elle n'est pas déjà en cours
            animationFrameId = requestAnimationFrame(sendCommands);
        }
    });

    document.addEventListener("keyup", function(event) {
        delete keysPressed[event.key];

        if (Object.keys(keysPressed).length === 0) {
            cancelAnimationFrame(animationFrameId);
            animationFrameId = null;
        }
    });
}

function setCommands2(socket) {

	document.addEventListener("keydown", function(event) {
		// console.log("event :", event.key);
		if (socket.readyState === WebSocket.OPEN)
		{
			if (event.key === "+") 
			{
				event.preventDefault();
				socket.send(JSON.stringify({
					action: 'move', dir: 'up'}));
			} else if (event.key === "Enter") 
			{
				event.preventDefault();
				socket.send(JSON.stringify({
					action: 'move', dir: 'down'}));
			}
		} 
	});
}
window.currentX = window.currentX || 0
window.currentY = window.window.currentY || 0;
window.targetX = window.targetX || 0
window.targetY = window.window.targetY || 0;
window.newTargetX = window.newTargetX || 0
window.newTargetY = window.window.newTargetY || 0;
window.actualPads = window.actualPads || [0, 0];
window.targetPads = window.targetPads || [0, 0];
window.targets = window.targets || [];
window.speed = window.speed || 1/16; // Ajuste entre 0.05 (lent) et 0.3 (rapide) pour fluidité
window.offsetX = window.offsetX || 0;
window.offsetY = window.offsetY || 0;
window.offsets = window.offsets || [0, 0];
function animate2(pads) {
	// console.log("pads");
	eps = 0.1;
	// let tar = targets.shift();
	// console.log(tar);
	// // if (Math.abs(currentX - targetX) < eps || Math.abs(currentY - targetY) < eps)
	// // {
	// 	console.log("animate");
	// 	console.log(tar);
	// 	// if (tar) {

	// 		// if (currentX - targetX >= -eps && currentX - targetX <= eps)
	// 		// {
	// 			offsetX = (tar[0] - currentX);
	// 			targetX = tar[0];
	// 		// }
	// 		// if (currentY - targetY >= -eps && currentY - targetY <= eps)
	// 		// {
	// 			// offsetY = (newTargetY - currentY);
	// 			offsetY = (tar[1] - currentY);
	// 			// targetY = newTargetY;
	// 			targetY = tar[1];			
	// 		// }
	// 	// }
	// 	// else
		// 	console.log("notar");
	// }

	// currentX += (newTargetX - currentX) * speed;
	
	// currentY += (newTargetY - currentY) * speed;
		// Si on a atteint la cible précédente
		if (Math.abs(currentX - targetX) < eps && Math.abs(currentY - targetY) < eps) {
			const tar = targets.shift();
			if (tar) {
				targetX = tar[0];
				targetY = tar[1];
				// targetX = newTargetX;
				// targetY = newTargetY;
			}
		}
	
		// Met à jour les déplacements vers la cible actuelle
	// 	const offsetX = targetX - currentX;
	// 	const offsetY = targetY - currentY;
    // currentX += offsetX * speed;
	// if (currentX > targetX)
	// {
	// 	currentX = targetX;
	// 	targetX = newTargetX;
	// }
	// currentY += offsetY * speed;
	// if (currentY > targetY)
	// {
	// 	currentY = targetY;
	// 	targetY = newTargetY;
	// }

	// currentX = newTargetX;
	// currentY = newTargetY;
	// const tar = targets.shift();
	// if (tar)
	// {

		// currentX = tar[0];
		// currentY = tar[1];
		currentX += (tar[0] - currentX) * speed;
		currentY += (tar[1] - currentY) * speed;
		actualPads[0] += (targetPads[0] - actualPads[0]) * speed;
		actualPads[1] += (targetPads[1] - actualPads[1]) * speed;
		// console.log("ANIMATION");
		pads[2].style.transform = `translate(${currentX}px, ${currentY}px)`;
		pads[0].style.transform = `translateY(${actualPads[0]}px)`;
		pads[1].style.transform = `translateY(${actualPads[1]}px)`;
		// pads[2].style.left = currentX + "%";
	// }
	// pads[2].style.top = currentY + "%";
    requestAnimationFrame(()=>animate(pads));
}
function animate3(pads) {
	const eps = 0.4; // tolérance de distance avant de prendre un nouveau point

	// Si on est proche de la cible, on passe au suivant
	// console.log(Math.abs(currentX - targetX));
	if (Math.abs(currentX - targetX) < eps && Math.abs(currentY - targetY) < eps) {
		const tar = targets.shift();
		if (tar) {
			// console.log("je dois passer ici a chaque refresh serveur");
			targetX = tar[0];
			targetY = tar[1];
		}
	}
	// targetX = newTargetX;
	// targetY = newTargetY;
	// Interpolation fluide vers la cible actuelle
	// const tar = targets.shift();
	// if (tar) {
		
	// 	currentX = tar[0];
	// 	currentY = tar[1];
	// }
	currentX += (targetX - currentX) * speed;
	currentY += (targetY - currentY) * speed;
	// currentX = newTargetX;
	// currentY = newTargetY;
	// Interpolation pour les pads
	actualPads[0] += (targetPads[0] - actualPads[0]) * speed;
	actualPads[1] += (targetPads[1] - actualPads[1]) * speed;

	// Appliquer le style
	pads[2].style.transform = `translate(${currentX}px, ${currentY}px)`;
	pads[0].style.transform = `translateY(${actualPads[0]}px)`;
	pads[1].style.transform = `translateY(${actualPads[1]}px)`;

	requestAnimationFrame(() => animate(pads));
}
window.exCurrentX = window.exCurrentX || 0;
window.exCurrentY = window.exCurrentY || 0;
window.senseX = window.senseX || "right";
window.senseY = window.senseY || "up";
window.exSenseX = window.exSenseX || "right";
window.exSenseY = window.exSenseY || "down";
window.bounce = window.bounce || false;

function setSense()
{
	if (targetX < newTargetX)
		senseX = "right";
	else if (targetX > newTargetX)
		senseX = "left";
	if (targetY > newTargetY)
		senseY = "up";
	else if (targetY < newTargetY)
		senseY = "down";
	// console.log("sx: ", senseX, " sy: ", senseY)
}

function reInitExCurrent() {

	exCurrentX = currentX;
	exCurrentY = currentY;
}

function reInitTarget() {

	targetX = newTargetX;
	targetY = newTargetY;
}

function reInitExSense() {

	exSenseX = senseX;
	exSenseY = senseY;
}

function stopOverMove(snsX, snsY) {

	if (snsX === "right")
	{
		if (currentX > targetX)
		{
			// console.log("egalise 10");
			// console.log("yop", currentX, " t ", targetX);
			currentY = targetY;
			currentX = targetX;
			// bounce = false;
		}
	}
	else 
	{
		if (currentX < targetX)
		{
			// console.log("egalise 20");
			// console.log("yep", currentX, " t ", targetX);
			currentY = targetY;
			currentX = targetX;
			// bounce = false;
		}
	}
	if (snsY === "down")
	{
		if (currentY > targetY)
		{
			// console.log("egalise 1");

			// console.log("yip", currentY, " t ", targetY);
			currentY = targetY;
			currentX = targetX;
		}
	}
	else 
	{
		if (currentY < targetY)
		{
			// console.log("egalise 2");
			// console.log("yup", currentY, " t ", targetY);
			currentY = targetY;
			currentX = targetX;
		}
	}
}

function hasNewTarget() {

	return targetX !== newTargetX || targetY !== newTargetY;
}

function addOffsetToCurrent() {
		
	currentX += offsets[0];
	currentY += offsets[1];
}

function hasSenseSwitched() {

	return exSenseX !== senseX || exSenseY !== senseY;
}

function isTargetStrike() {

	return currentX === targetX && currentY === targetY;
}

function calculateOffset(spd)
{
	offsets[0] = (newTargetX - currentX) * spd;
	offsets[1] = (newTargetY - currentY) * spd;
}

function setSpeed() {

	speed = (1 - (1 / ((Math.abs(targetX - newTargetX) * 4) + 1)));
	// console.log("speed: ", speed);
}

window.celerity = window.celerity || 0;

function get_magnitude() {

	return Math.sqrt(
		((targetX - newTargetX) ** 2) +
		((targetY - newTargetY) ** 2)
	);
}

// function hasWall() {
	
// 	let wall = false;
// 	let new_celerity = get_magnitude();
// 	if (!celerity || new_celerity < celerity)
// 	{
// 		console.log("yeeee");
// 		wall = true;
// 		celerity = new_celerity;
// 	}
// 	return wall;
// }
window.hasWall = window.hasWall || false;
function animate(pads) {

	// if (hasNewTarget() && hasWall())
	// {
	// 	console.log("haswall");
	// 	// calculateOffset(speed);
	// 	// offsets = offsets.map(o => o * 2);
	// 	// beforeBounce = true;				
	// }

	if (!bounce)
	{
		if (hasNewTarget())
		{		
			setSense();
			// setSpeed();			
			// if (hasWall)
			// {
			// 	// console.log("haswall");
			// 	calculateOffset(1);
			// 	reInitTarget();
			// 	reInitExSense();
			// 	// offsets = offsets.map(o => o * 200);
			// 	// beforeBounce = true;				
			// }
			// if (hasSenseSwitched())
			if (hasWall)
			{
				bounce = true;
				calculateOffset(speed);
				reInitTarget();
				reInitExSense();
			}
			else
			{
			
				calculateOffset(speed);
				reInitTarget();
				reInitExSense();
			}
		}		
	}	
	addOffsetToCurrent();
	stopOverMove(exSenseX, exSenseY);

	if (isTargetStrike())
	{
		// console.log("bounce false");
		bounce = false;
		reInitExSense();
		// currentX += (newTargetX - currentX) * 0.5;
		// currentY += (newTargetY - currentY) * 0.5;	
	}

	applyMove(pads);
}

function applyMove(pads) {

	actualPads[0] += (targetPads[0] - actualPads[0]) * speed;
	actualPads[1] += (targetPads[1] - actualPads[1]) * speed;
	pads[2].style.transform = `translate(${currentX}px, ${currentY}px)`;
	pads[4].style.transform = `translate(${newTargetX}px, ${newTargetY}px)`;
	pads[0].style.transform = `translateY(${actualPads[0]}px)`;
	pads[1].style.transform = `translateY(${actualPads[1]}px)`;
	requestAnimationFrame(() => animate(pads));
}

function animateZ(pads) {

	actualPads[0] += (targetPads[0] - actualPads[0]) * speed;
	actualPads[1] += (targetPads[1] - actualPads[1]) * speed;
	pads[2].style.transform = `translate(${newTargetX}px, ${newTargetY}px)`;
	pads[0].style.transform = `translateY(${actualPads[0]}px)`;
	pads[1].style.transform = `translateY(${actualPads[1]}px)`;
	requestAnimationFrame(() => animateZ(pads));
}
// Appelle animate une seule fois au début


// À chaque message WebSocket :
// function onMatchWsMessage(event, pads, [waiting, end], waitingState) {
//     const data = JSON.parse(event.data);
//     const matchRect = document.getElementById("match").getBoundingClientRect();

//     if (pads[0] && pads[1] && data.yp1 !== undefined && data.yp2 !== undefined) {
//         pads[0].style.top = data.yp1 + "%";
//         pads[1].style.top = data.yp2 + "%";
        
//         targetX = data.ball[0] * (matchRect.width / 100);
//         targetY = data.ball[1] * (matchRect.height / 100);

//         pads[3].innerText = data.score[0] + " | " + data.score[1];
//     }
// }

function startCountdown(delay)
{
	// console.log("%%%%%%%%%%%%%%% get the shit going , BABY!!!%%%%%%%%%%%%%%");

	loaderElement = document.querySelector(".loader");
	if (loaderElement)
		loaderElement.style.opacity = "1";

    const countdownEl = document.querySelector('.countdown');
    const countdownEndsAt = window.gameStartTimestamp * 1000 + delay * 1000;
    // console.log("Le compte à rebours se termine à:", countdownEndsAt / 1000);

	function updateCountdown() {
        const now = Date.now();
        const remaining = Math.ceil((countdownEndsAt - now) / 1000);

        if (remaining > 0) {
            countdownEl.textContent = remaining;
            requestAnimationFrame(updateCountdown);
        } else if (remaining > -1) {
            countdownEl.textContent = "GO!";
            requestAnimationFrame(updateCountdown);
        } else {
            loaderElement.style.opacity = "0";
            window.gameStartTimestamp = undefined;
        }
    }
	updateCountdown();
}

function onMatchWsMessage(event, pads, [waiting, endCont, end], waitingState) {
	match = document.getElementById("match");

	// console.log("SERVEUR");
	// requestAnimationFrame(() => {
	const data = JSON.parse(event.data);
	if (data.timestamp && !data.state) {
		if (window.gameStartTimestamp === undefined) {
			window.gameStartTimestamp = data.timestamp;
            delay = data.delay;
			// console.log("✅ Premier timestamp enregistré:", data.timestamp);
	
			// Ici tu peux démarrer ton compte à rebours
			// startCountdownFrom(data.timestamp, '.countdown', '.loader');
			// console.log("################START THE GAME##############");

            startCountdown(delay);
		} else {
			// console.log("⏩ Timestamp déjà reçu, ignoré.");
		}
		return;
	}
	// console.log("match mesage: ", data);
	
	//! TO OPTI
	const leftNameElement = document.getElementById("inst-left");
	const rightNameElement = document.getElementById("inst-right");
	if (data.names)
	{
		leftNameElement.innerHTML = data.names[0] + "<br> keys: enter / +"
		rightNameElement.innerHTML = data.names[1] + "<br> keys: ↑ / ↓";
	}
	if (data.state == "end")
	{	
        let gifUrl;
        if (window.selfName == data.winnerName)
            gifUrl = "https://dansylvain.github.io/pictures/sdurif.webp";
		else if (spec.style.display != "none")
			{
				gifUrl = "https://dansylvain.github.io/pictures/eye.webp";
				spec.style.display = "none";
			}
		else 
			gifUrl = "https://dansylvain.github.io/pictures/MacronExplosion.webp";

		end.innerHTML = `The winner is: ${data.winnerName} <br> 
		Score: ${data.score[0]} : ${data.score[1]} <br> 
		<img src="${gifUrl}" 
		alt="Winner GIF" 
		class="winner-gif">
		`;
		
		endCont.classList.add("end-cont");
		console.log("🏁 Match terminé, reset du timestamp");
		window.gameStartTimestamp = undefined;	
	}
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
	match = document.getElementById("match");
	const matchRect = match.getBoundingClientRect();
	const ballRect = pads[2].getBoundingClientRect();
	pads[2].style.top = -(matchRect.width / 100);
	// pads[2].style.left = (matchRect.width / 100) * 2;
	pads[2].style.width = (matchRect.width / 100) * 2;
	pads[2].style.height = (matchRect.width / 100) * 2;
	pads[4].style.width = (matchRect.width / 100) * 2;
	pads[4].style.height = (matchRect.height / 100) * 2;
	// pads[0].style.width = (matchRect.width / 100) * 10;
	// pads[0].style.height = (matchRect.height / 100) * 40;
	// pads[1].style.width = (matchRect.width / 100) * 10;
	// pads[1].style.height = (matchRect.height / 100) * 40;
	// console.log(" w ", rect.width, " h ", rect.height);
	// console.log(" ball 0 ", data.ball[0], " ball1 ", data.ball[1]);
	// console.log("data: ", `${data.ball[0] * (rect.width / 100)}`, `${data.ball[1] * (rect.height / 100)}}`);
	// if (pads[0] && pads[1] && data.yp1 !== undefined && data.yp2 !== undefined)
	// {
	// 	pads[0].style.top = data.yp1 + "%";
	// 	pads[1].style.top = data.yp2 + "%";
	// 	// pads[2].style.left = data.ball[0] + "%";
	// 	// pads[2].style.top = data.ball[1] + "%";
	// 	// pads[0].style.transform = `translateY(${data.yp1}%)`;
	// 	// pads[1].style.transform = `translateY(${data.yp2}%)`;
	// 	pads[2].style.transform = `translate(${data.ball[0] * (rect.width / 100)}px, ${data.ball[1] * (rect.height / 100)}px)`;
	// 	pads[3].innerText = data.score[0] + " | " + data.score[1];
	// }
	
    if (pads[0] && pads[1] && data.yp1 !== undefined && data.yp2 !== undefined) {
        // pads[0].style.top = data.yp1 + "%";
        // pads[1].style.top = data.yp2 + "%";
        
		targetPads[0] = data.yp1 * (matchRect.height / 100);
		targetPads[1] = data.yp2 * (matchRect.height / 100);

        // newTargetX = data.ball[0] * (matchRect.width / 100);
        // newTargetY = data.ball[1] * (matchRect.height / 100);
		// eps = 1
		// console.log("targetx ", targetX, " currentx ", currentX, " targety ", targetY, " currentY ", currentY);
		// if ((targetX - currentX >= -eps && targetX - currentX <= eps)
		// 	 &&
		// 	(targetY - currentY >= -eps && targetY - currentY <= eps)
		// )			
		// {
		// console.log("ICI: ", data.hasWall);
			hasWall = data.hasWall;
			newTargetX = data.ball[0] * (matchRect.width / 100);
			newTargetY = data.ball[1] * (matchRect.height / 100);
			targets.push([newTargetX, newTargetY]);
			// console.log(targets);
		// }
		
        pads[3].innerText = data.score[0] + " | " + data.score[1];
    }
	// });
		
}

// function onMatchWsMessage2(event, pads, [waiting, end], waitingState) {
		
// 	const data = JSON.parse(event.data);

// 	if (data.state == "end")
// 	{	
// 		end.innerHTML = "the winner is :" + data.winnerId + end.innerHTML;
// 		end.classList.add("end");
// 	}
// 	if (waitingState[0] != data.state) 
// 	{
// 		waitingState[0] = data.state;	
// 		if (waiting) 
// 		{
// 			if (data.state == "waiting")			
// 				waiting.classList.remove("no-waiting");
// 			else			
// 				waiting.classList.add("no-waiting");			
// 		}			
// 	}
// 	if (pads[0] && pads[1] && data.yp1 !== undefined && data.yp2 !== undefined)
// 	{
// 		pads[0].style.top = data.yp1 + "%";
// 		pads[1].style.top = data.yp2 + "%";
// 		pads[2].style.top = data.ball[0] + "%";
// 		pads[2].style.top = data.ball[1] + "%";
// 		pads[3].innerText = data.score[0] + " | " + data.score[1];
// 	}
// }



function sequelInitMatchWs(socket) {

	const pads = [
		document.getElementById("p1"),
		document.getElementById("p2"),
		document.getElementById("ball"),
		document.getElementById("score"),
		document.getElementById("ball2")
	];
	const [waiting, endCont, end] = [		
		document.getElementById("waiting"),
		document.getElementById("end-cont"),
		document.getElementById("end")];	
	let waitingState = ["waiting"];
	requestAnimationFrame(()=>animate(pads));
	socket.onmessage = event => onMatchWsMessage(
		event, pads, [waiting, endCont, end], waitingState);
	
	const spec = document.getElementById("spec")
	if (spec)
	{
		if (window.selfMatchId != window.matchId)
			spec.style.display = "block";
		else
			spec.style.display = "none";
	}
	// console.log("BEFORE INIT SEC !!!!!! ", window.player2Id, typeof(window.player2Id));
	if (window.player2Id != 0)
	{
		// console.log("INIT SEC !!!!!! ", window.player2Id);
		initSecPlayer();
	}
	setCommands(socket, window.matchSocket2);
}

function initSecPlayer() {

    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
        window.pidom = "localhost:8443";
	else
		window.pidom = window.location.hostname + ":8443";

    window.matchSocket2 = new WebSocket(
        `wss://${window.pidom}/ws/match/${window.matchId}/` +
        `?playerId=${window.player2Id}`);
	window.matchSocket2.onopen = () => {
		// console.log("Connexion Match établie 2nd Player😊");
	};
	window.matchSocket2.onclose = (event) => {
		// console.log("Connexion Match disconnected 😈 2nd Player");
	};
	// setCommands2(window.matchSocket2);
}

function initMatchWs() {
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
        window.pidom = "localhost:8443";
	else
		window.pidom = window.location.hostname + ":8443";

//si je viens du debut je sui sclosé (et je reviens par boucle) si je viens de onclse je continu normal
	// console.log("INIT MATCH 😊😊😊");
	// console.log("STOP: " + window.stopFlag);
	// console.log("ANTILOPP: " + window.antiLoop);
	if (window.matchSocket && window.antiLoop)
		return window.matchSocket.close();
	if (window.matchSocket2 && window.antiLoop)
		return window.matchSocket2.close();
    // if (window.matchSocket)
	// 	window.matchSocket.close();
	window.antiLoop = true;
    window.matchSocket = new WebSocket(
        `wss://${window.pidom}/ws/match/${window.matchId}/` +
        `?playerId=${window.playerId}`);
	window.matchSocket.onopen = () => {
		// console.log("Connexion Match établie 😊");
	};
	window.matchSocket.onclose = (event) => {	
		// console.log("Connexion Match disconnected 😈");		
		window.antiLoop = false;
		// console.log("CODE: " + event.code);
		// console.log("STOP: " + window.stopFlag);
		if (event.code !== 3000 && !window.stopFlag)
		{			
			// console.log("codepas42");
			initMatchWs();	
		}
		else
			// console.log("code42");
		window.stopFlag = false;
	};
	sequelInitMatchWs(window.matchSocket);
}
