const loginForm = document.getElementById("login-form");

loginForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
        alert("Please fill in both fields.");
        return;
    }

    try {
        const response = await fetch("/auth/api/login", {   // <-- important
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await response.json();
        alert(data.message);

        if (data.success) {
            // optional: redirect somewhere later
            // window.location.href = "/";
        }

    } catch (err) {
        console.error(err);
        alert("Error: Could not connect to server.");
    }
});


const regForm = document.getElementById("register-form");

regForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const username = document.getElementById("reg-username").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    const confirmPassword = document.getElementById("reg-confirm-password").value;

    if (!username || !email || !password || !confirmPassword) {
        alert("Please fill in all fields.");
        return;
    }

    try {
        const response = await fetch("/auth/api/register", {   // <-- important
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
                confirm_password: confirmPassword
            })
        });

        const data = await response.json();
        alert(data.message);

        if (data.success) {
            // Switch to the Sign In tab
            wrapper.classList.remove("show-register");
            signInTab.classList.add("active");
            registerTab.classList.remove("active");
            signInForm.style.display = "block";
            registerForm.style.display = "none";
        }

    } catch (err) {
        console.error(err);
        alert("Error: Could not connect to server.");
    }
});
