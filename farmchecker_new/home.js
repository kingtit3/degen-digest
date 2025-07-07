// FarmChecker.xyz - Home Page
class HomePage {
  constructor() {
    this.apiBase = "/api";
    this.data = {
      topGainers: [],
      latestDigest: null,
    };
    this.bannerPaused = false;
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
        this.loadTopGainers(),
        this.loadLatestDigest(),
      ]);
    } catch (error) {
      console.error("Error loading data:", error);
    }
  }

  async loadTopGainers() {
    try {
      const response = await fetch(`${this.apiBase}/crypto/top-gainers`);
      this.data.topGainers = await response.json();
    } catch (error) {
      console.error("Error loading top gainers:", error);
      this.data.topGainers = [];
    }
  }

  async loadLatestDigest() {
    try {
      const response = await fetch(`${this.apiBase}/latest-digest`);
      this.data.latestDigest = await response.json();
    } catch (error) {
      console.error("Error loading latest digest:", error);
      this.data.latestDigest = null;
    }
  }

  setupEventListeners() {
    // Dark mode toggle
    const darkModeToggle = document.getElementById("dark-mode-toggle");
    if (darkModeToggle) {
      darkModeToggle.addEventListener("click", () => this.toggleDarkMode());
    }

    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById("mobile-menu-toggle");
    const mobileNav = document.getElementById("mobile-nav");
    if (mobileMenuToggle && mobileNav) {
      mobileMenuToggle.addEventListener("click", () => {
        mobileNav.classList.toggle("active");
      });
    }

    // Banner controls
    const pauseBtn = document.getElementById("pause-banner");
    const playBtn = document.getElementById("play-banner");

    if (pauseBtn) {
      pauseBtn.addEventListener("click", () => this.pauseBanner());
    }
    if (playBtn) {
      playBtn.addEventListener("click", () => this.playBanner());
    }
  }

  updateUI() {
    this.updateTopGainersBanner();
    this.updateLatestDigest();
  }

  updateTopGainersBanner() {
    const container = document.getElementById("top-gainers-banner");
    if (!container) return;

    if (this.data.topGainers.length === 0) {
      container.innerHTML = '<div class="loading">No top gainers available</div>';
      return;
    }

    const tickers = this.data.topGainers
      .map(
        (token) => `
            <div class="crypto-ticker">
                <img src="${
                  token.image || "https://via.placeholder.com/32x32"
                }" alt="${
                  token.symbol
                }" onerror="this.src='https://via.placeholder.com/32x32'">
                <div class="crypto-info">
                    <div class="crypto-symbol">${token.symbol}</div>
                    <div class="crypto-name">${token.name}</div>
                </div>
                <div class="crypto-price">
                    <div class="price-value">${token.price || "—"}</div>
                    <div class="price-change ${
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

    // Duplicate tickers for seamless scrolling
    container.innerHTML = `
            <div class="scrolling-content ${this.bannerPaused ? "paused" : ""}">
                ${tickers}
                ${tickers} <!-- Duplicate for seamless loop -->
            </div>
        `;
  }

  updateLatestDigest() {
    const container = document.getElementById("latest-digest");
    if (!container) return;

    if (!this.data.latestDigest) {
      container.innerHTML = '<div class="loading">No digest available</div>';
      return;
    }

    container.innerHTML = `
            <div class="digest-header">
                <h4>${this.data.latestDigest.title}</h4>
                <span class="digest-date">${this.formatDate(this.data.latestDigest.created_at)}</span>
            </div>
            <div class="digest-body">
                ${this.data.latestDigest.content}
            </div>
        `;
  }

  pauseBanner() {
    this.bannerPaused = true;
    const scrollingContent = document.querySelector(".scrolling-content");
    if (scrollingContent) {
      scrollingContent.classList.add("paused");
    }
    document.getElementById("pause-banner").style.display = "none";
    document.getElementById("play-banner").style.display = "block";
  }

  playBanner() {
    this.bannerPaused = false;
    const scrollingContent = document.querySelector(".scrolling-content");
    if (scrollingContent) {
      scrollingContent.classList.remove("paused");
    }
    document.getElementById("pause-banner").style.display = "block";
    document.getElementById("play-banner").style.display = "none";
  }

  formatDate(dateString) {
    if (!dateString) return "Unknown date";
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (error) {
      return "Invalid date";
    }
  }
}

// Initialize the home page
document.addEventListener("DOMContentLoaded", () => {
  new HomePage();
}); 