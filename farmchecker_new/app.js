// FarmChecker.xyz - Main Application
class FarmCheckerApp {
  constructor() {
    this.apiBase = "/api"; // Will be replaced with actual API endpoint
    this.data = {
      stats: {},
      twitterPosts: [],
      redditPosts: [],
      topGainers: [],
      trendingCrypto: [],
      marketData: {},
      latestDigest: null,
      systemStatus: {},
    };
    this.bannerPaused = false;
    this.init();
  }

  async init() {
    await this.loadAllData();
    this.setupEventListeners();
    this.updateUI();
    this.setupCharts();
    this.setupScrollingBanner();

    // Auto-refresh every 5 minutes
    setInterval(() => this.loadAllData(), 5 * 60 * 1000);
  }

  async loadAllData() {
    try {
      await Promise.all([
        this.loadStats(),
        this.loadTwitterPosts(),
        this.loadRedditPosts(),
        this.loadTopGainers(),
        this.loadTrendingCrypto(),
        this.loadMarketData(),
        this.loadLatestDigest(),
        this.loadSystemStatus(),
      ]);
    } catch (error) {
      console.error("Error loading data:", error);
    }
  }

  async loadStats() {
    try {
      const response = await fetch(`${this.apiBase}/stats`);
      this.data.stats = await response.json();
    } catch (error) {
      console.error("Error loading stats:", error);
      // Fallback data
      this.data.stats = {
        twitter: 14,
        reddit: 20,
        crypto: 820,
        total_engagement: 15678,
      };
    }
  }

  async loadTopGainers() {
    try {
      const response = await fetch(`${this.apiBase}/crypto/top-gainers`);
      this.data.topGainers = await response.json();
    } catch (error) {
      console.error("Error loading top gainers:", error);
      // Fallback data
      this.data.topGainers = [
        {
          symbol: "BTC",
          name: "Bitcoin",
          price: 45000,
          price_change_percentage_24h: 5.2,
          image:
            "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
        },
        {
          symbol: "ETH",
          name: "Ethereum",
          price: 3200,
          price_change_percentage_24h: 3.8,
          image:
            "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
        },
      ];
    }
  }

  async loadTrendingCrypto() {
    try {
      const response = await fetch(`${this.apiBase}/crypto/trending`);
      this.data.trendingCrypto = await response.json();
    } catch (error) {
      console.error("Error loading trending crypto:", error);
      // Fallback data
      this.data.trendingCrypto = [
        {
          symbol: "SOL",
          name: "Solana",
          price: 120,
          price_change_percentage_24h: 8.5,
          image:
            "https://assets.coingecko.com/coins/images/4128/large/solana.png",
        },
        {
          symbol: "ADA",
          name: "Cardano",
          price: 0.85,
          price_change_percentage_24h: 2.1,
          image:
            "https://assets.coingecko.com/coins/images/975/large/cardano.png",
        },
      ];
    }
  }

  async loadMarketData() {
    try {
      const response = await fetch(`${this.apiBase}/crypto/market-data`);
      this.data.marketData = await response.json();
    } catch (error) {
      console.error("Error loading market data:", error);
      // Fallback data
      this.data.marketData = {
        total_tokens: 820,
        sources: {
          crypto: 70,
          dexpaprika: 30,
          dexscreener: 720,
        },
        market_sentiment: "bullish",
      };
    }
  }

  async loadTwitterPosts() {
    try {
      const response = await fetch(`${this.apiBase}/twitter-posts`);
      this.data.twitterPosts = await response.json();
    } catch (error) {
      console.error("Error loading Twitter posts:", error);
      // Fallback data
      this.data.twitterPosts = [
        {
          id: 1,
          title: "Bitcoin reaches new all-time high",
          content:
            "Bitcoin has reached a new all-time high of $75,000, driven by institutional adoption...",
          author: "crypto_analyst",
          engagement_score: 1250,
          published_at: "2025-07-05T20:30:00Z",
          likes: 850,
          replies: 400,
          retweets: 200,
          views: 50000,
        },
      ];
    }
  }

