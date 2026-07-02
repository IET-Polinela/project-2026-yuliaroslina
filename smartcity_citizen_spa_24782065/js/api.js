const API_BASE_URL = "http://103.151.63.87:8002";

function handleUnauthorized() {
    alert("Sesi Anda telah habis atau Anda belum login.");

    localStorage.clear();

    window.location.hash = "#login";

    return null;
}

async function requestAPI(endpoint, method = "GET", data = null) {
    const accessToken = localStorage.getItem("access_token");

    const headers = {
        "Content-Type": "application/json",
    };

    if (accessToken) {
        headers["Authorization"] = "Bearer " + accessToken;
    }

    const options = {
        method: method,
        headers: headers,
    };

    if (data !== null) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(API_BASE_URL + endpoint, options);

        if (response.status === 401) {
            return handleUnauthorized();
        }

        let responseData = null;

        try {
            responseData = await response.json();
        } catch (error) {
            responseData = null;
        }

        return {
            status: response.status,
            data: responseData,
        };
    } catch (error) {
        console.error("Request API gagal:", error);

        return {
            status: 0,
            data: null,
        };
    }
}