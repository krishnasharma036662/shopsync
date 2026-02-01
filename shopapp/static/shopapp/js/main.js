document.addEventListener("DOMContentLoaded", () => {

    /* ================= THEME ================= */

    if (!localStorage.getItem("theme")) {
        localStorage.setItem("theme", "dark");
    }

    if (localStorage.getItem("theme") === "light") {
        document.body.classList.add("light");
    }

    const toggle = document.getElementById("themeToggle");
    if (toggle) {
        toggle.onclick = () => {
            document.body.classList.toggle("light");
            localStorage.setItem(
                "theme",
                document.body.classList.contains("light") ? "light" : "dark"
            );
        };
    }

    /* ================= PRICE FORMAT ================= */

    window.formatPrice = (v) => {
        if (!v || v <= 0) return "";
        return `₹ ${Number(v).toLocaleString("en-IN")}`;
    };

    /* ================= HOME – TRENDING ================= */

    const trending = document.getElementById("trending-container");
    if (trending) {
        fetch("/api/trending/")
            .then(r => r.json())
            .then(items => {
                trending.innerHTML = "";
                items.slice(0, 3).forEach(p => {
                    const card = document.createElement("div");
                    card.className = "card";
                    card.innerHTML = `
                        <img src="${p.image || '/static/shopapp/img/placeholder.png'}">
                        <h3>${p.title}</h3>
                        <div class="price">
                            ${formatPrice(p.price)}
                            ${p.old_price ? `<del>${formatPrice(p.old_price)}</del>` : ""}
                        </div>
                    `;
                    card.onclick = () => location.href = `/product/${p.id}/`;
                    trending.appendChild(card);
                });
            });
    }

    /* ================= SEARCH ================= */

    const results = document.getElementById("results-container");
    if (results) {
        const q = new URLSearchParams(location.search).get("q");
        fetch(`/api/search/?q=${encodeURIComponent(q)}`)
            .then(r => r.json())
            .then(d => {
                results.innerHTML = "";
                d.results.forEach(p => {
                    const card = document.createElement("div");
                    card.className = "result-card";
                    card.innerHTML = `
                        <div class="result-img">
                            <img src="${p.image || ''}">
                        </div>
                        <div class="result-content">
                            <div>
                                <div class="result-title">${p.title}</div>
                                <div class="result-sub">${p.description || ""}</div>
                            </div>
                            <div class="price-row">
                                <div class="price">${formatPrice(p.price)}</div>
                                ${p.old_price ? `<div class="old-price">${formatPrice(p.old_price)}</div>` : ""}
                            </div>
                        </div>
                    `;
                    card.onclick = () => location.href = `/product/${p.id}/`;
                    results.appendChild(card);
                });
            });
    }
});

/* ================= PRODUCT PAGE (RUN AFTER EVERYTHING) ================= */

window.addEventListener("load", () => {

    if (typeof productId === "undefined") return;

    /* PRICE COMPARISON */
    fetch(`/api/compare/${productId}/`)
        .then(r => r.json())
        .then(d => {
            document.getElementById("product-title").innerText = d.product;
            if (d.image) document.getElementById("product-image").src = d.image;

            const list = document.getElementById("comparison-list");
            list.innerHTML = "";
            d.comparisons.forEach(i => {
                list.innerHTML += `
                    <div class="compare-row">
                        <span>${i.platform}</span>
                        <span>${formatPrice(i.price)}</span>
                        <a href="/api/redirect/${i.listing_id}/">Buy</a>
                    </div>
                `;
            });
        });

    /* 🔥 AI INSIGHTS */
    fetch(`/api/insights/${productId}/`)
        .then(r => r.json())
        .then(ai => {

            const pros = document.getElementById("pros-list");
            pros.innerHTML = "";
            ai.pros.forEach(p => pros.innerHTML += `<li>${p}</li>`);

            const cons = document.getElementById("cons-list");
            cons.innerHTML = "";
            ai.cons.forEach(c => cons.innerHTML += `<li>${c}</li>`);

            document.getElementById("ai-verdict").innerText = ai.verdict || "—";

            document.querySelector(".deal-score").innerText =
                ai.deal_score !== undefined ? ai.deal_score : "—";

            document.querySelector(".side-box strong").innerText =
                ai.best_time_to_buy || "MONITOR";
        });

    /* ================= PRICE HISTORY GRAPH (ADDED) ================= */

    const chartCanvas = document.getElementById("priceChart");
    if (!chartCanvas) return;

    const loadChartJS = () => new Promise(resolve => {
        if (window.Chart) return resolve();
        const s = document.createElement("script");
        s.src = "https://cdn.jsdelivr.net/npm/chart.js";
        s.onload = resolve;
        document.head.appendChild(s);
    });

    loadChartJS().then(() => {
        fetch(`/api/price-trend/${productId}/`)
            .then(r => r.json())
            .then(d => {

                if (!d.dates || d.dates.length < 2) {
                    chartCanvas.parentElement.innerHTML +=
                        "<p style='margin-top:10px;opacity:.6'>Not enough price data yet.</p>";
                    return;
                }

                new Chart(chartCanvas, {
                    type: "line",
                    data: {
                        labels: d.dates,
                        datasets: [{
                            label: "Price (₹)",
                            data: d.prices,
                            borderColor: "#2563eb",
                            backgroundColor: "rgba(37,99,235,0.15)",
                            tension: 0.3,
                            fill: true,
                            pointRadius: 3
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: {
                                ticks: {
                                    callback: v => `₹ ${v.toLocaleString("en-IN")}`
                                }
                            }
                        }
                    }
                });
            });
    });
});