  async loadRedditPosts() {
    try {
      const response = await fetch(`${this.apiBase}/reddit-posts`);
      this.data.redditPosts = await response.json();
    } catch (error) {
      console.error("Error loading Reddit posts:", error);
      // Fallback data
      this.data.redditPosts = [
        {
          id: 1,
          title: "Ethereum 2.0 Update Discussion",
          content:
            "What do you think about the latest Ethereum 2.0 developments?",
          author: "eth_enthusiast",
          engagement_score: 850,
          published_at: "2025-07-05T19:30:00Z",
          upvotes: 650,
          comments: 200,
          score: 850,
        },
      ];
    }
  }

  async loadLatestDigest() {
    try {
      const response = await fetch(`${this.apiBase}/latest-digest`);
      this.data.latestDigest = await response.json();
    } catch (error) {
      console.error("Error loading latest digest:", error);
      // Fallback data
      this.data.latestDigest = {
        title: "Daily Crypto Digest - July 5, 2025",
        content:
          "Today's top stories include Bitcoin's new ATH, Ethereum upgrades, and DeFi innovations...",
        created_at: "2025-07-05T21:00:00Z",
      };
    }
  }

  async loadSystemStatus() {
    try {
      const response = await fetch(`${this.apiBase}/system-status`);
      this.data.systemStatus = await response.json();
    } catch (error) {
      console.error("Error loading system status:", error);
      // Fallback data
      this.data.systemStatus = {
        twitter: { status: "online", last_run: "2025-07-05T21:30:00Z" },
        reddit: { status: "online", last_run: "2025-07-05T21:15:00Z" },
        crypto: { status: "online", last_run: "2025-07-05T21:25:00Z" },
      };
    }
  }

