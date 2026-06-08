const appContent = document.getElementById("app-content");

const routes = {
    login: `
        <section class="login-page">
            <div class="card login-card shadow-lg border-0">
                <div class="text-center mb-4">
                    <i class="bi bi-buildings-fill text-primary" style="font-size: 3.2rem;"></i>
                    <h2 class="fw-bold mt-3 mb-2">Citizen Portal</h2>
                    <p class="text-muted mb-0">
                        Masuk untuk mengelola laporan warga.
                    </p>
                </div>

                <form id="loginForm">
                    <div class="mb-3">
                        <label for="loginUsername" class="form-label fw-semibold">Username</label>
                        <input type="text" class="form-control form-control-lg"
                            id="loginUsername" placeholder="Masukkan username" required>
                    </div>

                    <div class="mb-4">
                        <label for="loginPassword" class="form-label fw-semibold">Password</label>
                        <input type="password" class="form-control form-control-lg"
                            id="loginPassword" placeholder="Masukkan password" required>
                    </div>

                    <button type="submit" class="btn btn-primary btn-lg w-100">
                        <i class="bi bi-box-arrow-in-right"></i>
                        Login
                    </button>
                </form>
            </div>
        </section>
    `,

    dashboard: `
        <section class="dashboard dashboard-style-grid">

            <aside class="left-panel">
                <button type="button"
                    class="create-report-box"
                    onclick="openCreateModal()">
                    <i class="bi bi-plus-circle"></i>
                    <span>Buat</span>
                    <span>Laporan</span>
                    <span>Baru</span>
                </button>

                <div class="status-card">
                    <h6>
                        <i class="bi bi-activity"></i>
                        STATUS LAPORAN ANDA
                    </h6>

                    <div class="status-row">
                        <span>
                            <i class="bi bi-pencil-square text-secondary"></i>
                            Draf
                        </span>
                        <span class="status-badge bg-secondary" id="draftCount">0</span>
                    </div>

                    <div class="status-row">
                        <span>
                            <i class="bi bi-send-fill text-warning"></i>
                            Diajukan
                        </span>
                        <span class="status-badge bg-warning text-dark" id="progressCount">0</span>
                    </div>

                    <div class="status-row">
                        <span>
                            <i class="bi bi-gear-fill text-info"></i>
                            Diproses
                        </span>
                        <span class="status-badge bg-info text-dark" id="processCount">0</span>
                    </div>

                    <div class="status-row">
                        <span>
                            <i class="bi bi-check-circle-fill text-success"></i>
                            Selesai
                        </span>
                        <span class="status-badge bg-success" id="resolvedCount">0</span>
                    </div>
                </div>

                <button type="button" class="btn btn-outline-danger w-100 mt-3" onclick="logoutUser()">
                    <i class="bi bi-box-arrow-right"></i>
                    Logout
                </button>
            </aside>

            <main class="main-panel">
                <div class="top-dashboard-bar">
                    <ul class="nav nav-tabs custom-tabs">
                        <li class="nav-item">
                            <button type="button" class="nav-link active" id="myReportsTab"
                                onclick="switchTab('my_reports')">
                                <i class="bi bi-folder-fill"></i>
                                Laporan Saya
                            </button>
                        </li>

                        <li class="nav-item">
                            <button type="button" class="nav-link" id="feedTab"
                                onclick="switchTab('feed')">
                                <i class="bi bi-globe-asia-australia"></i>
                                Feed Kota (Publik)
                            </button>
                        </li>
                    </ul>
                </div>

                <div id="listContainer" class="report-grid">
                    <div class="text-center text-muted py-5">
                        Memuat data laporan...
                    </div>
                </div>

                <div id="paginationContainer" class="mt-4"></div>
            </main>

        </section>
    `
};

function handleRouting() {
    const hash = window.location.hash.replace("#", "") || "login";

    appContent.innerHTML = routes[hash] || routes.login;

    if (hash === "login" && typeof setupLoginForm === "function") {
        setupLoginForm();
    }

    if (hash === "dashboard" && typeof loadDashboardData === "function") {
        loadDashboardData("my_reports", 1);
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
window.addEventListener("DOMContentLoaded", () => {
    const username = localStorage.getItem("username");

    const navbarUser = document.getElementById("navbarUser");

    if (navbarUser && username) {
        navbarUser.innerHTML =
            `<i class="bi bi-person-circle"></i> Halo, ${username} 👋`;
    }
});