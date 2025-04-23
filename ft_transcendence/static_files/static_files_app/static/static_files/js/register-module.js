document.addEventListener("htmx:beforeSwap", function (evt) {
	console.log("REGISTER FORM LISTENNING");
	console.log(evt.detail.target.id);

	if (evt.detail.target.id === "register-form") {
		try {
			console.log("Réponse brute:", evt.detail.xhr.responseText); // debug
			const response = JSON.parse(evt.detail.xhr.responseText);

			if (response.success) {
				evt.detail.shouldSwap = false;

				htmx
					.ajax("GET", "/home/", {
						target: "body",
						swap: "outerHTML",
						headers: { "HX-Login-Success": "true" },
					})
					.then(function () {
						history.pushState(null, "", "/home/");
					});
			} else {
				const messageElement = document.getElementById("register-form");
				const sanitizedMessage = DOMPurify.sanitize(response.message);
				messageElement.textContent = sanitizedMessage;
			}
		} catch (e) {
			console.error("Erreur de traitement de la réponse:", e);
		}
	}
});