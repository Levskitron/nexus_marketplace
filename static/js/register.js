document.addEventListener("DOMContentLoaded", function() {
    
    // Get all the elements we need
    const wrapper = document.querySelector(".login-wrapper");
    const signInTab = document.getElementById("tab-signin");
    const registerTab = document.getElementById("tab-register");
    const signInForm = document.getElementById("form-container-signin");
    const registerForm = document.getElementById("form-container-register");

    // --- Tab Switching Logic ---

    // Listen for a click on the "Sign In" tab
    signInTab.addEventListener("click", function() {
        wrapper.classList.remove("show-register");
        signInTab.classList.add("active");
        registerTab.classList.remove("active");
        signInForm.style.display = "block";
        registerForm.style.display = "none";
    });

    // Listen for a click on the "Register" tab
    registerTab.addEventListener("click", function() {
        wrapper.classList.add("show-register");
        signInTab.classList.remove("active");
        registerTab.classList.add("active");
        signInForm.style.display = "none";
        registerForm.style.display = "block";
    });

    // ---------------------------------------------
    // VVV THIS IS THE NEW CODE VVV
    // ---------------------------------------------
    const regPassword = document.getElementById("reg-password");
    const confirmPasswordGroup = document.getElementById("confirm-password-group");

    // Listen for typing in the main password field
    regPassword.addEventListener("input", function() {
        if (regPassword.value.length > 0) {
            // If there's text, show the confirm field
            confirmPasswordGroup.style.display = "block";
        } else {
            // If the field is emptied, hide it again
            confirmPasswordGroup.style.display = "none";
        }
    });
    // ---------------------------------------------
    // ^^^ END OF NEW CODE ^^^
    // ---------------------------------------------


    // --- Form Submission Logic (from before) ---

    const loginForm = document.getElementById("login-form");
    loginForm.addEventListener("submit", function(event) {
        event.preventDefault(); 
        const username = document.getElementById("username").value;
        alert(`Attempting to sign in as: ${username}`);
    });

    const regForm = document.getElementById("register-form");
    regForm.addEventListener("submit", function(event) {
        event.preventDefault(); 
        const username = document.getElementById("reg-username").value;
        alert(`Attempting to register as: ${username}`);
    });

});