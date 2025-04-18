function initPongAnimation(register) {
	const container = document.getElementById('pong-background');
	if (!container) return;

	container.innerHTML = '';
	const cols = 12;
	const rows = 7;
	const spacingX = window.innerWidth / cols;
	const spacingY = window.innerHeight / rows;
	const speed = 0.5;

	const icons = [];

	for (let row = -1; row <= rows; row++) {
		for (let col = -1; col <= cols; col++) {
			const icon = document.createElement('div');
			icon.className = 'pong-icon';
			icon.style.left = `${col * spacingX}px`;
			icon.style.top = `${row * spacingY}px`;
			container.appendChild(icon);

			icons.push({
				el: icon,
				x: col * spacingX,
				y: row * spacingY,
			});
		}
	}

	function animate() {
		const w = window.innerWidth;
		const h = window.innerHeight;

		for (const icon of icons) {
			if (register == true) {
				icon.x -= speed;
			}
			else {
				icon.x += speed;
			}
			icon.y += speed;

			if (register == true) {
				if (icon.x < -50) icon.x += (cols + 2) * spacingX;
			}
			else {
				if (icon.x > w) icon.x -= (cols + 2) * spacingX;
			}
			if (icon.y > h) icon.y -= (rows + 2) * spacingY;

			icon.el.style.left = `${icon.x}px`;
			icon.el.style.top = `${icon.y}px`;
		}
		window.pongAnimationId = requestAnimationFrame(animate);
	}
	if (window.pongAnimationId) {
		cancelAnimationFrame(window.pongAnimationId);
	}
	animate();
}