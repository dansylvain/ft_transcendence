window.tjs_container = window.tjs_container || document.getElementById('scene-container');

window.tjs_scene = window.tjs_scene || new THREE.Scene();
window.tjs_camera = window.tjs_camera || new THREE.PerspectiveCamera(75, window.tjs_container.clientWidth / window.tjs_container.clientHeight, 0.1, 1000);
window.tjs_renderer = window.tjs_renderer || new THREE.WebGLRenderer({ antialias: true });
window.tjs_renderer.setSize(window.tjs_container.clientWidth, window.tjs_container.clientHeight);
window.tjs_container.appendChild(window.tjs_renderer.domElement);

window.tjs_textureLoader = window.tjs_textureLoader || new THREE.TextureLoader();

window.tjs_rgeo = window.tjs_rgeo || new THREE.BoxGeometry(10, 10, 40 * (60 / 100));
window.tjs_sgeo = window.tjs_sgeo || new THREE.SphereGeometry(2, 32, 32);

window.tjs_rmat = window.tjs_rmat || [
    new THREE.MeshBasicMaterial({ map: window.tjs_textureLoader.load('https://threejs.org/examples/textures/crate.gif') }),
    new THREE.MeshBasicMaterial({ map: window.tjs_textureLoader.load('https://threejs.org/examples/textures/crate.gif') }),
    new THREE.MeshBasicMaterial({ map: window.tjs_textureLoader.load('https://threejs.org/examples/textures/crate.gif') }),
    new THREE.MeshBasicMaterial({ map: window.tjs_textureLoader.load('https://threejs.org/examples/textures/crate.gif') }),
    new THREE.MeshBasicMaterial({ map: window.tjs_textureLoader.load('https://threejs.org/examples/textures/crate.gif') }),
    new THREE.MeshBasicMaterial({ map: window.tjs_textureLoader.load('https://threejs.org/examples/textures/crate.gif') })
];

window.tjs_smat = window.tjs_smat || new THREE.MeshBasicMaterial({ map: window.tjs_textureLoader.load('https://threejs.org/examples/textures/crate.gif') });

window.tjs_r1 = window.tjs_r1 || new THREE.Mesh(window.tjs_rgeo, window.tjs_rmat);
window.tjs_r2 = window.tjs_r2 || new THREE.Mesh(window.tjs_rgeo, window.tjs_rmat);

window.tjs_ball = window.tjs_ball || new THREE.Mesh(window.tjs_sgeo, window.tjs_smat);

window.tjs_scene.add(window.tjs_ball);
window.tjs_scene.add(window.tjs_r1);
window.tjs_scene.add(window.tjs_r2);

window.tjs_r1.position.z = -20;
window.tjs_r1.position.x = 5;

window.tjs_r2.position.z = -20;
window.tjs_r2.position.x = 90;

window.tjs_ball.position.x = -1;
window.tjs_ball.position.z = -1;

window.tjs_upgrade = window.tjs_upgrade || {
	user_lvl: 0,
	points: 0,
	cooldown: 5,
}

function actionCooldownUpdate() {
	// update the html button
	if (!window.tjs_upgrade.cooldown) {
		document.getElementById("upgrade").innerHTML = `Upgrade (+${window.tjs_upgrade.points})`;
	} else if (window.tjs_upgrade.points) {
		document.getElementById("upgrade").innerHTML = `Upgrade (+${window.tjs_upgrade.points}) ${window.tjs_upgrade.cooldown}s`;
	} else {
		document.getElementById("upgrade").innerHTML = `Upgrade ${window.tjs_upgrade.cooldown}s`;
	}
}

