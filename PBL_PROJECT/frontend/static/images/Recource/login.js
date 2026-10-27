const loginForm = document.getElementById("loginForm");

loginForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    const response = await fetch("/api/login", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            email: email,
            password: password
        })

    });

    const data = await response.json();

    if (!response.ok) {

        alert(data.message);
        return;

    }

    if (data.role === "patient") {

        window.location.href = "/patient/dashboard";

    }

    else if (data.role === "doctor") {

        window.location.href = "/doctor/dashboard";

    }

});