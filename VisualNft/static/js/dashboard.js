async function fetchData(endpoint) {
    const response = await fetch(endpoint);
    const data = await response.json();
    return data;
}

async function updateCharts() {
    const nftData = await fetchData("/api/nftData");
    const userData = await fetchData("/api/userData");

    const nftLabels = nftData.labels;
    const nftCounts = nftData.counts;

    const userLabels = userData.labels;
    const userCounts = userData.counts;

    const nftChartCanvas = document.getElementById("nftChart").getContext("2d");
    const userChartCanvas = document.getElementById("userChart").getContext("2d");

    new Chart(nftChartCanvas, {
        type: "bar",
        data: {
            labels: nftLabels,
            datasets: [{
                label: "Number of NFT Items",
                data: nftCounts,
                backgroundColor: "rgba(75, 192, 192, 0.7)",
            }],
        },
    });

    new Chart(userChartCanvas, {
        type: "bar",
        data: {
            labels: userLabels,
            datasets: [{
                label: "Number of Users",
                data: userCounts,
                backgroundColor: "rgba(255, 99, 132, 0.7)",
            }],
        },
    });
}

window.onload = updateCharts;