// function call on button click
function actionUpgrade() {
	if (window.tjs_upgrade.points < 1) {
		return;
	}
	window.tjs_upgrade.points--;
	switch (window.tjs_upgrade.user_lvl) {
		case 0:
    		window.tjs_ball.material.color.setHex(0x00ff00);
			break;
		case 1:
			window.tjs_ball.material.color.setHex(0xff0000);
			break;
		case 2:
			window.tjs_ball.material.color.setHex(0x0000ff);
			break;
		case 3:
			window.tjs_ball.material.color.setHex(0xffffff);
			window.tjs_ball.material.map = textureLoader.load('https://media.tenor.com/YkyhmCCJd_0AAAAM/aaaa.gif');
			break;
		default:
			break;
	}
	window.tjs_upgrade.user_lvl++;
	actionCooldownUpdate();
}

// function call each seconds
function actionCooldown() {
	if (window.tjs_upgrade.cooldown > 0) {
		window.tjs_upgrade.cooldown--;
	} else {
		window.tjs_upgrade.cooldown = 5;
	}
	if (window.tjs_upgrade.cooldown == 0) {
		window.tjs_upgrade.points++;
	}
	actionCooldownUpdate();
}

actionCooldownUpdate();
setInterval(actionCooldown, 1000);

window.tjs_isDragging = false;
window.tjs_previous_mouse = { x: 0, y: 0 };

window.tjs_radius = window.tjs_radius || 15;

window.tjs_theta = window.tjs_theta || 0;         // horizontal angle
window.tjs_phi = window.tjs_phi || Math.PI / 2;   // vertical angle

window.tjs_container.onmousedown = function (e) {
	window.tjs_isDragging = true;
	window.tjs_previous_mouse = { x: e.clientX, y: e.clientY };
};

window.tjs_container.onmouseup = function () {
	window.tjs_isDragging = false;
};

window.tjs_container.onmousemove = function (e) {
	if (!window.tjs_isDragging)
        return;

	let sensitivity = 0.005;

	// update angles based on mouse movement
	window.tjs_theta -= (e.clientX - window.tjs_previous_mouse.x) * sensitivity;
	window.tjs_phi   -= (e.clientY - window.tjs_previous_mouse.y) * sensitivity;

	window.tjs_phi = Math.max(0.1, Math.min(Math.PI - 0.1, window.tjs_phi));

	// calculate new camera position
	window.tjs_camera.position.x = window.tjs_radius * Math.sin(window.tjs_phi) * Math.sin(window.tjs_theta) + tjs_camera_offset_x;
	window.tjs_camera.position.z = window.tjs_radius * Math.sin(window.tjs_phi) * Math.cos(window.tjs_theta) + tjs_camera_offset_z;
	window.tjs_camera.position.y = window.tjs_radius * Math.cos(window.tjs_phi);

	window.tjs_camera.lookAt(tjs_camera_offset_x, 0, tjs_camera_offset_z);

	window.tjs_previous_mouse = { x: e.clientX, y: e.clientY };
};

// if mouse is inside the container and scrolling
window.tjs_container.onwheel = function (e) {
	window.tjs_radius -= e.deltaY * 0.1;
	window.tjs_radius = Math.max(10, Math.min(500, window.tjs_radius));

	window.tjs_camera.position.x = window.tjs_radius * Math.sin(window.tjs_phi) * Math.sin(window.tjs_theta) + tjs_camera_offset_x;
	window.tjs_camera.position.z = window.tjs_radius * Math.sin(window.tjs_phi) * Math.cos(window.tjs_theta) + tjs_camera_offset_z;
	window.tjs_camera.position.y = window.tjs_radius * Math.cos(window.tjs_phi);

	window.tjs_camera.lookAt(tjs_camera_offset_x, 0, tjs_camera_offset_z);
};

window.tjs_container.addEventListener('wheel', function (event) {
    event.preventDefault();
}, { passive: false });

window.tjs_container.addEventListener('touchmove', function (event) {
    event.preventDefault();
}, { passive: false });

// resize canvas on window resize
window.addEventListener('resize', function () {
	window.tjs_renderer.setSize(window.tjs_container.clientWidth, window.tjs_container.clientHeight);
	window.tjs_camera.aspect = window.tjs_container.clientWidth / window.tjs_container.clientHeight;
	window.tjs_camera.updateProjectionMatrix();
});

