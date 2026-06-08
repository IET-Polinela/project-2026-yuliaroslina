function setupLoginForm() {
    const loginForm = document.getElementById("loginForm");

    if (!loginForm) {
        return;
    }

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = document.getElementById("loginUsername").value;
        const password = document.getElementById("loginPassword").value;

        const result = await requestAPI("/api/token/", "POST", {
            username: username,
            password: password,
        });

        if (result.status === 200) {
            localStorage.setItem("access_token", result.data.access);
            localStorage.setItem("refresh_token", result.data.refresh);
            localStorage.setItem("username", username);

            alert("Login berhasil!");
            window.location.hash = "#dashboard";
            location.reload();
        } else {
            alert("Login gagal. Periksa username dan password.");
        }
    });
}