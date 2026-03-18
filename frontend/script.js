const API_BASE_URL = "https://87ulvr65i0.execute-api.us-east-1.amazonaws.com";
const DEFAULT_LIMIT = 25;
const DEFAULT_SORT = "price";
const DEFAULT_DIRECTION = "desc";

const searchInput = document.getElementById("player-search");
const searchButton = document.getElementById("search-button");
const loadButton = document.getElementById("load-button");
const sortSelect = document.getElementById("sort-select");
const limitSelect = document.getElementById("limit-select");
const statusMessage = document.getElementById("status-message");
const cardsContainer = document.getElementById("cards-container");
const topGainersContainer = document.getElementById("top-gainers");
const topLosersContainer = document.getElementById("top-losers");
const highestVolumeContainer = document.getElementById("highest-volume");

function escapeForSingleQuotedJs(value) {
  return String(value ?? "")
    .replace(/\\/g, "\\\\")
    .replace(/'/g, "\\'");
}

function formatPrice(value) {
  const amount = Number(value);
  if (Number.isNaN(amount)) {
    return "Price unavailable";
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

function formatDate(value) {
  if (!value || value.length !== 8) {
    return value || "Unknown date";
  }

  const year = value.slice(0, 4);
  const month = value.slice(4, 6);
  const day = value.slice(6, 8);
  return `${month}/${day}/${year}`;
}

function formatPercent(value) {
  const amount = Number(value);
  if (Number.isNaN(amount)) {
    return "N/A";
  }

  return `${amount.toFixed(2)}%`;
}

function formatNumber(value) {
  const amount = Number(value);
  if (Number.isNaN(amount)) {
    return "N/A";
  }

  return new Intl.NumberFormat("en-US").format(amount);
}

function getSelectedSort() {
  const [sort, direction] = sortSelect.value.split(":");
  return {
    sort: sort || DEFAULT_SORT,
    direction: direction || DEFAULT_DIRECTION,
  };
}

async function requestCards(params = {}) {
  const url = new URL(`${API_BASE_URL}/cards`);

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  });

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }

  return response.json();
}

async function getAIInsight(player) {
  const url = `${API_BASE_URL}/recommendations?player=${encodeURIComponent(player)}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    alert(data.insight);
  } catch (err) {
    alert("Failed to load AI insight");
  }
}

window.getAIInsight = getAIInsight;

function renderCards(items) {
  cardsContainer.innerHTML = "";

  if (!items.length) {
    cardsContainer.innerHTML = `
      <article class="empty-state">
        <h2>No cards found</h2>
        <p>Try a different player search or change the sorting controls.</p>
      </article>
    `;
    return;
  }

  cardsContainer.innerHTML = items.map((item) => `
    <article class="card">
      <p class="card-player">${item.player || "Unknown Player"}</p>
      <h2 class="card-name">${item.card_name || "Unnamed Card"}</h2>
      <dl class="card-meta">
        <div>
          <dt>Price</dt>
          <dd>${formatPrice(item.price)}</dd>
        </div>
        <div>
          <dt>Date</dt>
          <dd>${formatDate(item.date)}</dd>
        </div>
        <div>
          <dt>Price Change</dt>
          <dd>${formatPercent(item.price_change_percent)}</dd>
        </div>
        <div>
          <dt>Sales</dt>
          <dd>${formatNumber(item.number_of_sales)}</dd>
        </div>
      </dl>
      <button class="insight-button" type="button" onclick="getAIInsight('${escapeForSingleQuotedJs(item.player || "")}')">
        Get AI Insight
      </button>
    </article>
  `).join("");
}

function renderDashboardList(container, items, metricLabel, formatter) {
  if (!items.length) {
    container.innerHTML = '<p class="dashboard-empty">No data available.</p>';
    return;
  }

  container.innerHTML = items.map((item) => `
    <article class="mini-card">
      <p class="mini-card-player">${item.player || "Unknown Player"}</p>
      <h3 class="mini-card-name">${item.card_name || "Unnamed Card"}</h3>
      <div class="mini-card-metric">
        <span>${metricLabel}</span>
        <strong>${formatter(item)}</strong>
      </div>
    </article>
  `).join("");
}

async function loadMainCards() {
  const player = searchInput.value.trim();
  const { sort, direction } = getSelectedSort();
  const limit = limitSelect.value || String(DEFAULT_LIMIT);

  statusMessage.textContent = "Loading card feed...";
  cardsContainer.innerHTML = "";

  try {
    const data = await requestCards({
      limit,
      sort,
      direction,
      player,
    });

    const items = Array.isArray(data.items) ? data.items : [];
    renderCards(items);

    const playerText = player ? ` for "${player}"` : "";
    statusMessage.textContent = `Showing ${data.count ?? items.length} cards${playerText}, sorted by ${sort} (${direction}) with a limit of ${limit}.`;
  } catch (error) {
    cardsContainer.innerHTML = "";
    statusMessage.textContent = `Unable to load cards. ${error.message}`;
  }
}

async function loadDashboard() {
  topGainersContainer.innerHTML = '<p class="dashboard-empty">Loading gainers...</p>';
  topLosersContainer.innerHTML = '<p class="dashboard-empty">Loading losers...</p>';
  highestVolumeContainer.innerHTML = '<p class="dashboard-empty">Loading volume leaders...</p>';

  try {
    const [gainers, losers, volume] = await Promise.all([
      requestCards({ limit: 5, sort: "price_change_percent", direction: "desc" }),
      requestCards({ limit: 5, sort: "price_change_percent", direction: "asc" }),
      requestCards({ limit: 5, sort: "number_of_sales", direction: "desc" }),
    ]);

    renderDashboardList(
      topGainersContainer,
      Array.isArray(gainers.items) ? gainers.items : [],
      "Change",
      (item) => formatPercent(item.price_change_percent)
    );
    renderDashboardList(
      topLosersContainer,
      Array.isArray(losers.items) ? losers.items : [],
      "Change",
      (item) => formatPercent(item.price_change_percent)
    );
    renderDashboardList(
      highestVolumeContainer,
      Array.isArray(volume.items) ? volume.items : [],
      "Sales",
      (item) => formatNumber(item.number_of_sales)
    );
  } catch (error) {
    topGainersContainer.innerHTML = '<p class="dashboard-empty">Unable to load gainers.</p>';
    topLosersContainer.innerHTML = '<p class="dashboard-empty">Unable to load losers.</p>';
    highestVolumeContainer.innerHTML = '<p class="dashboard-empty">Unable to load volume data.</p>';
  }
}

function resetControls() {
  searchInput.value = "";
  sortSelect.value = `${DEFAULT_SORT}:${DEFAULT_DIRECTION}`;
  limitSelect.value = String(DEFAULT_LIMIT);
}

searchButton.addEventListener("click", loadMainCards);
loadButton.addEventListener("click", () => {
  resetControls();
  loadMainCards();
});

searchInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    loadMainCards();
  }
});

sortSelect.addEventListener("change", loadMainCards);
limitSelect.addEventListener("change", loadMainCards);

async function initializePage() {
  statusMessage.textContent = "Loading dashboard and card feed...";
  await Promise.all([loadDashboard(), loadMainCards()]);
}

initializePage();
