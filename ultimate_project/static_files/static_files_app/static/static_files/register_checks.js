function registerChecks() {
	const firstNameInput = document.getElementById("first_name");
	const lastNameInput = document.getElementById("last_name");
	const usernameInput = document.getElementById("username");
	const emailInput = document.getElementById("email");
	const passwordInput = document.getElementById("password");
	const repeatPasswordInput = document.getElementById("repeat_password");
	const emailError = document.getElementById("email-error");
	const passwordError = document.getElementById("password-error");
	const registerButton = document.getElementById("register-button");
	const form = document.querySelector("form.user");
	const strengthBar = document.getElementById("password-strength-bar");
	const strengthText = document.getElementById("password-strength-text");

	// Email validation function
	function validateEmail(email) {
		// Regex for email validation
		const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
		return re.test(String(email).toLowerCase());
	}

	// Password strength evaluation function
	function evaluatePasswordStrength(password) {
		if (!password) return { score: 0, message: "Not entered", percentage: 0 };

		let score = 0;
		const messages = ["Very weak", "Weak", "Medium", "Strong", "Very strong"];

		// Length check
		if (password.length > 7) score += 1;
		if (password.length > 10) score += 1;

		// Character diversity checks
		if (/[a-z]/.test(password)) score += 1; // lowercase
		if (/[A-Z]/.test(password)) score += 1; // uppercase
		if (/[0-9]/.test(password)) score += 1; // numbers
		if (/[^a-zA-Z0-9]/.test(password)) score += 1; // special chars

		// Cap the score at 4
		score = Math.min(4, score);

		// Map score to percentage for the progress bar
		const percentage = (score / 4) * 100;

		return {
			score: score,
			percentage: percentage,
			message: messages[score]
		};
	}

	// Update password strength indicator
	function updatePasswordStrength() {
		const password = passwordInput.value;
		const strength = evaluatePasswordStrength(password);

		// Update the progress bar
		strengthBar.style.width = strength.percentage + "%";
		strengthBar.setAttribute("aria-valuenow", strength.percentage);

		// Update color based on strength
		strengthBar.className = "progress-bar";
		if (password === "") {
			// When password is empty, ensure the bar is completely empty
			strengthBar.style.width = "0%";
			strengthBar.setAttribute("aria-valuenow", 0);
		} else if (strength.score === 0) {
			strengthBar.classList.add("bg-secondary");
		} else if (strength.score === 1) {
			strengthBar.classList.add("bg-danger");
		} else if (strength.score === 2) {
			strengthBar.classList.add("bg-warning");
		} else if (strength.score === 3) {
			strengthBar.classList.add("bg-info");
		} else {
			strengthBar.classList.add("bg-success");
		}

		// Update text
		strengthText.textContent = "Password strength: " + strength.message;
	}

	// Check if passwords match
	function checkPasswords() {
		if (passwordInput.value && repeatPasswordInput.value) {
			if (passwordInput.value !== repeatPasswordInput.value) {
				passwordError.style.display = "block";
				return false;
			} else {
				passwordError.style.display = "none";
				return true;
			}
		}
		return passwordInput.value === repeatPasswordInput.value;
	}

	// Validate the entire form and enable/disable the register button
	function validateForm() {
		const isFirstNameValid = firstNameInput.value.trim() !== "";
		const isLastNameValid = lastNameInput.value.trim() !== "";
		const isUsernameValid = usernameInput.value.trim() !== "";
		const isEmailValid = emailInput.value && validateEmail(emailInput.value);
		const isPasswordValid = passwordInput.value.trim() !== "";
		const doPasswordsMatch = checkPasswords();

		// Update email validation visual state
		if (emailInput.value && !isEmailValid) {
			emailInput.classList.add("is-invalid");
		} else {
			emailInput.classList.remove("is-invalid");
		}

		const isFormValid =
			isFirstNameValid &&
			isLastNameValid &&
			isUsernameValid &&
			isEmailValid &&
			isPasswordValid &&
			doPasswordsMatch;

		// Disable the register button is the full form is not valid
		registerButton.disabled = !isFormValid;
		return isFormValid;
	}

	// Add input event listeners to all required fields
	firstNameInput.addEventListener("input", validateForm);
	lastNameInput.addEventListener("input", validateForm);
	usernameInput.addEventListener("input", validateForm);

	emailInput.addEventListener("input", function () {
		if (emailInput.value && !validateEmail(emailInput.value)) {
			emailError.style.display = "block";
			emailInput.classList.add("is-invalid");
		} else {
			emailError.style.display = "none";
			emailInput.classList.remove("is-invalid");
		}
		validateForm();
	});

	passwordInput.addEventListener("input", function () {
		updatePasswordStrength();
		checkPasswords();
		validateForm();
	});

	repeatPasswordInput.addEventListener("input", function () {
		checkPasswords();
		validateForm();
	});
}