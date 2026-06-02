const appContent = document.getElementById("app-content");

const routes = {
    login: `
        <section class="login-page">
            <div class="card login-card">
                <h3><i class="bi bi-box-arrow-in-right"></i> Login Citizen</h3>
                <p>Silakan login untuk masuk ke dashboard.</p>

                <form id="loginForm">
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" id="loginUsername" required>
                    </div>

                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" id="loginPassword" required>
                    </div>

                    <button type="submit">
                        <i class="bi bi-send"></i> Login
                    </button>
                </form>
            </div>
        </section>
    `,

    dashboard: `
        <section class="dashboard">
            <div class="card sidebar">
                <h4><i class="bi bi-person-circle"></i> Profil Warga</h4>
                <p>Nama: Citizen User</p>
                <p>Status: Aktif</p>
                <button onclick="logoutUser()">
                    <i class="bi bi-box-arrow-right"></i> Logout
                </button>
            </div>

            <div class="card main-content">
                <h3><i class="bi bi-speedometer2"></i> Dashboard Citizen</h3>
                <p>Selamat datang di Portal Citizen.</p>

                <div class="info-grid">
                    <div class="info-card">
                        <i class="bi bi-file-earmark-text"></i>
                        <h4>3</h4>
                        <p>Laporan Dibuat</p>
                    </div>

                    <div class="info-card">
                        <i class="bi bi-hourglass-split"></i>
                        <h4>1</h4>
                        <p>Sedang Diproses</p>
                    </div>

                    <div class="info-card">
                        <i class="bi bi-check-circle"></i>
                        <h4>2</h4>
                        <p>Selesai</p>
                    </div>
                </div>
            </div>

            <div class="card notification">
                <h4><i class="bi bi-bell"></i> Notifikasi</h4>
                <p>Belum ada notifikasi baru.</p>
            </div>
        </section>
    `
};

function handleRouting() {
    const hash = window.location.hash.replace("#", "") || "login";

    appContent.innerHTML = routes[hash] || routes.login;

    if (hash === "login" && typeof setupLoginForm === "function") {
        setupLoginForm();
    }
}

function logoutUser() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    alert("Logout berhasil!");
    window.location.hash = "#login";
}

window.addEventListener("hashchange", handleRouting);
window.addEventListener("DOMContentLoaded", handleRouting);