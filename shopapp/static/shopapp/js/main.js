/* =========================
   THEME TOGGLE (GLOBAL)
   ========================= */

const themeToggle = document.getElementById("themeToggle");

// Apply saved theme on page load
const savedTheme = localStorage.getItem("theme");
if (savedTheme === "light") {
    document.body.classList.add("light");
}

// Toggle theme on click
if (themeToggle) {
    themeToggle.addEventListener("click", () => {
        document.body.classList.toggle("light");

        const currentTheme = document.body.classList.contains("light")
            ? "light"
            : "dark";

        localStorage.setItem("theme", currentTheme);
    });
}

/* =========================
   TRENDING PRODUCTS (HOME)
   ========================= */

const trendingContainer = document.getElementById("trending-container");

if (trendingContainer) {
    trendingContainer.innerHTML = "<p>Loading…</p>";

    fetch("/api/trending/")
        .then(res => res.json())
        .then(products => {
            trendingContainer.innerHTML = "";

            if (!products || products.length === 0) {
                trendingContainer.innerHTML = "<p>No trending products.</p>";
                return;
            }

            products.forEach(p => {
                const card = document.createElement("div");
                card.className = "card";
                card.innerHTML = `<h3>${p.title}</h3>`;
                card.onclick = () => {
                    window.location.href = `/product/${p.id}/`;
                };
                trendingContainer.appendChild(card);
            });
        })
        .catch(() => {
            trendingContainer.innerHTML = "<p>Failed to load trending products.</p>";
        });
}

/* =========================
   SEARCH RESULTS (SEARCH PAGE)
   ========================= */

const resultsContainer = document.getElementById("results-container");

if (resultsContainer) {
    const params = new URLSearchParams(window.location.search);
    const query = params.get("q");

    if (!query || query.trim() === "") {
        resultsContainer.innerHTML = "<p>Please enter a search query.</p>";
    } else {
        resultsContainer.innerHTML = "<p>Loading…</p>";

        fetch(`/api/search/?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                resultsContainer.innerHTML = "";

                if (!data.results || data.results.length === 0) {
                    resultsContainer.innerHTML = "<p>No results found.</p>";
                    return;
                }

                data.results.forEach(p => {
                    const card = document.createElement("div");
                    card.className = "card";
                    card.innerHTML = `<h3>${p.title}</h3>`;
                    card.onclick = () => {
                        window.location.href = `/product/${p.id}/`;
                    };
                    resultsContainer.appendChild(card);
                });
            })
            .catch(() => {
                resultsContainer.innerHTML = "<p>Search failed.</p>";
            });
    }
}

/* =========================
   PRODUCT PAGE LOGIC
   ========================= */

// These elements only exist on product page
const productTitle = document.getElementById("product-title");
const comparisonList = document.getElementById("comparison-list");
const prosList = document.getElementById("pros-list");
const consList = document.getElementById("cons-list");
const aiVerdict = document.getElementById("ai-verdict");

// `productId` is injected inline in product.html
if (typeof productId !== "undefined") {

    // Fetch price comparison
    fetch(`/api/compare/${productId}/`)
        .then(res => res.json())
        .then(data => {
            if (productTitle) {
                productTitle.innerText = data.product;
            }

            if (comparisonList) {
                comparisonList.innerHTML = "";

                if (!data.comparisons || data.comparisons.length === 0) {
                    comparisonList.innerHTML = "<p>No listings available.</p>";
                } else {
                    data.comparisons.forEach(item => {
                        const row = document.createElement("div");
                        row.className = "compare-row";
                        row.innerHTML = `
                            <span>${item.platform}</span>
                            <span>₹ ${item.price}</span>
                            <a href="${item.url}">Buy</a>
                        `;
                        comparisonList.appendChild(row);
                    });
                }
            }
        })
        .catch(() => {
            if (comparisonList) {
                comparisonList.innerHTML = "<p>Failed to load comparison.</p>";
            }
        });

    // Fetch AI insights
    fetch(`/api/insights/${productId}/`)
        .then(res => res.json())
        .then(data => {
            if (prosList) {
                prosList.innerHTML = data.pros.map(p => `<li>${p}</li>`).join("");
            }

            if (consList) {
                consList.innerHTML = data.cons.map(c => `<li>${c}</li>`).join("");
            }

            if (aiVerdict) {
                aiVerdict.innerText = data.verdict || "—";
            }
        })
        .catch(() => {
            if (aiVerdict) {
                aiVerdict.innerText = "Insights unavailable.";
            }
        });
}
