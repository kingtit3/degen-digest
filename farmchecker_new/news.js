// FarmChecker.xyz - News Page
class NewsPage {
  constructor() {
    this.apiBase = "/api";
    this.data = {
      news: [],
    };
    this.darkMode = localStorage.getItem('darkMode') === 'true';
    this.init();
  }

  async init() {
    console.log("News page initializing...");
    this.setupTheme();
    await this.loadData();
    this.setupEventListeners();
    this.updateUI();

    // Auto-refresh every 5 minutes
    setInterval(() => this.loadData(), 5 * 60 * 1000);
    console.log("News page initialization complete");
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
      await this.loadNews();
    } catch (error) {
      console.error("Error loading data:", error);
    }
  }

  async loadNews() {
    try {
      const response = await fetch(`${this.apiBase}/news-posts`);
      this.data.news = await response.json();
      console.log(`Loaded ${this.data.news.length} news stories`);
    } catch (error) {
      console.error("Error loading news:", error);
      this.data.news = [];
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

    // Sort select
    const sortSelect = document.getElementById("sort-select");
    if (sortSelect) {
      sortSelect.addEventListener("change", () => {
        this.updateUI();
      });
    }
  }

  updateUI() {
    this.renderNews();
  }

  renderNews() {
    const newsGrid = document.getElementById("news-grid");
    if (!newsGrid) return;

    if (this.data.news.length === 0) {
      newsGrid.innerHTML = '<div class="loading">No news stories available</div>';
      return;
    }

    // Sort news based on selected option
    const sortBy = document.getElementById("sort-select")?.value || "published_at";
    const sortedNews = [...this.data.news].sort((a, b) => {
      if (sortBy === "published_at") {
        return new Date(b.published_at || b.created_at || 0) - new Date(a.published_at || a.created_at || 0);
      }
      return (b[sortBy] || 0) - (a[sortBy] || 0);
    });

    newsGrid.innerHTML = sortedNews.map(news => this.createNewsCard(news)).join("");
  }

  createNewsCard(news) {
    const title = this.cleanTitle(news.title || "Untitled");
    const content = this.cleanContent(news.content || "");
    const author = this.cleanNewsAuthor(news.author);
    const url = news.url || "#";
    const publishedAt = news.published_at || news.created_at;
    const engagementScore = news.engagement_score || 0;
    const viralityScore = news.virality_score || 0;
    const sentimentScore = news.sentiment_score || 0;

    const date = publishedAt ? new Date(publishedAt).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    }) : "Unknown";

    return `
      <div class="post-card">
        <div class="post-header">
          <h4 class="post-title">
            <a href="${url}" target="_blank" rel="noopener noreferrer">
              ${title}
            </a>
          </h4>
          <div class="post-meta">
            <span><i class="fas fa-user"></i> ${author}</span>
            <span><i class="fas fa-calendar"></i> ${date}</span>
            <span class="engagement-score">
              <i class="fas fa-chart-line"></i> ${this.formatNumber(engagementScore)}
            </span>
          </div>
        </div>
        
        ${content ? `<div class="post-content">${content}</div>` : ""}
        
        <div class="post-engagement">
          <div class="engagement-item">
            <i class="fas fa-chart-line"></i>
            <span>Engagement: ${this.formatNumber(engagementScore)}</span>
          </div>
          <div class="engagement-item">
            <i class="fas fa-virus"></i>
            <span>Virality: ${this.formatNumber(viralityScore)}</span>
          </div>
          <div class="engagement-item">
            <i class="fas fa-smile"></i>
            <span>Sentiment: ${this.formatNumber(sentimentScore)}</span>
          </div>
        </div>
      </div>
    `;
  }

  cleanNewsAuthor(author) {
    if (!author || author === "Anonymous" || author === "anon") {
      return "News Source";
    }
    return author;
  }

  cleanTitle(title) {
    if (!title) return "Untitled";
    return title
      .replace(/[<>]/g, "")
      .replace(/&quot;/g, '"')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .substring(0, 200);
  }

  cleanContent(content) {
    if (!content) return "";
    if (content === "Content available") return "Content not available";
    
    return content
      .replace(/<[^>]*>/g, "")
      .replace(/&quot;/g, '"')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .substring(0, 300) + (content.length > 300 ? "..." : "");
  }

  formatNumber(num) {
    if (num === null || num === undefined) return "0";
    if (num >= 1e9) return (num / 1e9).toFixed(1) + "B";
    if (num >= 1e6) return (num / 1e6).toFixed(1) + "M";
    if (num >= 1e3) return (num / 1e3).toFixed(1) + "K";
    return num.toString();
  }
}

// Initialize the news page
document.addEventListener("DOMContentLoaded", () => {
  new NewsPage();
}); 