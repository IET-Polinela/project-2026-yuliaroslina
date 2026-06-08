console.log("Citizen Portal SPA berhasil dimuat.");

let currentTab = "my_reports";
let currentPage = 1;
let editingReportId = null;

async function loadDashboardData(tab = currentTab, page = currentPage) {
    currentTab = tab;
    currentPage = page;

    const result = await requestAPI(
        `/api/report/?tab=${currentTab}&page=${currentPage}`,
        "GET"
    );

    const listContainer = document.getElementById("listContainer");
    const paginationContainer = document.getElementById("paginationContainer");

    if (!listContainer) {
        return;
    }

    if (result.status === 200) {
        const reports = result.data.results || [];

        renderList(reports);
        renderPagination(result.data);
        loadSummaryStats();
    } else {
        listContainer.innerHTML = `
            <div class="alert alert-danger">
                Gagal memuat data laporan.
            </div>
        `;

        if (paginationContainer) {
            paginationContainer.innerHTML = "";
        }
    }
}

function renderList(reports) {
    const listContainer = document.getElementById("listContainer");

    if (reports.length === 0) {
        listContainer.innerHTML = `
            <div class="text-center text-muted py-5">
                Belum ada data laporan.
            </div>
        `;
        return;
    }

    listContainer.innerHTML = reports.map((report) => {
        const progress = getProgressValue(report.status);
        const statusText = formatStatus(report.status);

        return `
            <div class="report-card">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <span class="badge ${getStatusBadge(report.status)} px-3 py-2">
                        ${statusText}
                    </span>

                    <span class="report-category">
                        ${report.category}
                    </span>
                </div>

                <h5>${report.title}</h5>

                <p class="text-muted">
                    ${report.description}
                </p>

                <div class="report-meta-line">
                    <div>
                        <strong>Lokasi:</strong> ${report.location}
                    </div>

                    <div>
                        <strong>Oleh:</strong>
                        ${currentTab === "feed" ? "Warga Anonim" : report.reporter}
                    </div>
                </div>

                <div class="progress-label">
                    <span>Progress Laporan:</span>
                    <span class="text-primary">
                        ${statusText} (${progress}%)
                    </span>
                </div>

                <div class="progress mt-2">
                    <div class="progress-bar ${getProgressColor(report.status)}"
                        style="width: ${progress}%">
                    </div>
                </div>

                ${renderActionButton(report)}
            </div>
        `;
    }).join("");
}

function renderActionButton(report) {
    if (report.status === "DRAFT" && report.is_owner) {
        return `
            <button class="btn btn-warning w-100 mt-4"
                onclick="editDraft(${report.id})">
                <i class="bi bi-pencil-square"></i>
                Edit Draft
            </button>
        `;
    }

    return "";
}

function renderPagination(data) {
    const paginationContainer = document.getElementById("paginationContainer");

    if (!paginationContainer) {
        return;
    }

    let buttons = `
        <div class="d-flex justify-content-center align-items-center gap-2">
    `;

    if (data.previous) {
        buttons += `
            <button class="btn btn-outline-primary btn-sm"
                onclick="loadDashboardData('${currentTab}', ${currentPage - 1})">
                Sebelumnya
            </button>
        `;
    }

    buttons += `
        <span class="badge bg-primary px-3 py-2">
            Halaman ${currentPage}
        </span>
    `;

    if (data.next) {
        buttons += `
            <button class="btn btn-outline-primary btn-sm"
                onclick="loadDashboardData('${currentTab}', ${currentPage + 1})">
                Berikutnya
            </button>
        `;
    }

    buttons += `</div>`;

    paginationContainer.innerHTML = buttons;
}

function switchTab(tab) {
    currentTab = tab;
    currentPage = 1;

    document.getElementById("myReportsTab").classList.remove("active");
    document.getElementById("feedTab").classList.remove("active");

    if (tab === "my_reports") {
        document.getElementById("myReportsTab").classList.add("active");
    } else {
        document.getElementById("feedTab").classList.add("active");
    }

    loadDashboardData(tab, 1);
}

function getStatusBadge(status) {
    if (status === "DRAFT") {
        return "bg-secondary";
    }

    if (status === "REPORTED") {
        return "bg-warning text-dark";
    }

    if (status === "VERIFIED") {
        return "bg-info text-dark";
    }

    if (status === "IN_PROGRESS") {
        return "bg-primary";
    }

    if (status === "RESOLVED") {
        return "bg-success";
    }

    return "bg-dark";
}

