// Function to set the username in the form
function setUsernameInForm() {
	// Try to get username from Django template value first
	let usernameField = document.getElementById("username");
	let initialUsername = usernameField ? usernameField.value : "";

	// Then try sessionStorage if the field is empty
	if (!initialUsername) {
		const storedUsername = sessionStorage.getItem("2fa_username");
		console.log(
			"Looking for stored username in sessionStorage:",
			storedUsername
		);

		if (storedUsername && usernameField) {
			usernameField.value = storedUsername;
			initialUsername = storedUsername;
		}
	}

	// Finally, try the global variable set by login page
	if (!initialUsername && window.twoFAUsername) {
		console.log("Using username from global variable:", window.twoFAUsername);
		if (usernameField) {
			usernameField.value = window.twoFAUsername;
			initialUsername = window.twoFAUsername;
		}
	}

	// Update the display
	const usernameDisplay = document.getElementById("otp_verify");

	// ! DEBUG
	if (initialUsername && usernameField) {
		// console.log("Username set in form:", initialUsername);
		// if (usernameDisplay) {
		// 	usernameDisplay.textContent = `Verifying for account: ${initialUsername}`;
		// }
	} else {
		console.error("No username found in any source or field not found");
		if (usernameDisplay) {
			usernameDisplay.textContent =
				"Warning: No username found. Please go back to login.";
			usernameDisplay.className = "small text-danger mb-3";
		}
	}
}

// Try to set username when DOM content is loaded
document.addEventListener("DOMContentLoaded", function () {
	setUsernameInForm();
});

// Also try immediately in case script runs after DOM is already loaded
setTimeout(setUsernameInForm, 100); // Small delay to ensure DOM is ready

// Set the username again if the form is submitted
document.addEventListener("htmx:beforeRequest", function (evt) {
	if (evt.detail.requestConfig.path === "/auth/verify-2fa/") {
		// Ensure username is set before submission
		setUsernameInForm();

		// Log the form data being sent
		const form = evt.detail.elt;
		const formData = new FormData(form);
		console.log("2FA form submission - username:", formData.get("username"));
		console.log("2FA form submission - token:", formData.get("token"));
	}
});

document.addEventListener("htmx:beforeSwap", function (evt) {
	if (evt.detail.target.id === "login_error") {
		try {
			console.log("Réponse brute:", evt.detail.xhr.responseText);
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
						// Clear the stored username
						sessionStorage.removeItem("2fa_username");
						if (window.twoFAUsername) {
							delete window.twoFAUsername;
						}
						history.pushState(null, "", "/home/");
					});
			} else {
				// Display error message

				// Sanitize the message using DOMPurify before setting content
				const messageElement = document.getElementById("login_error");
				const sanitizedMessage = DOMPurify.sanitize(response.message);

				// Use textContent for plain text or innerHTML with sanitized content
				if (
					sanitizedMessage.includes("<") &&
					sanitizedMessage.includes(">")
				) {
					messageElement.innerHTML = sanitizedMessage;
				} else {
					messageElement.textContent = sanitizedMessage;
				}
			}
		} catch (e) {
			console.error("Erreur de traitement de la réponse:", e);
		}
	}
});