document.addEventListener("DOMContentLoaded", function() {

    // Elements used for tab switching
    const wrapper = document.querySelector(".login-wrapper");
    const signInTab = document.getElementById("tab-signin");
    const registerTab = document.getElementById("tab-register");
    const signInForm = document.getElementById("form-container-signin");
    const registerForm = document.getElementById("form-container-register");

    // Tab switching logic
    signInTab.addEventListener("click", function() {
        wrapper.classList.remove("show-register");
        signInTab.classList.add("active");
        registerTab.classList.remove("active");
        signInForm.style.display = "block";
        registerForm.style.display = "none";
    });

    registerTab.addEventListener("click", function() {
        wrapper.classList.add("show-register");
        signInTab.classList.remove("active");
        registerTab.classList.add("active");
        signInForm.style.display = "none";
        registerForm.style.display = "block";
    });


    // Show confirm password box when typing
    const regPassword = document.getElementById("reg-password");
    const confirmPasswordGroup = document.getElementById("confirm-password-group");

    regPassword.addEventListener("input", function() {
        if (regPassword.value.length > 0) {
            confirmPasswordGroup.style.display = "block";
        } else {
            confirmPasswordGroup.style.display = "none";
        }
    });



    // LOGIN FORM SUBMISSION
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
            const response = await fetch("/auth/api/login", {
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
                // Redirect later (for now it's fine)
                // window.location.href = "/";
            }

        } catch (err) {
            console.error(err);
            alert("Error: Could not connect to server.");
        }
    });



    // REGISTER FORM SUBMISSION
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
            const response = await fetch("/auth/api/register", {
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
                // Switch back to login tab
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

});
