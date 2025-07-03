#!/usr/bin/env python3
"""
Enhanced Twitter Playwright Crawler with Google Cloud Storage Integration
Crawls Twitter for Solana-focused content using Playwright with direct GCS upload.
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Google Cloud Storage imports
try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print(
        "Warning: Google Cloud Storage not available. Install with: pip install google-cloud-storage"
    )

try:
    from playwright.async_api import async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not available. Install with: pip install playwright")

from textblob import TextBlob

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedTwitterPlaywrightCrawler:
    def __init__(
        self,
        headless: bool = True,
        output_dir: str = "output",
        username: str = None,
        password: str = None,
        cookies_path: str = None,
        user_agent: str = None,
        gcs_bucket: str = "degen-digest-data",
        project_id: str = "lucky-union-463615-t3",
    ):
        self.headless = headless
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.username = username
        self.password = password
        self.cookies_path = cookies_path
        self.user_agent = (
            user_agent
            or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Google Cloud Storage configuration
        self.gcs_bucket_name = gcs_bucket
        self.project_id = project_id
        self.gcs_client = None
        self.gcs_bucket = None

        # Initialize Google Cloud Storage
        if GCS_AVAILABLE:
            try:
                self.gcs_client = storage.Client(project=project_id)
                self.gcs_bucket = self.gcs_client.bucket(gcs_bucket)
                # Create bucket if it doesn't exist
                if not self.gcs_bucket.exists():
                    self.gcs_bucket.create(project=project_id)
                    logger.info(
                        f"Created GCS bucket: {gcs_bucket} in project: {project_id}"
                    )
                else:
                    logger.info(
                        f"Using existing GCS bucket: {gcs_bucket} in project: {project_id}"
                    )
            except Exception as e:
                logger.error(
                    f"Error accessing GCS bucket {gcs_bucket} in project {project_id}: {e}"
                )
                self.gcs_bucket = None
        else:
            logger.warning(
                "Google Cloud Storage not available - tweets will only be saved locally"
            )

        # Playwright components
        self.playwright = None
        self.browser = None
        self.page = None
        self.is_logged_in = False

        # Solana-focused search queries
        self.search_queries = [
            "solana",
            "sol",
            "solana nft",
            "solana defi",
            "solana meme",
            "solana pump",
            "solana airdrop",
            "solana ecosystem",
            "phantom wallet",
            "solflare",
            "raydium",
            "orca",
            "serum",
            "jupiter",
            "pyth",
            "bonk",
            "dogwifhat",
            "samoyedcoin",
            "solana gaming",
            "solana art",
        ]

        # User agents to rotate
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]

    async def setup_browser(self):
        """Initialize Playwright browser with enhanced stealth and cookies"""
        self.playwright = await async_playwright().start()

        # Use provided or random user agent
        ua = self.user_agent or random.choice(self.user_agents)

        # Launch browser with enhanced stealth settings
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
            ],
        )

        # Create context with enhanced stealth settings
        context = await self.browser.new_context(
            user_agent=ua,
            viewport={
                "width": random.choice([1920, 1366, 1440, 1536]),
                "height": random.choice([1080, 768, 900, 864]),
            },
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            },
        )

        # Load cookies if provided
        if self.cookies_path:
            try:
                with open(self.cookies_path, encoding="utf-8") as f:
                    cookies = json.load(f)
                await context.add_cookies(cookies)
                logger.info(f"Loaded {len(cookies)} cookies from {self.cookies_path}")
            except Exception as e:
                logger.warning(f"Could not load cookies: {e}")

        self.page = await context.new_page()

        # Add enhanced stealth scripts
        await self.page.add_init_script(
            """
            // Override webdriver property
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            // Override languages
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            // Fake Chrome object
            window.chrome = { runtime: {} };
            // Fake user activation
            Object.defineProperty(document, 'hasFocus', { value: () => true });
            // Randomize window properties
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            // Randomize touch support
            Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 1 });
            // Randomize platform
            Object.defineProperty(navigator, 'platform', { get: () => 'MacIntel' });
        """
        )

        # Add random delay to mimic human
        await asyncio.sleep(random.uniform(1.5, 3.5))

    async def login_to_twitter(self):
        """Login to Twitter using provided credentials"""
        if not self.username or not self.password:
            logger.warning("No credentials provided, skipping login")
            return False

        try:
            logger.info("Attempting to login to Twitter...")

            # Go to Twitter login page
            await self.page.goto("https://twitter.com/login", wait_until="networkidle")
            await asyncio.sleep(2)

            # Enter username
            username_input = await self.page.wait_for_selector(
                'input[autocomplete="username"]', timeout=10000
            )
            await username_input.fill(self.username)
            await asyncio.sleep(1)

            # Click Next (try multiple selectors)
            next_selectors = [
                'div[data-testid="SignupButton"]',
                'div[data-testid="LoginButton"]',
                'div[role="button"]:has-text("Next")',
                'div[role="button"]:has-text("Log in")',
                'button:has-text("Next")',
                'button:has-text("Log in")',
            ]
            next_button = None
            for selector in next_selectors:
                try:
                    next_button = await self.page.wait_for_selector(
                        selector, timeout=3000
                    )
                    if next_button:
                        break
                except Exception:
                    continue
            if next_button:
                await next_button.click()
                await asyncio.sleep(2)
            else:
                await self.page.keyboard.press("Enter")
                await asyncio.sleep(2)

            # Enter password
            password_input = await self.page.wait_for_selector(
                'input[name="password"]', timeout=10000
            )
            await password_input.fill(self.password)
            await asyncio.sleep(1)

            # Click Login (try multiple selectors)
            login_selectors = [
                'div[data-testid="LoginButton"]',
                'div[role="button"]:has-text("Log in")',
                'button:has-text("Log in")',
                'div[data-testid="SignupButton"]',
            ]
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = await self.page.wait_for_selector(
                        selector, timeout=3000
                    )
                    if login_button:
                        break
                except Exception:
                    continue
            if login_button:
                await login_button.click()
            else:
                await self.page.keyboard.press("Enter")
            await asyncio.sleep(5)

            # Check if login was successful (try multiple selectors)
            success_selectors = [
                'a[data-testid="AppTabBar_Home_Link"]',
                'a[data-testid="SideNav_Home_Link"]',
                'div[data-testid="tweetTextarea_0"]',
                'div[aria-label*="Timeline: Your Home Timeline"]',
                'div[aria-label*="Profile"]',
                'nav[role="navigation"]',
            ]
            for selector in success_selectors:
                try:
                    el = await self.page.wait_for_selector(selector, timeout=5000)
                    if el:
                        logger.info(
                            f"Successfully logged in to Twitter (found {selector})"
                        )
                        self.is_logged_in = True
                        return True
                except Exception:
                    continue
            logger.error(
                "Login failed - could not find any home/profile/tweet elements"
            )
            return False

        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False

    async def get_followed_accounts(self, max_accounts: int = 50) -> list[str]:
        """Get list of followed accounts"""
        try:
            logger.info("Getting followed accounts...")

            # Go to profile page
            await self.page.goto("https://twitter.com/home", wait_until="networkidle")
            await asyncio.sleep(2)

            # Click on Following tab
            following_selectors = [
                'a[href="/following"]',
                'a[href*="following"]',
                'div[role="tab"]:has-text("Following")',
                'a:has-text("Following")',
            ]

            following_link = None
            for selector in following_selectors:
                try:
                    following_link = await self.page.wait_for_selector(
                        selector, timeout=5000
                    )
                    if following_link:
                        break
                except Exception:
                    continue

            if following_link:
                await following_link.click()
                await asyncio.sleep(3)

                # Extract usernames
                username_selectors = [
                    'a[data-testid="User-Name"]',
                    'a[role="link"]',
                    'div[data-testid="UserCell"] a[href^="/"]',
                ]

                usernames = []
                for selector in username_selectors:
                    try:
                        elements = await self.page.query_selector_all(selector)
                        for element in elements[:max_accounts]:
                            href = await element.get_attribute("href")
                            if href and href.startswith("/") and len(href) > 1:
                                username = href[1:]  # Remove leading slash
                                if (
                                    username not in usernames
                                    and not username.startswith("i/")
                                ):
                                    usernames.append(username)
                        if usernames:
                            break
                    except Exception:
                        continue

                logger.info(f"Found {len(usernames)} followed accounts")
                return usernames
            else:
                logger.warning("Could not find Following tab")
                return []

        except Exception as e:
            logger.error(f"Error getting followed accounts: {e}")
            return []

    async def get_user_tweets(
        self, username: str, max_tweets: int = 20
    ) -> list[dict[str, Any]]:
        """Get tweets from a specific user"""
        try:
            logger.info(f"Getting tweets from @{username}")
            self.current_query = f"user:{username}"

            # Navigate to user's profile
            profile_url = f"https://twitter.com/{username}"
            await self.page.goto(profile_url, wait_until="networkidle")
            await asyncio.sleep(3)

            # Try to find tweets
            tweet_selectors = [
                'article[data-testid="tweet"]',
                'article[data-testid="cellInnerDiv"]',
                'div[data-testid="tweet"]',
                'article[role="article"]',
            ]

            tweets_found = False
            for selector in tweet_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    tweets_found = True
                    break
                except Exception:
                    continue

            if not tweets_found:
                logger.warning(f"No tweets found for @{username}")
                return []

            # Scroll to load more tweets
            tweets_loaded = 0
            max_scrolls = 3

            for scroll in range(max_scrolls):
                if tweets_loaded >= max_tweets:
                    break

                await self.page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(2)

                for selector in tweet_selectors:
                    try:
                        tweet_elements = await self.page.query_selector_all(selector)
                        if tweet_elements:
                            tweets_loaded = len(tweet_elements)
                            break
                    except Exception:
                        continue

            # Extract tweets
            tweets = await self.extract_tweets_enhanced(max_tweets)
            logger.info(f"Extracted {len(tweets)} tweets from @{username}")

            return tweets

        except Exception as e:
            logger.error(f"Error getting tweets from @{username}: {e}")
            return []

    async def get_for_you_tweets(self, max_tweets: int = 30) -> list[dict[str, Any]]:
        """Get tweets from the For You page"""
        try:
            logger.info("Getting tweets from For You page...")
            await self.page.goto("https://twitter.com/home", wait_until="networkidle")
            await asyncio.sleep(3)

            # Human-like scrolling
            await self.human_like_scroll(max_scrolls=8, max_tweets=max_tweets)

            # Extract tweets
            tweets = await self.extract_tweets_enhanced(max_tweets)
            logger.info(f"Extracted {len(tweets)} tweets from For You page")
            return tweets
        except Exception as e:
            logger.error(f"Error getting For You tweets: {e}")
            return []

    async def get_saved_post_comments(
        self, max_posts: int = 10
    ) -> list[dict[str, Any]]:
        """Get comments from saved posts"""
        try:
            logger.info("Getting comments from saved posts...")

            # Navigate to bookmarks/saved posts
            await self.page.goto(
                "https://twitter.com/i/bookmarks", wait_until="networkidle"
            )
            await asyncio.sleep(3)

            # Try to find saved posts
            post_selectors = [
                'article[data-testid="tweet"]',
                'article[data-testid="cellInnerDiv"]',
                'div[data-testid="tweet"]',
                'article[role="article"]',
            ]

            posts_found = False
            for selector in post_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    posts_found = True
                    break
                except Exception:
                    continue

            if not posts_found:
                logger.warning("No saved posts found")
                return []

            # Get saved posts
            saved_posts = []
            for selector in post_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        saved_posts = elements[:max_posts]
                        break
                except Exception:
                    continue

            all_comments = []

            # For each saved post, try to get comments
            for i, post in enumerate(saved_posts[:max_posts]):
                try:
                    # Click on the post to open it
                    await post.click()
                    await asyncio.sleep(2)

                    # Look for comments/replies
                    comment_selectors = [
                        'article[data-testid="tweet"]',
                        'div[data-testid="reply"]',
                        'div[data-testid="cellInnerDiv"]',
                    ]

                    comments = []
                    for selector in comment_selectors:
                        try:
                            comment_elements = await self.page.query_selector_all(
                                selector
                            )
                            if comment_elements:
                                # Extract comment data (similar to tweet extraction)
                                for comment_element in comment_elements[
                                    :5
                                ]:  # Limit comments per post
                                    comment_data = (
                                        await self.extract_single_tweet_enhanced(
                                            comment_element
                                        )
                                    )
                                    if comment_data:
                                        comment_data[
                                            "source_type"
                                        ] = "saved_post_comment"
                                        comment_data["parent_post_index"] = i
                                        comments.append(comment_data)
                                break
                        except Exception:
                            continue

                    all_comments.extend(comments)
                    logger.info(f"Found {len(comments)} comments from saved post {i+1}")

                    # Go back to bookmarks page
                    await self.page.go_back()
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.warning(f"Error processing saved post {i+1}: {e}")
                    continue

            logger.info(
                f"Extracted {len(all_comments)} total comments from saved posts"
            )
            return all_comments

        except Exception as e:
            logger.error(f"Error getting saved post comments: {e}")
            return []

    async def search_twitter(
        self, query: str, max_tweets: int = 20
    ) -> list[dict[str, Any]]:
        """Search Twitter for a specific query with enhanced selectors"""
        logger.info(f"Searching Twitter for: {query}")
        self.current_query = query

        try:
            # Navigate to Twitter search with different URL format
            search_url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
            await self.page.goto(search_url, wait_until="networkidle", timeout=30000)

            # Wait a bit for page to load
            await asyncio.sleep(3)

            # Try multiple selectors for tweets
            tweet_selectors = [
                'article[data-testid="tweet"]',
                'article[data-testid="cellInnerDiv"]',
                'div[data-testid="tweet"]',
                'article[role="article"]',
                'div[data-testid="tweetText"]',
            ]

            tweets_found = False
            for selector in tweet_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    tweets_found = True
                    logger.info(f"Found tweets using selector: {selector}")
                    break
                except Exception:
                    continue

            if not tweets_found:
                logger.warning(f"No tweets found for query: {query}")
                return []

            # Scroll to load more tweets
            tweets_loaded = 0
            max_scrolls = 5

            for scroll in range(max_scrolls):
                if tweets_loaded >= max_tweets:
                    break

                # Scroll down
                await self.page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(2)

                # Count current tweets using multiple selectors
                for selector in tweet_selectors:
                    try:
                        tweet_elements = await self.page.query_selector_all(selector)
                        if tweet_elements:
                            tweets_loaded = len(tweet_elements)
                            logger.info(
                                f"Loaded {tweets_loaded} tweets for '{query}' (scroll {scroll + 1})"
                            )
                            break
                    except Exception:
                        continue

            # Extract tweet data
            tweets = await self.extract_tweets_enhanced(max_tweets)
            logger.info(f"Extracted {len(tweets)} tweets for '{query}'")

            return tweets

        except Exception as e:
            logger.error(f"Error searching Twitter for '{query}': {e}")
            return []

    async def extract_tweets_enhanced(self, max_tweets: int) -> list[dict[str, Any]]:
        """Extract tweet data with enhanced selectors"""
        tweets = []

        try:
            # Try multiple selectors to find tweets
            selectors_to_try = [
                'article[data-testid="tweet"]',
                'article[data-testid="cellInnerDiv"]',
                'div[data-testid="tweet"]',
                'article[role="article"]',
            ]

            tweet_elements = []
            for selector in selectors_to_try:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        tweet_elements = elements
                        logger.info(f"Using selector: {selector}")
                        break
                except Exception:
                    continue

            for i, tweet_element in enumerate(tweet_elements[:max_tweets]):
                try:
                    tweet_data = await self.extract_single_tweet_enhanced(tweet_element)
                    if tweet_data:
                        tweets.append(tweet_data)
                except Exception as e:
                    logger.warning(f"Error extracting tweet {i}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting tweets: {e}")

        return tweets

    async def extract_single_tweet_enhanced(
        self, tweet_element
    ) -> dict[str, Any] | None:
        """Extract data from a single tweet with enhanced selectors"""
        try:
            # Try multiple selectors for tweet text
            text_selectors = [
                '[data-testid="tweetText"]',
                "div[lang]",
                'span[dir="auto"]',
                'div[data-testid="tweetText"] span',
            ]

            text = ""
            for selector in text_selectors:
                try:
                    text_element = await tweet_element.query_selector(selector)
                    if text_element:
                        text = await text_element.inner_text()
                        if text.strip():
                            break
                except Exception:
                    continue

            if not text.strip():
                return None

            # Extract username with multiple selectors
            username_selectors = [
                'a[role="link"]',
                'a[data-testid="User-Name"]',
                'a[href^="/"]',
            ]

            username = ""
            for selector in username_selectors:
                try:
                    username_element = await tweet_element.query_selector(selector)
                    if username_element:
                        href = await username_element.get_attribute("href")
                        if href and href.startswith("/") and len(href) > 1:
                            username = href[1:]  # Remove leading slash
                            break
                except Exception:
                    continue

            # Extract timestamp
            time_selectors = ["time", '[data-testid="tweetText"] time']
            timestamp = ""
            for selector in time_selectors:
                try:
                    time_element = await tweet_element.query_selector(selector)
                    if time_element:
                        timestamp = await time_element.get_attribute("datetime")
                        if timestamp:
                            break
                except Exception:
                    continue

            # Extract engagement metrics
            engagement = await self.extract_engagement_enhanced(tweet_element)

            # Analyze sentiment
            sentiment = self.analyze_sentiment(text)

            # Create tweet object
            tweet_data = {
                "source": "twitter_playwright_enhanced",
                "id": f"playwright_{int(time.time())}_{random.randint(1000,9999)}",
                "text": text,
                "username": username,
                "created_at": timestamp or datetime.now(timezone.utc).isoformat(),
                "engagement": engagement,
                "sentiment": sentiment,
                "query": self.current_query,
                "collected_at": datetime.now(timezone.utc).isoformat(),
            }

            return tweet_data

        except Exception as e:
            logger.warning(f"Error extracting single tweet: {e}")
            return None

    async def extract_engagement_enhanced(self, tweet_element) -> dict[str, int]:
        """Extract engagement metrics with enhanced selectors"""
        engagement = {"likes": 0, "retweets": 0, "replies": 0, "views": 0}

        try:
            # Try multiple selectors for engagement buttons
            engagement_selectors = {
                "likes": [
                    '[data-testid="like"]',
                    '[data-testid="unlike"]',
                    'div[aria-label*="Like"]',
                ],
                "retweets": [
                    '[data-testid="retweet"]',
                    '[data-testid="unretweet"]',
                    'div[aria-label*="Retweet"]',
                ],
                "replies": [
                    '[data-testid="reply"]',
                    'div[aria-label*="Reply"]',
                ],
            }

            for metric, selectors in engagement_selectors.items():
                for selector in selectors:
                    try:
                        element = await tweet_element.query_selector(selector)
                        if element:
                            text = await element.inner_text()
                            if metric == "likes":
                                engagement["likes"] = self.parse_engagement_count(text)
                            elif metric == "retweets":
                                engagement["retweets"] = self.parse_engagement_count(
                                    text
                                )
                            elif metric == "replies":
                                engagement["replies"] = self.parse_engagement_count(
                                    text
                                )
                            break
                    except Exception:
                        continue

        except Exception as e:
            logger.warning(f"Error extracting engagement: {e}")

        return engagement

    def parse_engagement_count(self, text: str) -> int:
        """Parse engagement count from text (e.g., '1.2K' -> 1200)"""
        if not text or text.strip() == "":
            return 0

        text = text.strip().lower()

        try:
            if "k" in text:
                return int(float(text.replace("k", "")) * 1000)
            elif "m" in text:
                return int(float(text.replace("m", "")) * 1000000)
            else:
                return int(text)
        except Exception:
            return 0

    def analyze_sentiment(self, text: str) -> dict[str, float]:
        """Analyze sentiment of tweet text"""
        try:
            blob = TextBlob(text)
            return {
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity,
            }
        except Exception:
            return {"polarity": 0.0, "subjectivity": 0.0}

    async def run_single_crawl(
        self, max_tweets_per_query: int = 10
    ) -> list[dict[str, Any]]:
        """Run a single crawl session"""
        logger.info("Starting enhanced Playwright Twitter crawl session...")

        try:
            await self.setup_browser()

            # Login if credentials provided
            if self.username and self.password:
                login_success = await self.login_to_twitter()
                if not login_success:
                    logger.warning("Login failed, continuing without authentication")

            all_tweets = []

            # Search for each query (limit to first 3 for testing)
            for query in self.search_queries[:3]:
                logger.info(f"Searching for: {query}")
                tweets = await self.search_twitter(query, max_tweets_per_query)
                all_tweets.extend(tweets)

                # Small delay between queries
                await asyncio.sleep(3)

            # Save results
            if all_tweets:
                await self.save_tweets(all_tweets)

            logger.info(
                f"Enhanced crawl session completed: {len(all_tweets)} tweets collected"
            )
            return all_tweets

        except Exception as e:
            logger.error(f"Error in enhanced crawl session: {e}")
            return []
        finally:
            await self.cleanup()

    async def run_solana_focused_crawl(
        self,
        max_for_you_tweets: int = 30,
        max_followed_accounts: int = 20,
        max_tweets_per_user: int = 10,
        max_saved_posts: int = 10,
    ) -> list[dict[str, Any]]:
        """Run a Solana-focused crawl using For You page and saved posts"""
        logger.info("Starting Solana-focused Twitter crawl session...")

        try:
            await self.setup_browser()

            # Login if credentials provided
            if self.username and self.password:
                login_success = await self.login_to_twitter()
                if not login_success:
                    logger.warning("Login failed, continuing without authentication")

            all_tweets = []
            for_you_tweets = []
            followed_tweets = []
            saved_comments = []
            discovered_users = set()

            # 1. Get tweets from For You page
            if self.is_logged_in:
                logger.info("🎯 Getting tweets from For You page...")
                for_you_tweets = await self.get_for_you_tweets(max_for_you_tweets)

                # Extract usernames from For You tweets for later discovery
                for tweet in for_you_tweets:
                    username = tweet.get("username", "")
                    if username:
                        discovered_users.add(username)
                    tweet["source_type"] = "for_you_page"

            # 2. Get followed accounts and their tweets (ALL tweets, no filtering)
            if self.is_logged_in:
                logger.info("👥 Getting followed accounts...")
                followed_accounts = await self.get_followed_accounts(
                    max_followed_accounts
                )

                if followed_accounts:
                    logger.info(
                        f"📱 Scanning {len(followed_accounts)} followed accounts..."
                    )
                    for username in followed_accounts[
                        :10
                    ]:  # Limit to first 10 for performance
                        try:
                            user_tweets = await self.get_user_tweets(
                                username, max_tweets_per_user
                            )

                            # Mark all followed account tweets
                            for tweet in user_tweets:
                                tweet["source_type"] = "followed_account"
                                tweet["followed_username"] = username

                            followed_tweets.extend(user_tweets)
                            logger.info(
                                f"Collected {len(user_tweets)} tweets from @{username}"
                            )
                            await asyncio.sleep(1)  # Small delay between users
                        except Exception as e:
                            logger.warning(
                                f"Error getting tweets from @{username}: {e}"
                            )
                            continue

            # 3. Get comments from saved posts
            if self.is_logged_in:
                logger.info("💾 Getting comments from saved posts...")
                saved_comments = await self.get_saved_post_comments(max_saved_posts)

                # Extract usernames from saved post comments
                for comment in saved_comments:
                    username = comment.get("username", "")
                    if username:
                        discovered_users.add(username)
                    comment["source_type"] = "saved_post_comment"

            # 4. Discover and get tweets from users found in For You and saved posts
            discovered_tweets = []
            if discovered_users:
                logger.info(
                    f"🔍 Discovering tweets from {len(discovered_users)} users..."
                )
                for username in list(discovered_users)[
                    :5
                ]:  # Limit to first 5 for performance
                    try:
                        user_tweets = await self.get_user_tweets(
                            username, max_tweets_per_user
                        )

                        # Mark discovered user tweets
                        for tweet in user_tweets:
                            tweet["source_type"] = "discovered_user"
                            tweet["discovery_source"] = "for_you_or_saved"

                        discovered_tweets.extend(user_tweets)
                        logger.info(
                            f"Collected {len(user_tweets)} tweets from discovered user @{username}"
                        )
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.warning(
                            f"Error getting tweets from discovered user @{username}: {e}"
                        )
                        continue

            # Combine all tweets
            all_tweets = (
                for_you_tweets + followed_tweets + saved_comments + discovered_tweets
            )

            # Log statistics
            logger.info("📊 Crawl Statistics:")
            logger.info(f"   - For You page tweets: {len(for_you_tweets)}")
            logger.info(f"   - Followed account tweets: {len(followed_tweets)}")
            logger.info(f"   - Saved post comments: {len(saved_comments)}")
            logger.info(f"   - Discovered user tweets: {len(discovered_tweets)}")
            logger.info(f"   - Total tweets collected: {len(all_tweets)}")

            # Save results
            if all_tweets:
                await self.save_tweets(all_tweets)

            logger.info(
                f"Solana-focused crawl completed: {len(all_tweets)} total tweets collected"
            )
            return all_tweets

        except Exception as e:
            logger.error(f"Error in Solana-focused crawl session: {e}")
            return []
        finally:
            await self.cleanup()

    async def save_tweets(self, tweets: list[dict[str, Any]]):
        """Save tweets to both local file and Google Cloud Storage"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"twitter_playwright_enhanced_{timestamp}.json"
            filepath = self.output_dir / filename

            data = {
                "tweets": tweets,
                "metadata": {
                    "total_tweets": len(tweets),
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                    "source": "twitter_playwright_enhanced",
                    "crawler_version": "2.0",
                    "gcs_uploaded": True,
                },
            }

            # Save locally
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            # Also save as latest locally
            latest_file = self.output_dir / "twitter_playwright_enhanced_latest.json"
            with open(latest_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Saved {len(tweets)} tweets locally to {filename}")

            # Upload to Google Cloud Storage
            if self.gcs_bucket and GCS_AVAILABLE:
                try:
                    # Upload timestamped file
                    cloud_path = f"data/twitter_playwright_enhanced_{timestamp}.json"
                    blob = self.gcs_bucket.blob(cloud_path)
                    blob.upload_from_filename(str(filepath))
                    logger.info(f"Uploaded to GCS: {cloud_path}")

                    # Upload as latest
                    latest_cloud_path = "data/twitter_playwright_enhanced_latest.json"
                    blob_latest = self.gcs_bucket.blob(latest_cloud_path)
                    blob_latest.upload_from_filename(str(latest_file))
                    logger.info(f"Uploaded latest to GCS: {latest_cloud_path}")

                    # Update metadata to indicate successful GCS upload
                    data["metadata"]["gcs_uploaded"] = True
                    data["metadata"]["gcs_path"] = cloud_path
                    data["metadata"]["gcs_latest_path"] = latest_cloud_path

                except Exception as e:
                    logger.error(f"Error uploading to GCS: {e}")
                    data["metadata"]["gcs_uploaded"] = False
                    data["metadata"]["gcs_error"] = str(e)
            else:
                logger.warning("GCS not available - tweets saved locally only")
                data["metadata"]["gcs_uploaded"] = False

        except Exception as e:
            logger.error(f"Error saving tweets: {e}")

    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, "playwright"):
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    async def human_like_scroll(self, max_scrolls: int = 10, max_tweets: int = 30):
        """Simulate human-like scrolling on the current page"""
        tweets_loaded = 0
        for scroll in range(max_scrolls):
            # Random scroll amount and direction
            if random.random() < 0.85:
                scroll_amount = random.randint(400, 1200)
            else:
                scroll_amount = -random.randint(200, 600)
            await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")

            # Random pause
            pause = random.uniform(1.0, 4.0)
            if random.random() < 0.15:
                pause += random.uniform(2.0, 5.0)  # Occasionally wait longer
            await asyncio.sleep(pause)

            # Optionally, randomly click or hover on a tweet
            if random.random() < 0.2:
                try:
                    tweet_elements = await self.page.query_selector_all(
                        'article[data-testid="tweet"]'
                    )
                    if tweet_elements:
                        tweet = random.choice(tweet_elements)
                        if random.random() < 0.5:
                            await tweet.hover()
                        else:
                            await tweet.click()
                            await asyncio.sleep(random.uniform(1.0, 2.5))
                            await self.page.go_back()
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                except Exception as e:
                    logger.debug(f"Human-like interaction failed: {e}")

            # Check how many tweets are loaded
            tweet_elements = await self.page.query_selector_all(
                'article[data-testid="tweet"]'
            )
            tweets_loaded = len(tweet_elements)
            if tweets_loaded >= max_tweets:
                break


async def main():
    """Main function for testing"""
    crawler = EnhancedTwitterPlaywrightCrawler(headless=True)
    tweets = await crawler.run_single_crawl(max_tweets_per_query=5)
    print(f"Collected {len(tweets)} tweets")


if __name__ == "__main__":
    asyncio.run(main())