function getProgressColor(status) {
    if (status === "DRAFT") {
        return "bg-secondary";
    }

    if (status === "REPORTED") {
        return "bg-warning";
    }

    if (status === "VERIFIED") {
        return "bg-info";
    }

    if (status === "IN_PROGRESS") {
        return "bg-primary";
    }

    if (status === "RESOLVED") {
        return "bg-success";
    }

    return "bg-dark";
}

function formatStatus(status) {
    if (status === "DRAFT") {
        return "DRAFT";
    }

    if (status === "REPORTED") {
        return "Diajukan";
    }

    if (status === "VERIFIED") {
        return "Diverifikasi";
    }

    if (status === "IN_PROGRESS") {
        return "Diproses";
    }

    if (status === "RESOLVED") {
        return "Selesai";
    }

    return status;
}

function getProgressValue(status) {
    if (status === "DRAFT") {
        return 10;
    }

    if (status === "REPORTED") {
        return 25;
    }

    if (status === "VERIFIED") {
        return 50;
    }

    if (status === "IN_PROGRESS") {
        return 75;
    }

    if (status === "RESOLVED") {
        return 100;
    }

    return 0;
}

async function loadSummaryStats() {
    const result = await requestAPI(
        "/api/report/?tab=my_reports&page_size=1000",
        "GET"
    );

    if (result.status !== 200) {
        return;
    }

    const reports = result.data.results || [];

    const draftCount = reports.filter(
        (report) => report.status === "DRAFT"
    ).length;

    const progressCount = reports.filter(
        (report) =>
            report.status === "REPORTED" ||
            report.status === "VERIFIED"
    ).length;

    const processCount = reports.filter(
        (report) => report.status === "IN_PROGRESS"
    ).length;

    const resolvedCount = reports.filter(
        (report) => report.status === "RESOLVED"
    ).length;

    document.getElementById("draftCount").textContent = draftCount;
    document.getElementById("progressCount").textContent = progressCount;

    const processElement = document.getElementById("processCount");
    if (processElement) {
        processElement.textContent = processCount;
    }

    document.getElementById("resolvedCount").textContent = resolvedCount;
}

function openCreateModal() {
    editingReportId = null;

    document.getElementById("reportModalLabel").textContent =
        "Tambah Laporan Baru";

    document.getElementById("reportForm").reset();

    const modal = new bootstrap.Modal(
        document.getElementById("reportModal")
    );

    modal.show();
}

async function editDraft(id) {
    const result = await requestAPI(`/api/report/${id}/`, "GET");

    if (result.status !== 200) {
        alert("Gagal mengambil data draft.");
        return;
    }

    const report = result.data;

    editingReportId = id;

    document.getElementById("reportModalLabel").textContent =
        "Edit Draft Laporan";

    document.getElementById("titleInput").value = report.title;
    document.getElementById("categoryInput").value = report.category;
    document.getElementById("locationInput").value = report.location;
    document.getElementById("descriptionInput").value = report.description;

    const modal = new bootstrap.Modal(
        document.getElementById("reportModal")
    );

    modal.show();
}

async function submitReport(status) {
    const payload = {
        title: document.getElementById("titleInput").value,
        category: document.getElementById("categoryInput").value,
        location: document.getElementById("locationInput").value,
        description: document.getElementById("descriptionInput").value,
        status: status,
    };

    const endpoint = editingReportId
        ? `/api/report/${editingReportId}/`
        : "/api/report/";

    const method = editingReportId ? "PUT" : "POST";

    const result = await requestAPI(endpoint, method, payload);

    if (result.status === 200 || result.status === 201) {
        const modalElement = document.getElementById("reportModal");
        const modal = bootstrap.Modal.getInstance(modalElement);

        modal.hide();

        document.getElementById("reportForm").reset();
        editingReportId = null;

        loadDashboardData(currentTab, currentPage);
        alert("Laporan berhasil disimpan.");
    } else {
        alert("Gagal menyimpan laporan.");
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const saveDraftBtn = document.getElementById("saveDraftBtn");
    const submitReportBtn = document.getElementById("submitReportBtn");

    if (saveDraftBtn) {
        saveDraftBtn.addEventListener("click", function () {
            submitReport("DRAFT");
        });
    }

    if (submitReportBtn) {
        submitReportBtn.addEventListener("click", function () {
            submitReport("REPORTED");
        });
    }
});