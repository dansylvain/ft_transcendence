document.addEventListener("htmx:beforeSwap", function (evt) {
	if (evt.detail.target.id === "login-form") {
		try {
			console.log("Réponse brute:", evt.detail.xhr.responseText);
			const response = JSON.parse(evt.detail.xhr.responseText);

			if (response.success) {
				console.log("SUCCESS");
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
			} else if (response.message === "2FA is enabled") {
				// Store username for 2FA page
				const usernameInput = document.getElementById("username");
				if (usernameInput) {
					const usernameValue = usernameInput.value;
					sessionStorage.setItem("2fa_username", usernameValue);

					// Set username as global variable as another backup
					window.twoFAUsername = usernameValue;
				} else {
					console.error("Username input element not found");
				}

				// Redirect to 2FA page
				evt.detail.shouldSwap = false;
				console.log("Redirecting to 2FA page");

				// Get username for the URL
				const username = usernameInput ? usernameInput.value : "";

				// Include username in the URL to help with page transitions
				htmx
					.ajax(
						"GET",
						`/two-factor-auth/?username=${encodeURIComponent(username)}`,
						{
							target: "body",
							swap: "outerHTML",
						}
					)
					.then(function () {
						console.log("2FA page loaded, pushing history state");
						history.pushState(null, "", "/two-factor-auth/");

						// Extra check to set username after page load
						setTimeout(function () {
							const usernameField = document.getElementById("username");
							if (usernameField && window.twoFAUsername) {
								usernameField.value = window.twoFAUsername;
								console.log(
									"Username set after page load:",
									usernameField.value
								);
							}
						}, 200);
					});
			} else {
				// Sanitize the message using DOMPurify before setting content
				const messageElement = document.getElementById("login-form");
				const sanitizedMessage = DOMPurify.sanitize(response.message);

				messageElement.textContent = sanitizedMessage;
			}
		} catch (e) {
			console.error("Error from LOGIN JS Script :", e);
		}
	}
});