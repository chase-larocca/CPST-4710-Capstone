document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("forgot-password-link").addEventListener("click", function (event) {
        event.preventDefault(); // Prevent default link behavior

        // Ask user for their email
        const email = prompt("Enter your email to reset password:");

        if (!email || !email.includes("@")) {
            alert("Please enter a valid email address.");
            return;
        }

        // Send request to backend
        fetch("/api/forgot-password", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert("If this email is associated with an account, you will receive a reset link.");
            } else {
                alert(result.error || "Something went wrong.");
            }
        })
        .catch(error => {
            console.error("Error sending password reset request:", error);
            alert("Oops, something went wrong.");
        });
    });
});
