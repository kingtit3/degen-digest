// FarmChecker.xyz - DEX Page
class DexPage {
  constructor() {
    this.apiBase = "/api";
    this.data = {
      dexscreener: [],
      dexpaprika: [],
      combined: [],
      stats: {}
    };
    this.currentTab = 'dexscreener';
    this.currentSort = 'volume';
    this.darkMode = localStorage.getItem('darkMode') === 'true';
    this.init();
  }

  async init() {
    this.setupTheme();
    await this.loadAllData();
    this.setupEventListeners();
    this.updateUI();

    // Auto-refresh every 2 minutes for DEX data
    setInterval(() => this.loadAllData(), 2 * 60 * 1000);
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

  async loadAllData() {
    try {
      await Promise.all([
        this.loadDexScreenerData(),
        this.loadDexPaprikaData(),
        this.loadCombinedData(),
        this.loadStats()
      ]);
    } catch (error) {
      console.error("Error loading DEX data:", error);
    }
  }

  async loadDexScreenerData() {
    try {
      const response = await fetch(`${this.apiBase}/dex/dexscreener?sort=${this.currentSort}`);
      this.data.dexscreener = await response.json();
    } catch (error) {
      console.error("Error loading DexScreener data:", error);
      this.data.dexscreener = [];
    }
  }

  async loadDexPaprikaData() {
    try {
      const response = await fetch(`${this.apiBase}/dex/dexpaprika?sort=${this.currentSort}`);
      this.data.dexpaprika = await response.json();
    } catch (error) {
      console.error("Error loading DexPaprika data:", error);
      this.data.dexpaprika = [];
    }
  }

  async loadCombinedData() {
    try {
      const response = await fetch(`${this.apiBase}/dex/combined?sort=${this.currentSort}`);
      this.data.combined = await response.json();
    } catch (error) {
      console.error("Error loading combined DEX data:", error);
      this.data.combined = [];
    }
  }

  async loadStats() {
    try {
      const response = await fetch(`${this.apiBase}/stats`);
      this.data.stats = await response.json();
    } catch (error) {
      console.error("Error loading stats:", error);
      this.data.stats = {};
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

    // Tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
      button.addEventListener('click', (e) => {
        this.switchTab(e.target.dataset.tab);
      });
    });

    // Sort filter
    const sortFilter = document.getElementById("dex-sort-filter");
    if (sortFilter) {
      sortFilter.addEventListener("change", (e) => {
        this.currentSort = e.target.value;
        this.loadAllData();
      });
    }
  }

  switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
      button.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');

