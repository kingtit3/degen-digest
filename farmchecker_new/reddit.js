// FarmChecker.xyz - Reddit Page
class RedditPage {
  constructor() {
    this.apiBase = "/api";
    this.data = {
      redditPosts: [],
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
      await this.loadRedditPosts();
    } catch (error) {
      console.error("Error loading data:", error);
    }
  }

      async loadRedditPosts() {
        try {
            const response = await fetch(`${this.apiBase}/reddit?sort=${this.currentSort}`);
            this.data.redditPosts = await response.json();
        } catch (error) {
            console.error("Error loading Reddit posts:", error);
            this.data.redditPosts = [];
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

    // Reddit filter
    const redditFilter = document.getElementById("reddit-filter");
    if (redditFilter) {
      redditFilter.addEventListener("change", (e) => {
        this.currentSort = e.target.value;
        this.loadData();
      });
    }
  }

  updateUI() {
    this.updateRedditPosts();
  }

  updateRedditPosts() {
    const container = document.getElementById("reddit-posts");
    if (!container) return;

    if (this.data.redditPosts.length === 0) {
      container.innerHTML = '<div class="loading">No Reddit posts available</div>';
      return;
    }

    container.innerHTML = this.data.redditPosts
      .map(
        (post) => `
            <div class="post-card reddit-post">
                <div class="post-header">
                    <div class="post-author-info">
                        <div class="author-avatar">
                            <i class="fab fa-reddit"></i>
                        </div>
                        <div class="author-details">
                            <div class="author-name">${this.escapeHtml(
                              this.cleanRedditAuthor(post.author),
                            )}</div>
                            <div class="post-meta">
                                <span class="subreddit">
                                    <i class="fas fa-hashtag"></i> r/${this.escapeHtml(post.subreddit || 'cryptocurrency')}
                                </span>
                                <span class="post-time">
                                    <i class="fas fa-clock"></i> ${this.formatDate(post.published_at)}
                                </span>
                                ${post.is_original_content ? '<span class="oc-badge"><i class="fas fa-star"></i> OC</span>' : ''}
                            </div>
                        </div>
                    </div>
                    <div class="engagement-score">
                        <span class="badge">${this.formatNumber(post.score || 0)}</span>
                    </div>
                </div>
                <div class="post-content">
                    <div class="post-title">${this.escapeHtml(post.title)}</div>
                    ${post.content ? `<div class="post-text">${this.escapeHtml(this.cleanRedditContent(post.content))}</div>` : ''}
                    ${post.url ? `<div class="post-link"><a href="${post.url}" target="_blank" rel="noopener">View Post <i class="fas fa-external-link-alt"></i></a></div>` : ''}
                </div>
                <div class="post-engagement">
                    <div class="engagement-item">
                        <i class="fas fa-arrow-up"></i>
                        <span>${this.formatNumber(post.upvotes || 0)}</span>
                    </div>
                    <div class="engagement-item">
                        <i class="fas fa-arrow-down"></i>
                        <span>${this.formatNumber(post.downvotes || 0)}</span>
                    </div>
                    <div class="engagement-item">
                        <i class="fas fa-comment"></i>
                        <span>${this.formatNumber(post.comments || 0)}</span>
                    </div>
                    <div class="engagement-item">
                        <i class="fas fa-share"></i>
                        <span>${this.formatNumber(post.shares || 0)}</span>
                    </div>
                    ${post.gilded > 0 ? `
                    <div class="engagement-item">
                        <i class="fas fa-award"></i>
                        <span>${this.formatNumber(post.gilded)}</span>
                    </div>
                    ` : ''}
                </div>
            </div>
        `,
      )
      .join("");
  }

  cleanRedditAuthor(author) {
    if (!author || author === "Anonymous" || author === "anon") {
      return "Reddit User";
    }
    return author;
  }

  cleanRedditContent(content) {
    if (!content) return "Content not available";
    if (content === "Content available") return "Content not available";
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

// Initialize the Reddit page
document.addEventListener("DOMContentLoaded", () => {
  new RedditPage();
}); 
}); 