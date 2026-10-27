const registerForm = document.getElementById("registerForm");

const password = document.getElementById("password");
const confirmPassword = document.getElementById("confirmPassword");

const togglePassword = document.getElementById("togglePassword");

const strengthBar = document.getElementById("strengthBar");
const strengthText = document.getElementById("strengthText");


/* SHOW / HIDE PASSWORD */

togglePassword.addEventListener("click", () => {

    if (password.type === "password") {

        password.type = "text";

        togglePassword.innerHTML =
            '<i class="fa-solid fa-eye-slash"></i>';

    } else {

        password.type = "password";

        togglePassword.innerHTML =
            '<i class="fa-solid fa-eye"></i>';

    }

});


/* PASSWORD STRENGTH */

password.addEventListener("input", () => {

    const value = password.value;

    let score = 0;

    if (value.length >= 8) {
        score++;
    }

    if (/[A-Z]/.test(value)) {
        score++;
    }

    if (/[0-9]/.test(value)) {
        score++;
    }

    if (/[^A-Za-z0-9]/.test(value)) {
        score++;
    }


    if (value.length === 0) {

        strengthBar.style.width = "0%";
        strengthText.textContent = "Password strength";

    }

    else if (score <= 1) {

        strengthBar.style.width = "25%";
        strengthText.textContent = "Weak password";

    }

    else if (score === 2) {

        strengthBar.style.width = "50%";
        strengthText.textContent = "Medium password";

    }

    else if (score === 3) {

        strengthBar.style.width = "75%";
        strengthText.textContent = "Good password";

    }

    else {

        strengthBar.style.width = "100%";
        strengthText.textContent = "Strong password";

    }

});


/* FORM SUBMIT */
registerForm.addEventListener("submit", (event) => {

    event.preventDefault();

    const fullName =
        document.getElementById("fullName").value.trim();

    const phone =
        document.getElementById("phone").value.trim();

    const email =
        document.getElementById("email").value.trim();

    const confirmPasswordValue =
        confirmPassword.value;


    if (fullName.length < 3) {
        alert("Please enter your full name.");
        return;
    }


    if (!/^[0-9]{10}$/.test(phone)) {
        alert("Please enter a valid 10-digit mobile number.");
        return;
    }


    if (password.value.length < 8) {
        alert("Password must contain at least 8 characters.");
        return;
    }


    if (password.value !== confirmPasswordValue) {
        alert("Passwords do not match.");
        return;
    }


    const terms = document.getElementById("terms");

    if (!terms.checked) {
        alert("Please accept the Terms & Conditions.");
        return;
    }


    alert("Registration successful! Please login.");

    window.location.href = "/login";

});