    this.currentTab = tabName;
    this.updateUI();
  }

  updateUI() {
    this.updateOverview();
    this.updateDexScreenerData();
    this.updateDexPaprikaData();
    this.updateCombinedData();
  }

  updateOverview() {
    const totalPairs = (this.data.stats.dexscreener_pairs || 0) + (this.data.stats.dexpaprika_tokens || 0);
    const totalVolume = this.calculateTotalVolume();
    const totalLiquidity = this.calculateTotalLiquidity();
    const lastUpdated = this.getLastUpdated();

    document.getElementById('total-pairs').textContent = this.formatNumber(totalPairs);
    document.getElementById('total-volume').textContent = this.formatCurrency(totalVolume);
    document.getElementById('total-liquidity').textContent = this.formatCurrency(totalLiquidity);
    document.getElementById('last-updated').textContent = lastUpdated;
  }

  calculateTotalVolume() {
    let total = 0;
    
    // Add DexScreener volume
    this.data.dexscreener.forEach(pair => {
      total += parseFloat(pair.volume_24h || 0);
    });
    
    // Add DexPaprika volume
    this.data.dexpaprika.forEach(token => {
      total += parseFloat(token.volume_24h || 0);
    });
    
    return total;
  }

  calculateTotalLiquidity() {
    let total = 0;
    
    // Add DexScreener liquidity
    this.data.dexscreener.forEach(pair => {
      total += parseFloat(pair.liquidity_usd || 0);
    });
    
    // Add DexPaprika liquidity
    this.data.dexpaprika.forEach(token => {
      total += parseFloat(token.liquidity_usd || 0);
    });
    
    return total;
  }

  getLastUpdated() {
    const now = new Date();
    return now.toLocaleTimeString();
  }

  updateDexScreenerData() {
    const container = document.getElementById("dexscreener-data");
    const loading = document.getElementById("dexscreener-loading");
    
    if (!container) return;

    if (this.data.dexscreener.length === 0) {
      loading.style.display = 'none';
      container.innerHTML = '<div class="no-data">No DexScreener data available</div>';
      return;
    }

    loading.style.display = 'none';
    container.innerHTML = this.data.dexscreener
      .slice(0, 20)
      .map(pair => this.renderDexScreenerPair(pair))
      .join("");
  }

  updateDexPaprikaData() {
    const container = document.getElementById("dexpaprika-data");
    const loading = document.getElementById("dexpaprika-loading");
    
    if (!container) return;

    if (this.data.dexpaprika.length === 0) {
      loading.style.display = 'none';
      container.innerHTML = '<div class="no-data">No DexPaprika data available</div>';
      return;
    }

    loading.style.display = 'none';
    container.innerHTML = this.data.dexpaprika
      .slice(0, 20)
      .map(token => this.renderDexPaprikaToken(token))
      .join("");
  }

  updateCombinedData() {
    const container = document.getElementById("combined-data");
    const loading = document.getElementById("combined-loading");
    
    if (!container) return;

    if (this.data.combined.length === 0) {
      loading.style.display = 'none';
      container.innerHTML = '<div class="no-data">No combined data available</div>';
      return;
    }

    loading.style.display = 'none';
    container.innerHTML = this.data.combined
      .slice(0, 30)
      .map(item => this.renderCombinedItem(item))
      .join("");
  }

  renderDexScreenerPair(pair) {
    const priceChangeClass = parseFloat(pair.price_change_24h) >= 0 ? 'positive' : 'negative';
    const priceChangeIcon = parseFloat(pair.price_change_24h) >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
    
    return `
      <div class="dex-item">
        <div class="dex-item-header">
          <div class="dex-item-symbol">
            <span class="token-symbol">${pair.base_token_symbol}</span>
            <span class="token-pair">/${pair.quote_token_symbol}</span>
          </div>
          <div class="dex-item-source">
            <i class="fas fa-chart-bar"></i>
            ${pair.dex}
          </div>
        </div>
        
        <div class="dex-item-name">${pair.base_token_name}</div>
        
        <div class="dex-item-price">
          <div class="price-value">$${this.formatPrice(pair.price_usd)}</div>
          <div class="price-change ${priceChangeClass}">
            <i class="fas ${priceChangeIcon}"></i>
            ${this.formatPercentage(pair.price_change_24h)}
          </div>
        </div>
        
        <div class="dex-item-stats">
          <div class="stat-item">
            <span class="stat-label">Volume (24h):</span>
            <span class="stat-value">$${this.formatNumber(pair.volume_24h)}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Liquidity:</span>
            <span class="stat-value">$${this.formatNumber(pair.liquidity_usd)}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">FDV:</span>
            <span class="stat-value">$${this.formatNumber(pair.fdv)}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Txns (24h):</span>
            <span class="stat-value">${this.formatNumber(pair.txns_24h)}</span>
          </div>
        </div>
        
        <div class="dex-item-footer">
          <a href="${pair.dex_url}" target="_blank" class="dex-link">
            <i class="fas fa-external-link-alt"></i>
            View on DexScreener
          </a>
        </div>
      </div>
    `;
  }

  renderDexPaprikaToken(token) {
    const priceChangeClass = parseFloat(token.price_change_24h) >= 0 ? 'positive' : 'negative';
    const priceChangeIcon = parseFloat(token.price_change_24h) >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
    
    return `
      <div class="dex-item">
        <div class="dex-item-header">
          <div class="dex-item-symbol">
            <span class="token-symbol">${token.symbol}</span>
          </div>
          <div class="dex-item-source">
            <i class="fas fa-chart-pie"></i>
            ${token.dex}
          </div>
        </div>
        
        <div class="dex-item-name">${token.name}</div>
        
        <div class="dex-item-price">
          <div class="price-value">$${this.formatPrice(token.price_usd)}</div>
          <div class="price-change ${priceChangeClass}">
            <i class="fas ${priceChangeIcon}"></i>
            ${this.formatPercentage(token.price_change_24h)}
          </div>
        </div>
        
        <div class="dex-item-stats">
          <div class="stat-item">
            <span class="stat-label">Volume (24h):</span>
            <span class="stat-value">$${this.formatNumber(token.volume_24h)}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Liquidity:</span>
            <span class="stat-value">$${this.formatNumber(token.liquidity_usd)}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Market Cap:</span>
            <span class="stat-value">$${this.formatNumber(token.market_cap)}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Txns (24h):</span>
            <span class="stat-value">${this.formatNumber(token.txns_24h)}</span>
          </div>
        </div>
        
        <div class="dex-item-footer">
          <a href="${token.token_url}" target="_blank" class="dex-link">
            <i class="fas fa-external-link-alt"></i>
            View on DexPaprika
          </a>
        </div>
      </div>
    `;
  }

  renderCombinedItem(item) {
    const priceChangeClass = parseFloat(item.price_change_24h) >= 0 ? 'positive' : 'negative';
    const priceChangeIcon = parseFloat(item.price_change_24h) >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
    const sourceIcon = item.source === 'dexscreener' ? 'fa-chart-bar' : 'fa-chart-pie';
    
    return `
      <div class="dex-item combined">
        <div class="dex-item-header">
          <div class="dex-item-symbol">
            <span class="token-symbol">${item.symbol}</span>
          </div>
          <div class="dex-item-source">
            <i class="fas ${sourceIcon}"></i>
            ${item.source}
          </div>
        </div>
        
        <div class="dex-item-name">${item.name}</div>
        
        <div class="dex-item-price">
          <div class="price-value">$${this.formatPrice(item.price_usd)}</div>
          <div class="price-change ${priceChangeClass}">
            <i class="fas ${priceChangeIcon}"></i>
            ${this.formatPercentage(item.price_change_24h)}
          </div>
        </div>
        
        <div class="dex-item-stats">
          <div class="stat-item">
            <span class="stat-label">Volume (24h):</span>
            <span class="stat-value">$${this.formatNumber(item.volume_24h)}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Liquidity:</span>
            <span class="stat-value">$${this.formatNumber(item.liquidity_usd)}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Market Cap:</span>
            <span class="stat-value">$${this.formatNumber(item.market_cap)}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Txns (24h):</span>
            <span class="stat-value">${this.formatNumber(item.txns_24h)}</span>
          </div>
        </div>
      </div>
    `;
  }

  formatNumber(num) {
    if (num === null || num === undefined || isNaN(num)) return "-";
    if (num >= 1e9) return (num / 1e9).toFixed(1) + "B";
    if (num >= 1e6) return (num / 1e6).toFixed(1) + "M";
    if (num >= 1e3) return (num / 1e3).toFixed(1) + "K";
    return num.toLocaleString();
  }

  formatCurrency(amount) {
    if (amount === null || amount === undefined || isNaN(amount)) return "-";
    if (amount >= 1e9) return "$" + (amount / 1e9).toFixed(1) + "B";
    if (amount >= 1e6) return "$" + (amount / 1e6).toFixed(1) + "M";
    if (amount >= 1e3) return "$" + (amount / 1e3).toFixed(1) + "K";
    return "$" + amount.toLocaleString();
  }

  formatPrice(price) {
    if (price === null || price === undefined || isNaN(price)) return "0.00";
    if (price < 0.01) return price.toFixed(6);
    if (price < 1) return price.toFixed(4);
    return price.toFixed(2);
  }

  formatPercentage(percentage) {
    if (percentage === null || percentage === undefined || isNaN(percentage)) return "0.00%";
    return percentage.toFixed(2) + "%";
  }
}

// Initialize the DEX page
document.addEventListener("DOMContentLoaded", () => {
  new DexPage();
}); 