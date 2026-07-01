console.log("Citizen Portal SPA berhasil dimuat.");

let currentTab = "my_reports";
let currentPage = 1;
let editingReportId = null;

// =====================================================
// HELPER ELEMENT
// =====================================================
function getElementByAnyId(...ids) {
    for (const id of ids) {
        const element = document.getElementById(id);
        if (element) {
            return element;
        }
    }

    return null;
}

function getInputValue(...ids) {
    const element = getElementByAnyId(...ids);
    return element ? element.value : "";
}

function setInputValue(value, ...ids) {
    const element = getElementByAnyId(...ids);

    if (element) {
        element.value = value || "";
    }
}

// =====================================================
// LOAD DATA DASHBOARD CITIZEN
// =====================================================
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

    if (!result) {
        return;
    }

    if (result.status === 200) {
        const reports = result.data.results || [];

        renderList(reports);
        renderPagination(result.data);
        await loadSummaryStats();
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

// =====================================================
// RENDER LIST LAPORAN
// =====================================================
function renderList(reports) {
    const listContainer = document.getElementById("listContainer");

    if (!listContainer) {
        return;
    }

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
            <div class="col">
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
                            ${currentTab === "feed" ? "Warga Anonim" : (report.reporter_name || report.reporter || "Saya")}
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

// =====================================================
// PAGINATION
// =====================================================
function renderPagination(data) {
    const paginationContainer = document.getElementById("paginationContainer");

    if (!paginationContainer) {
        return;
    }

    const totalItems = data.count || 0;
    const pageSize = 10;
    const totalPages = Math.ceil(totalItems / pageSize) || 1;

    let html = `
        <nav aria-label="Pagination laporan">
            <ul class="pagination justify-content-center">
    `;

    html += `
        <li class="page-item ${currentPage <= 1 ? "disabled" : ""}">
            <button class="page-link" type="button"
                onclick="loadDashboardData('${currentTab}', ${currentPage - 1})">
                Sebelumnya
            </button>
        </li>
    `;

    for (let page = 1; page <= totalPages; page++) {
        html += `
            <li class="page-item ${currentPage === page ? "active" : ""}">
                <button class="page-link" type="button"
                    onclick="loadDashboardData('${currentTab}', ${page})">
                    ${page}
                </button>
            </li>
        `;
    }

    html += `
        <li class="page-item ${currentPage >= totalPages ? "disabled" : ""}">
            <button class="page-link" type="button"
                onclick="loadDashboardData('${currentTab}', ${currentPage + 1})">
                Berikutnya
            </button>
        </li>
    `;

    html += `
            </ul>
        </nav>
    `;

    paginationContainer.innerHTML = html;
}

// =====================================================
// TAB LAPORAN SAYA / FEED KOTA
// =====================================================
function switchTab(tab) {
    currentTab = tab;
    currentPage = 1;

    const myReportsTab = document.getElementById("myReportsTab");
    const feedTab = document.getElementById("tabFeedKota") || document.getElementById("feedTab");

    if (myReportsTab) {
        myReportsTab.classList.remove("active");
    }

    if (feedTab) {
        feedTab.classList.remove("active");
    }

    if (tab === "my_reports" && myReportsTab) {
        myReportsTab.classList.add("active");
    }

    if (tab === "feed" && feedTab) {
        feedTab.classList.add("active");
    }

    loadDashboardData(tab, 1);
}

// =====================================================
// STATUS HELPER
// =====================================================
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

// =====================================================
// SUMMARY STATUS
// =====================================================
async function loadSummaryStats() {
    const statusCard = document.querySelector(".status-card");

    if (statusCard && !statusCard.id) {
        statusCard.id = "summaryStats";
    }

    const result = await requestAPI(
        "/api/report/?tab=my_reports&page_size=1000",
        "GET"
    );

    if (!result || result.status !== 200) {
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

    const draftElement = document.getElementById("draftCount");
    const progressElement = document.getElementById("progressCount");
    const processElement = document.getElementById("processCount");
    const resolvedElement = document.getElementById("resolvedCount");

    if (draftElement) {
        draftElement.textContent = draftCount;
    }

    if (progressElement) {
        progressElement.textContent = progressCount;
    }

    if (processElement) {
        processElement.textContent = processCount;
    }

    if (resolvedElement) {
        resolvedElement.textContent = resolvedCount;
    }
}

// =====================================================
// MODAL BUAT LAPORAN
// =====================================================
function openCreateModal() {
    editingReportId = null;

    const modalTitle = document.getElementById("reportModalLabel");

    if (modalTitle) {
        modalTitle.textContent = "Buat Laporan Baru";
    }

    const reportForm = document.getElementById("reportForm");

    if (reportForm) {
        reportForm.reset();
    }

    const modalElement = document.getElementById("reportModal");

    if (modalElement) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
        modal.show();
    }
}

async function editDraft(id) {
    const result = await requestAPI(`/api/report/${id}/`, "GET");

    if (!result || result.status !== 200) {
        alert("Gagal mengambil data draft.");
        return;
    }

    const report = result.data;

    editingReportId = id;

    const modalTitle = document.getElementById("reportModalLabel");

    if (modalTitle) {
        modalTitle.textContent = "Edit Draft Laporan";
    }

    setInputValue(report.title, "inputTitle", "titleInput");
    setInputValue(report.category, "inputCategory", "categoryInput");
    setInputValue(report.location, "inputLocation", "locationInput");
    setInputValue(report.description, "inputDescription", "descriptionInput");

    const modalElement = document.getElementById("reportModal");

    if (modalElement) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
        modal.show();
    }
}

// =====================================================
// TUTUP MODAL SECARA AMAN
// =====================================================
function closeReportModal() {
    const modalElement = document.getElementById("reportModal");

    if (!modalElement) {
        return;
    }

    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    modal.hide();

    modalElement.classList.remove("show");
    modalElement.setAttribute("aria-hidden", "true");
    modalElement.removeAttribute("aria-modal");
    modalElement.style.display = "none";

    document.querySelectorAll(".modal-backdrop").forEach((backdrop) => {
        backdrop.remove();
    });

    document.body.classList.remove("modal-open");
    document.body.style.removeProperty("overflow");
    document.body.style.removeProperty("padding-right");
}

// =====================================================
// SUBMIT LAPORAN
// =====================================================
async function submitReport(status) {
    const payload = {
        title: getInputValue("inputTitle", "titleInput"),
        category: getInputValue("inputCategory", "categoryInput"),
        location: getInputValue("inputLocation", "locationInput"),
        description: getInputValue("inputDescription", "descriptionInput"),
        status: status,
    };

    const endpoint = editingReportId
        ? `/api/report/${editingReportId}/`
        : "/api/report/";

    const method = editingReportId ? "PUT" : "POST";

    const result = await requestAPI(endpoint, method, payload);

    if (result && (result.status === 200 || result.status === 201)) {
        closeReportModal();

        const reportForm = document.getElementById("reportForm");

        if (reportForm) {
            reportForm.reset();
        }

        editingReportId = null;

        await loadDashboardData(currentTab, currentPage);
        await loadSummaryStats();

        alert("Laporan berhasil disimpan sebagai " + status);
    } else {
        alert("Gagal menyimpan laporan.");
    }
}

// =====================================================
// EVENT TOMBOL MODAL
// =====================================================
function setupReportForm() {
    const draftButton = getElementByAnyId("btnDraft", "saveDraftBtn");
    const submitButton = getElementByAnyId("btnSubmit", "submitReportBtn");

    if (draftButton && !draftButton.dataset.bound) {
        draftButton.dataset.bound = "true";

        draftButton.addEventListener("click", function (event) {
            event.preventDefault();
            submitReport("DRAFT");
        });
    }

    if (submitButton && !submitButton.dataset.bound) {
        submitButton.dataset.bound = "true";

        submitButton.addEventListener("click", function (event) {
            event.preventDefault();
            submitReport("REPORTED");
        });
    }
}

document.addEventListener("DOMContentLoaded", function () {
    setupReportForm();
});

if (document.readyState !== "loading") {
    setupReportForm();
}