// FarmChecker.xyz - Crypto Page
class CryptoPage {
  constructor() {
    this.apiBase = "/api";
    this.data = {
      trendingCrypto: [],
      marketData: {},
    };
    this.darkMode = localStorage.getItem('darkMode') === 'true';
    this.init();
  }

  async init() {
    this.setupTheme();
    await this.loadData();
    this.setupEventListeners();
    this.updateUI();

    // Auto-refresh every 5 minutes
    setInterval(() => this.loadData(), 5 * 60 * 1000);
  }

  setupTheme() {
    if (this.darkMode) {
      document.documentElement.setAttribute('data-theme', 'dark');
      document.querySelector('#dark-mode-toggle i').className = 'fas fa-sun';
    }
  }

  toggleDarkMode() {
    this.darkMode = !this.darkMode;
    localStorage.setItem('darkMode', this.darkMode);
    
    if (this.darkMode) {
      document.documentElement.setAttribute('data-theme', 'dark');
      document.querySelector('#dark-mode-toggle i').className = 'fas fa-sun';
    } else {
      document.documentElement.removeAttribute('data-theme');
      document.querySelector('#dark-mode-toggle i').className = 'fas fa-moon';
    }
  }

  async loadData() {
    try {
      await Promise.all([
        this.loadTrendingCrypto(),
        this.loadMarketData(),
      ]);
    } catch (error) {
      console.error("Error loading data:", error);
    }
  }

  async loadTrendingCrypto() {
    try {
      const response = await fetch(`${this.apiBase}/crypto/trending`);
      this.data.trendingCrypto = await response.json();
    } catch (error) {
      console.error("Error loading trending crypto:", error);
      this.data.trendingCrypto = [];
    }
  }

  async loadMarketData() {
    try {
      const response = await fetch(`${this.apiBase}/crypto/market-data`);
      this.data.marketData = await response.json();
    } catch (error) {
      console.error("Error loading market data:", error);
      this.data.marketData = {};
    }
  }

  setupEventListeners() {
    // Dark mode toggle
    const darkModeToggle = document.getElementById("dark-mode-toggle");
    if (darkModeToggle) {
      darkModeToggle.addEventListener("click", () => this.toggleDarkMode());
    }

    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById("mobile-menu-btn");
    const mobileNav = document.getElementById("mobile-nav");
    if (mobileMenuBtn && mobileNav) {
      mobileMenuBtn.addEventListener("click", () => {
        mobileNav.classList.toggle("active");
      });
    }
  }

  updateUI() {
    this.updateTrendingCrypto();
    this.updateMarketOverview();
  }

  updateTrendingCrypto() {
    const container = document.getElementById("trending-crypto");
    if (!container) return;

    if (this.data.trendingCrypto.length === 0) {
      container.innerHTML = '<div class="loading">No trending tokens available</div>';
      return;
    }

    container.innerHTML = this.data.trendingCrypto
      .slice(0, 10)
      .map(
        (token) => `
            <div class="crypto-item">
                <img src="${
                  token.image || "https://via.placeholder.com/40x40"
                }" alt="${
                  token.symbol
                }" onerror="this.src='https://via.placeholder.com/40x40'">
                <div class="crypto-item-info">
                    <div class="crypto-item-symbol">${token.symbol}</div>
                    <div class="crypto-item-name">${token.name}</div>
                </div>
                <div class="crypto-item-price">
                    <div class="crypto-item-value">${token.price || "—"}</div>
                    <div class="crypto-item-change ${
                      token.price_change_percentage_24h >= 0
                        ? "positive"
                        : "negative"
                    }">
                        ${token.price_change_24h || "0.00%"}
                    </div>
                </div>
            </div>
        `,
      )
      .join("");
  }

  updateMarketOverview() {
    const container = document.getElementById("market-overview");
    if (!container) return;

    if (
      !this.data.marketData ||
      Object.keys(this.data.marketData).length === 0
    ) {
      container.innerHTML = '<div class="loading">No market data available</div>';
      return;
    }

    container.innerHTML = `
            <div class="market-stat">
                <div class="market-stat-value">${this.formatNumber(
                  this.data.marketData.total_tokens,
                )}</div>
                <div class="market-stat-label">Total Tokens</div>
            </div>
            <div class="market-stat">
                <div class="market-stat-value">${
                  this.data.marketData.sources?.crypto || 0
                }</div>
                <div class="market-stat-label">CoinGecko</div>
            </div>
            <div class="market-stat">
                <div class="market-stat-value">${
                  this.data.marketData.sources?.dexscreener || 0
                }</div>
                <div class="market-stat-label">DexScreener</div>
            </div>
            <div class="market-stat">
                <div class="market-stat-value">${
                  this.data.marketData.sources?.dexpaprika || 0
                }</div>
                <div class="market-stat-label">DexPaprika</div>
            </div>
        `;
  }

  formatNumber(num) {
    if (num === null || num === undefined) return "-";
    if (num >= 1e9) return (num / 1e9).toFixed(1) + "B";
    if (num >= 1e6) return (num / 1e6).toFixed(1) + "M";
    if (num >= 1e3) return (num / 1e3).toFixed(1) + "K";
    return num.toString();
  }
}

// Initialize the crypto page
document.addEventListener("DOMContentLoaded", () => {
  new CryptoPage();
}); 