  setupEventListeners() {
    // Navigation
    document.querySelectorAll(".nav-link").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        this.handleNavigation(e.target.getAttribute("href").substring(1));
      });
    });

    // Twitter filter
    const twitterFilter = document.getElementById("twitter-filter");
    if (twitterFilter) {
      twitterFilter.addEventListener("change", (e) => {
        this.sortTwitterPosts(e.target.value);
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

  handleNavigation(section) {
    // Update active nav link
    document.querySelectorAll(".nav-link").forEach((link) => {
      link.classList.remove("active");
    });
    document.querySelector(`[href="#${section}"]`).classList.add("active");

    // Scroll to section
    document.getElementById(section).scrollIntoView({ behavior: "smooth" });
  }

  updateUI() {
    this.updateStats();
    this.updateTopGainersBanner();
    this.updateTrendingCrypto();
    this.updateMarketOverview();
    this.updateTwitterPosts();
    this.updateRedditPosts();
    this.updateLatestDigest();
    this.updateSystemStatus();
  }

  updateStats() {
    document.getElementById("twitter-count").textContent =
      this.data.stats.twitter || "-";
    document.getElementById("reddit-count").textContent =
      this.data.stats.reddit || "-";
    document.getElementById("crypto-count").textContent =
      this.data.stats.crypto || "-";
    document.getElementById("total-engagement").textContent =
      this.formatNumber(this.data.stats.total_engagement) || "-";
  }

  updateTopGainersBanner() {
    const container = document.getElementById("top-gainers-banner");
    if (!container) return;

    if (this.data.topGainers.length === 0) {
      container.innerHTML =
        '<div class="loading">No top gainers available</div>';
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
                    <div class="price-value">$${this.formatPrice(
                      token.price,
                    )}</div>
                    <div class="price-change ${
                      token.price_change_percentage_24h >= 0
                        ? "positive"
                        : "negative"
                    }">
                        ${
                          token.price_change_percentage_24h >= 0 ? "+" : ""
                        }${token.price_change_percentage_24h.toFixed(2)}%
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

  updateTrendingCrypto() {
    const container = document.getElementById("trending-crypto");
    if (!container) return;

    if (this.data.trendingCrypto.length === 0) {
      container.innerHTML =
        '<div class="loading">No trending tokens available</div>';
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
                    <div class="crypto-item-value">$${this.formatPrice(
                      token.price,
                    )}</div>
                    <div class="crypto-item-change ${
                      token.price_change_percentage_24h >= 0
                        ? "positive"
                        : "negative"
                    }">
                        ${
                          token.price_change_percentage_24h >= 0 ? "+" : ""
                        }${token.price_change_percentage_24h.toFixed(2)}%
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
      container.innerHTML =
        '<div class="loading">No market data available</div>';
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

  updateTwitterPosts() {
    const container = document.getElementById("twitter-posts");
    if (!container) return;

    if (this.data.twitterPosts.length === 0) {
      container.innerHTML =
        '<div class="loading">No Twitter posts available</div>';
      return;
    }

    container.innerHTML = this.data.twitterPosts
      .map(
        (post) => `
            <div class="post-card">
                <div class="post-header">
                    <div>
                        <div class="post-title">${this.escapeHtml(
                          post.title,
                        )}</div>
                        <div class="post-meta">
                            <span><i class="fas fa-user"></i> ${this.escapeHtml(
                              post.author || "Anonymous",
                            )}</span>
                            <span><i class="fas fa-clock"></i> ${this.formatDate(
                              post.published_at,
                            )}</span>
                        </div>
                    </div>
                    <div class="engagement-score">
                        <span class="badge">${this.formatNumber(
                          post.engagement_score,
                        )}</span>
                    </div>
                </div>
                <div class="post-content">${this.escapeHtml(
                  post.content || "",
                )}</div>
                <div class="post-engagement">
                    <div class="engagement-item">
                        <i class="fas fa-heart"></i>
                        <span>${this.formatNumber(post.likes || 0)}</span>
                    </div>
                    <div class="engagement-item">
                        <i class="fas fa-comment"></i>
                        <span>${this.formatNumber(post.replies || 0)}</span>
                    </div>
                    <div class="engagement-item">
                        <i class="fas fa-retweet"></i>
                        <span>${this.formatNumber(post.retweets || 0)}</span>
                    </div>
                    <div class="engagement-item">
                        <i class="fas fa-eye"></i>
                        <span>${this.formatNumber(post.views || 0)}</span>
                    </div>
                </div>
            </div>
        `,
      )
      .join("");
  }

  updateRedditPosts() {
    const container = document.getElementById("reddit-posts");
    if (!container) return;

    if (this.data.redditPosts.length === 0) {
      container.innerHTML =
        '<div class="loading">No Reddit posts available</div>';
      return;
    }

    container.innerHTML = this.data.redditPosts
      .map(
        (post) => `
            <div class="post-card">
                <div class="post-header">
                    <div>
                        <div class="post-title">${this.escapeHtml(
                          post.title,
                        )}</div>
                        <div class="post-meta">
                            <span><i class="fas fa-user"></i> ${this.escapeHtml(
                              post.author || "Anonymous",
                            )}</span>
                            <span><i class="fas fa-clock"></i> ${this.formatDate(
                              post.published_at,
                            )}</span>
                        </div>
                    </div>
                    <div class="engagement-score">
                        <span class="badge">${this.formatNumber(
                          post.engagement_score,
                        )}</span>
                    </div>
                </div>
                <div class="post-content">${this.escapeHtml(
                  post.content || "",
                )}</div>
                <div class="post-engagement">
                    <div class="engagement-item">
                        <i class="fas fa-arrow-up"></i>
                        <span>${this.formatNumber(post.upvotes || 0)}</span>
                    </div>
                    <div class="engagement-item">
                        <i class="fas fa-comment"></i>
                        <span>${this.formatNumber(post.comments || 0)}</span>
                    </div>
                    <div class="engagement-item">
                        <i class="fas fa-chart-line"></i>
                        <span>${this.formatNumber(post.score || 0)}</span>
                    </div>
                </div>
            </div>
        `,
      )
      .join("");
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
                <h4>${this.escapeHtml(this.data.latestDigest.title)}</h4>
                <span class="digest-date">${this.formatDate(
                  this.data.latestDigest.created_at,
                )}</span>
            </div>
            <div class="digest-body">
                ${this.escapeHtml(this.data.latestDigest.content)}
            </div>
        `;
  }

  updateSystemStatus() {
    const container = document.getElementById("system-status");
    if (!container) return;

    if (
      !this.data.systemStatus ||
      Object.keys(this.data.systemStatus).length === 0
    ) {
      container.innerHTML =
        '<div class="loading">No system status available</div>';
      return;
    }

    container.innerHTML = Object.entries(this.data.systemStatus)
      .map(
        ([service, status]) => `
            <div class="status-card ${status.status}">
                <div class="status-header">
                    <h4>${this.formatServiceName(service)}</h4>
                    <span class="status-indicator ${status.status}"></span>
                </div>
                <div class="status-details">
                    <p><strong>Status:</strong> ${status.status}</p>
                    <p><strong>Last Run:</strong> ${
                      status.last_run_ago || "Unknown"
                    }</p>
                </div>
            </div>
        `,
      )
      .join("");
  }

  setupScrollingBanner() {
    // Banner is set up in updateTopGainersBanner()
  }

  pauseBanner() {
    this.bannerPaused = true;
    const content = document.querySelector(".scrolling-content");
    if (content) {
      content.classList.add("paused");
    }

    document.getElementById("pause-banner").style.display = "none";
    document.getElementById("play-banner").style.display = "block";
  }

  playBanner() {
    this.bannerPaused = false;
    const content = document.querySelector(".scrolling-content");
    if (content) {
      content.classList.remove("paused");
    }

    document.getElementById("pause-banner").style.display = "block";
    document.getElementById("play-banner").style.display = "none";
  }

  setupCharts() {
    this.setupSourceChart();
    this.setupEngagementChart();
  }

  setupSourceChart() {
    const ctx = document.getElementById("source-chart");
    if (!ctx) return;

    const data = {
      labels: ["Twitter", "Reddit", "Crypto", "News"],
      datasets: [
        {
          data: [
            this.data.stats.twitter || 0,
            this.data.stats.reddit || 0,
            this.data.stats.crypto || 0,
            this.data.stats.news || 0,
          ],
          backgroundColor: ["#1DA1F2", "#FF4500", "#F7931A", "#FF6B6B"],
        },
      ],
    };

    new Chart(ctx, {
      type: "doughnut",
      data: data,
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "bottom",
          },
        },
      },
    });
  }

  setupEngagementChart() {
    const ctx = document.getElementById("engagement-chart");
    if (!ctx) return;

    const engagementData = this.generateEngagementData();

    new Chart(ctx, {
      type: "line",
      data: {
        labels: engagementData.labels,
        datasets: [
          {
            label: "Engagement Score",
            data: engagementData.data,
            borderColor: "#4CAF50",
            backgroundColor: "rgba(76, 175, 80, 0.1)",
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }

  generateEngagementData() {
    // Generate sample engagement data for the last 7 days
    const labels = [];
    const data = [];

    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      labels.push(
        date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
      );
      data.push(Math.floor(Math.random() * 1000) + 500);
    }

    return { labels, data };
  }

  sortTwitterPosts(sortBy) {
    if (sortBy === "engagement") {
      this.data.twitterPosts.sort(
        (a, b) => (b.engagement_score || 0) - (a.engagement_score || 0),
      );
    } else if (sortBy === "recent") {
      this.data.twitterPosts.sort(
        (a, b) => new Date(b.published_at) - new Date(a.published_at),
      );
    }
    this.updateTwitterPosts();
  }

  formatNumber(num) {
    if (num === null || num === undefined) return "0";
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + "M";
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + "K";
    }
    return num.toString();
  }

  formatPrice(price) {
    if (price === null || price === undefined) return "0.00";
    if (price >= 1) {
      return price.toFixed(2);
    } else if (price >= 0.01) {
      return price.toFixed(4);
    } else {
      return price.toFixed(8);
    }
  }

  formatDate(dateString) {
    if (!dateString) return "Unknown";

    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffInMinutes = Math.floor((now - date) / (1000 * 60));

      if (diffInMinutes < 1) return "Just now";
      if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
      if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
      if (diffInMinutes < 10080)
        return `${Math.floor(diffInMinutes / 1440)}d ago`;

      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (error) {
      return "Invalid date";
    }
  }

  formatServiceName(service) {
    return service.charAt(0).toUpperCase() + service.slice(1);
  }

  escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize the application when the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new FarmCheckerApp();
});
