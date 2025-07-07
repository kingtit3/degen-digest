// FarmChecker.xyz - Analytics Page
class AnalyticsPage {
  constructor() {
    this.apiBase = "/api";
    this.data = {
      stats: {},
    };
    this.darkMode = localStorage.getItem('darkMode') === 'true';
    this.init();
  }

  async init() {
    console.log("Analytics page initializing...");
    this.setupTheme();
    await this.loadData();
    this.setupEventListeners();
    this.updateUI();
    this.setupCharts();

    // Auto-refresh every 5 minutes
    setInterval(() => this.loadData(), 5 * 60 * 1000);
    console.log("Analytics page initialization complete");
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
      await this.loadStats();
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
  }

  updateUI() {
    this.updateStats();
  }

  updateStats() {
    // Update Twitter count
    const twitterCount = document.getElementById("twitter-count");
    if (twitterCount) {
      twitterCount.textContent = this.formatNumber(this.data.stats.twitter || 0);
    }

    // Update Reddit count
    const redditCount = document.getElementById("reddit-count");
    if (redditCount) {
      redditCount.textContent = this.formatNumber(this.data.stats.reddit || 0);
    }

    // Update crypto count
    const cryptoCount = document.getElementById("crypto-count");
    if (cryptoCount) {
      cryptoCount.textContent = this.formatNumber(this.data.stats.crypto || 0);
    }

    // Update total engagement
    const totalEngagement = document.getElementById("total-engagement");
    if (totalEngagement) {
      totalEngagement.textContent = this.formatNumber(this.data.stats.total_engagement || 0);
    }
  }

  setupCharts() {
    console.log("Setting up charts...");
    try {
      this.setupSourceChart();
      this.setupEngagementChart();
      console.log("Charts setup complete");
    } catch (error) {
      console.error("Error setting up charts:", error);
    }
  }

  setupSourceChart() {
    const ctx = document.getElementById("source-chart");
    if (!ctx) {
      console.error("Source chart canvas not found");
      return;
    }

    const sourceData = {
      twitter: this.data.stats.twitter || 0,
      reddit: this.data.stats.reddit || 0,
      crypto: this.data.stats.crypto || 0,
    };

    try {
      new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: ["Twitter", "Reddit", "Crypto"],
          datasets: [
            {
              data: [sourceData.twitter, sourceData.reddit, sourceData.crypto],
              backgroundColor: ["#1DA1F2", "#FF4500", "#F7931A"],
              borderWidth: 0,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "bottom",
              labels: {
                color: getComputedStyle(document.documentElement).getPropertyValue('--text-color') || '#333',
              },
            },
          },
        },
      });
    } catch (error) {
      console.error("Error creating source chart:", error);
    }
  }

  setupEngagementChart() {
    const ctx = document.getElementById("engagement-chart");
    if (!ctx) {
      console.error("Engagement chart canvas not found");
      return;
    }

    // Generate sample engagement data for the last 7 days
    const engagementData = this.generateEngagementData();

    try {
      new Chart(ctx, {
      type: "line",
      data: {
        labels: engagementData.labels,
        datasets: [
          {
            label: "Engagement Score",
            data: engagementData.data,
            borderColor: "#667eea",
            backgroundColor: "rgba(102, 126, 234, 0.1)",
            borderWidth: 2,
            fill: true,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--text-color'),
            },
          },
        },
        scales: {
          x: {
            ticks: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--text-color'),
            },
            grid: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--border-color'),
            },
          },
          y: {
            ticks: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--text-color'),
            },
            grid: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--border-color'),
            },
          },
        },
      },
    });
    } catch (error) {
      console.error("Error creating engagement chart:", error);
    }
  }

  generateEngagementData() {
    const labels = [];
    const data = [];
    const today = new Date();

    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      labels.push(date.toLocaleDateString("en-US", { month: "short", day: "numeric" }));
      
      // Generate random engagement data
      data.push(Math.floor(Math.random() * 1000) + 100);
    }

    return { labels, data };
  }

  formatNumber(num) {
    if (num === null || num === undefined) return "0";
    if (num >= 1e9) return (num / 1e9).toFixed(1) + "B";
    if (num >= 1e6) return (num / 1e6).toFixed(1) + "M";
    if (num >= 1e3) return (num / 1e3).toFixed(1) + "K";
    return num.toString();
  }
}

// Initialize the analytics page
document.addEventListener("DOMContentLoaded", () => {
  new AnalyticsPage();
}); 