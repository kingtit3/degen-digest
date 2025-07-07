// FarmChecker.xyz - Twitter Page
class TwitterPage {
  constructor() {
    this.apiBase = "/api";
    this.data = {
      twitterPosts: [],
    };
    this.currentSort = 'engagement';
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
      await this.loadTwitterPosts();
    } catch (error) {
      console.error("Error loading data:", error);
    }
  }

  async loadTwitterPosts() {
    try {
      const response = await fetch(`${this.apiBase}/twitter?sort=${this.currentSort}`);
      this.data.twitterPosts = await response.json();
    } catch (error) {
      console.error("Error loading Twitter posts:", error);
      this.data.twitterPosts = [];
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

    // Twitter filter
    const twitterFilter = document.getElementById("twitter-filter");
    if (twitterFilter) {
      twitterFilter.addEventListener("change", (e) => {
        this.currentSort = e.target.value;
        this.loadData();
      });
    }
  }

  updateUI() {
    this.updateTwitterPosts();
  }

  updateTwitterPosts() {
    const container = document.getElementById("twitter-posts");
    if (!container) return;

    if (this.data.twitterPosts.length === 0) {
      container.innerHTML = '<div class="loading">No Twitter posts available</div>';
      return;
    }

    container.innerHTML = this.data.twitterPosts
      .map(
        (post) => `
            <div class="post-card twitter-post">
                <div class="post-header">
                    <div class="post-author-info">
                        <div class="author-avatar">
                            <i class="fab fa-twitter"></i>
                        </div>
                        <div class="author-details">
                            <div class="author-name">${this.escapeHtml(
                              post.user_screen_name || post.author || "Anonymous",
                            )}</div>
                            <div class="post-meta">
                                <span class="verified-badge ${post.user_verified ? 'verified' : ''}">
                                    ${post.user_verified ? '<i class="fas fa-check-circle"></i>' : ''}
                                </span>
                                <span class="followers-count">
                                    <i class="fas fa-users"></i> ${this.formatNumber(post.user_followers_count || 0)}
                                </span>
                                <span class="post-time">
                                    <i class="fas fa-clock"></i> ${this.formatDate(post.published_at)}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="engagement-score">
                        <span class="badge">${this.formatNumber(post.engagement_score || 0)}</span>
                    </div>
                </div>
                <div class="post-content">
                    <div class="tweet-text">${this.escapeHtml(this.cleanTwitterContent(post.content))}</div>
                    ${post.url ? `<div class="tweet-link"><a href="${post.url}" target="_blank" rel="noopener">View Tweet <i class="fas fa-external-link-alt"></i></a></div>` : ''}
                </div>
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
                    ${post.quote_count > 0 ? `
                    <div class="engagement-item">
                        <i class="fas fa-quote-left"></i>
                        <span>${this.formatNumber(post.quote_count)}</span>
                    </div>
                    ` : ''}
                    ${post.bookmark_count > 0 ? `
                    <div class="engagement-item">
                        <i class="fas fa-bookmark"></i>
                        <span>${this.formatNumber(post.bookmark_count)}</span>
                    </div>
                    ` : ''}
                </div>
            </div>
        `,
      )
      .join("");
  }

  cleanTwitterTitle(title) {
    if (!title) return "Twitter Post";
    return title;
  }

  cleanTwitterContent(content) {
    if (!content) return "Content not available";
    if (content === "Content available") return "Content not available";
    
    // If content is already clean text, return it
    if (content.length > 10 && !content.includes("'text':") && !content.includes("'source':")) {
      return content.substring(0, 200) + (content.length > 200 ? "..." : "");
    }
    
    // Try to extract text from JSON-like content
    if (content.includes("'text':")) {
      try {
        const textMatch = content.match(/'text':\s*'([^']+)'/);
        if (textMatch) {
          return textMatch[1].substring(0, 200) + (textMatch[1].length > 200 ? "..." : "");
        }
      } catch (e) {
        // Fall through to return original content
      }
    }
    
    // Try to extract from JSON format
    if (content.includes('"text":')) {
      try {
        const textMatch = content.match(/"text":\s*"([^"]+)"/);
        if (textMatch) {
          return textMatch[1].substring(0, 200) + (textMatch[1].length > 200 ? "..." : "");
        }
      } catch (e) {
        // Fall through to return original content
      }
    }
    
    // If it looks like raw JSON data, return generic message
    if (content.startsWith("{") || content.includes("'source':")) {
      return "Tweet content not available";
    }
    
    return content.substring(0, 200) + (content.length > 200 ? "..." : "");
  }

  formatNumber(num) {
    if (num === null || num === undefined) return "0";
    if (num >= 1e9) return (num / 1e9).toFixed(1) + "B";
    if (num >= 1e6) return (num / 1e6).toFixed(1) + "M";
    if (num >= 1e3) return (num / 1e3).toFixed(1) + "K";
    return num.toString();
  }

  formatDate(dateString) {
    if (!dateString) return "Unknown date";
    
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffInHours = (now - date) / (1000 * 60 * 60);
      
      if (diffInHours < 1) {
        const diffInMinutes = Math.floor((now - date) / (1000 * 60));
        return `${diffInMinutes}m ago`;
      } else if (diffInHours < 24) {
        return `${Math.floor(diffInHours)}h ago`;
      } else if (diffInHours < 168) { // 7 days
        return `${Math.floor(diffInHours / 24)}d ago`;
      } else {
        return date.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        });
      }
    } catch (error) {
      return "Invalid date";
    }
  }

  escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize the Twitter page
document.addEventListener("DOMContentLoaded", () => {
  new TwitterPage();
}); 
}); 