function animate() {
    requestAnimationFrame(animate);

    window.tjs_ball.rotation.z += 0.1;

    window.tjs_renderer.render(window.tjs_scene, window.tjs_camera);
}

const tjs_camera_offset_x = 50;
const tjs_camera_offset_z = 30;

window.tjs_camera.position.x = tjs_camera_offset_x;
window.tjs_camera.position.y = 50;
window.tjs_camera.position.z = tjs_camera_offset_z;
window.tjs_camera.lookAt(tjs_camera_offset_x, 0, tjs_camera_offset_z);

animate();

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
		event.preventDefault();
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

function onMatchWsMessage(event, [waiting, end], waitingState) {
	const data = JSON.parse(event.data);

	if (data.state == "end")
	{	
		end.innerHTML = "the winner is :" + data.winnerId + end.innerHTML;
		end.classList.add("end");
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

	if (data.yp1 !== undefined && data.yp2 !== undefined) {
        console.log("data.yp1: ", data.yp1);

    	window.tjs_r1.position.z = (60 / 100) * (data.yp1);
		window.tjs_r2.position.z = (60 / 100) * (data.yp2);

		window.tjs_ball.position.x = (100 / 100) * (data.ball[0] - 1);
		window.tjs_ball.position.z = (60 / 100) * (data.ball[1] - 1);
	}
}

function sequelInitMatchWs(socket) {
	const [waiting, end] = [		
		document.getElementById("waiting"),	document.getElementById("end")];	
	let waitingState = ["waiting"];

	socket.onmessage = event => onMatchWsMessage(
		event, [waiting, end], waitingState);

	const spec = document.getElementById("spec")
	if (spec)
	{
		if (window.selfMatchId != window.matchId)
			spec.style.display = "block";
		else
			spec.style.display = "none";
	}
	initSecPlayer();
	setCommands(socket, window.matchSocket2);
}

function initSecPlayer() {

	if (window.rasp == "true")
		window.matchSocket2 = new WebSocket(
			`wss://${window.pidom}/ws/match/${window.matchId}/` +
			`?playerId=${-window.playerId}`);
	else	
		window.matchSocket2 = new WebSocket(
			`wss://localhost:8443/ws/match/${window.matchId}/` +
			`?playerId=${-window.playerId}`);

	window.matchSocket2.onopen = () => {
		console.log("Connexion Match établie 2nd Player😊");
	};
	window.matchSocket2.onclose = (event) => {
		console.log("Connexion Match disconnected 😈 2nd Player");
	};
	// setCommands2(window.matchSocket2);
}

function initMatchWs() {
//si je viens du debut je sui sclosé (et je reviens par boucle) si je viens de onclse je continu normal
	console.log("INIT MATCH 😊😊😊");
	console.log("STOP: " + window.stopFlag);
	console.log("ANTILOPP: " + window.antiLoop);
	if (window.matchSocket && window.antiLoop)
		return window.matchSocket.close();
    // if (window.matchSocket)
	// 	window.matchSocket.close();
	window.antiLoop = true;

	if (window.rasp == "true")
		window.matchSocket = new WebSocket(
			`wss://${window.pidom}/ws/match/${window.matchId}/` +
			`?playerId=${window.playerId}`);
	else	
		window.matchSocket = new WebSocket(
			`wss://localhost:8443/ws/match/${window.matchId}/` +
			`?playerId=${window.playerId}`);

	window.matchSocket.onopen = () => {
		console.log("Connexion Match établie 😊");
	};
	window.matchSocket.onclose = (event) => {	
		console.log("Connexion Match disconnected 😈");		
		window.antiLoop = false;
		console.log("CODE: " + event.code);
		console.log("STOP: " + window.stopFlag);
		if (event.code !== 3000 && !window.stopFlag)
		{			
			console.log("codepas42");
			initMatchWs();	
		}
		else
			console.log("code42");
		window.stopFlag = false;
	};
	sequelInitMatchWs(window.matchSocket);
}

initMatchWs();
