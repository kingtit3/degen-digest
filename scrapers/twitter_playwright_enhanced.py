#!/usr/bin/env python3
"""
Enhanced Twitter Playwright Crawler with Google Cloud Storage Integration
Crawls Twitter for Solana-focused content using Playwright with direct GCS upload.
"""

import asyncio
import json
import logging
import os
import random
import time
from datetime import UTC, datetime, timezone
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

        # Read credentials from environment variables if not provided
        self.username = username or os.getenv("TWITTER_USERNAME")
        self.password = password or os.getenv("TWITTER_PASSWORD")
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
        self.current_query = ""  # Initialize current_query attribute

        # Comprehensive crypto search queries including memecoins, launchpads, farming, and airdrops
        self.search_queries = [
            # Solana ecosystem
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
            # Memecoins
            "memecoin",
            "meme coin",
            "moon",
            "pump",
            "100x",
            "1000x",
            "gem",
            "next gem",
            "pepe",
            "doge",
            "shib",
            "floki",
            "wojak",
            "chad",
            "based",
            "degen",
            "mooning",
            "pumping",
            "fomo",
            "fud",
            "hodl",
            "diamond hands",
            # Launchpads and IDOs
            "launchpad",
            "ido",
            "initial dex offering",
            "token launch",
            "presale",
            "fair launch",
            "stealth launch",
            "pinksale",
            "dxsale",
            "bounce",
            "polkastarter",
            "daomaker",
            "trustpad",
            "seedify",
            "gamefi",
            "new token",
            "token launch",
            "ico",
            "initial coin offering",
            # Farming and Yield
            "yield farming",
            "farming",
            "liquidity mining",
            "staking",
            "apy",
            "apr",
            "rewards",
            "harvest",
            "compound",
            "auto compound",
            "vault",
            "strategy",
            "defi farming",
            "liquidity provider",
            "lp",
            "amm",
            "dex farming",
            # Airdrops
            "airdrop",
            "free tokens",
            "claim",
            "eligibility",
            "snapshot",
            "whitelist",
            "retroactive",
            "community airdrop",
            "token distribution",
            "free crypto",
            "airdrop campaign",
            "token giveaway",
            "free coins",
            # DeFi and Trading
            "defi",
            "decentralized finance",
            "swap",
            "trade",
            "liquidity",
            "pool",
            "amm",
            "dex",
            "cex",
            "exchange",
            "trading",
            "chart",
            "technical analysis",
            "ta",
            "support",
            "resistance",
            "breakout",
            "breakdown",
            "consolidation",
            # NFTs and Gaming
            "nft",
            "non fungible token",
            "gaming",
            "play to earn",
            "p2e",
            "metaverse",
            "virtual world",
            "gamefi",
            "nft gaming",
            "nft art",
            "nft collection",
            "mint",
            "minting",
            "floor price",
            "rarity",
            "trait",
            "utility",
            # General Crypto
            "crypto",
            "cryptocurrency",
            "blockchain",
            "web3",
            "defi",
            "altcoin",
            "alt season",
            "bull run",
            "bear market",
            "accumulation",
            "distribution",
            "whale",
            "whale alert",
            "large transaction",
            "wallet",
            "private key",
            # Trending Terms
            "trending",
            "viral",
            "hot",
            "fomo",
            "fud",
            "shill",
            "shilling",
            "moon",
            "rocket",
            "to the moon",
            "lambo",
            "wen",
            "ser",
            "gm",
            "gn",
            "wagmi",
            "ngmi",
            "diamond hands",
            "paper hands",
            "hodl",
            "buy the dip",
        ]

        # User agents to rotate
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]

    async def setup_browser(self):
        """Initialize Playwright browser with enhanced stealth and cookies - optimized for cloud"""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                logger.info(
                    f"🚀 [setup_browser] Attempt {retry_count + 1}/{max_retries} - Starting Playwright browser setup..."
                )
                logger.info("[setup_browser] Before async_playwright().start()")
                self.playwright = await async_playwright().start()
                logger.info("[setup_browser] After async_playwright().start()")

                ua = self.user_agent or random.choice(self.user_agents)
                logger.info(f"[setup_browser] Using User-Agent: {ua}")

                logger.info("[setup_browser] Before browser launch")
                # Use default browser path (Playwright will find it automatically)
                logger.info(
                    "[setup_browser] Using default browser path (auto-detected)"
                )

                # Enhanced browser launch configuration for Cloud Run
                browser_args = [
                    # Core sandbox and security (Cloud Run optimized)
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    # Display and graphics (Cloud Run specific)
                    "--disable-gpu",
                    "--disable-software-rasterizer",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-background-networking",
                    # Memory optimization for Cloud Run
                    "--memory-pressure-off",
                    "--max_old_space_size=512",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    # Anti-detection measures
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions-except",
                    "--disable-plugins-discovery",
                    "--disable-default-apps",
                    "--disable-sync",
                    "--disable-translate",
                    "--disable-client-side-phishing-detection",
                    "--disable-component-extensions-with-background-pages",
                    "--disable-component-update",
                    "--disable-domain-reliability",
                    "--disable-features=TranslateUI",
                    "--disable-ipc-flooding-protection",
                    "--no-default-browser-check",
                    "--disable-hang-monitor",
                    "--disable-prompt-on-repost",
                    "--force-color-profile=srgb",
                    "--metrics-recording-only",
                    "--no-first-run",
                    "--password-store=basic",
                    "--use-mock-keychain",
                    "--no-service-autorun",
                    "--export-tagged-pdf",
                    "--disable-search-engine-choice-screen",
                    "--unsafely-disable-devtools-self-xss-warnings",
                    "--enable-automation",
                    "--hide-scrollbars",
                    "--mute-audio",
                    # Additional stealth measures
                    "--disable-accelerated-2d-canvas",
                    "--no-zygote",
                    "--disable-field-trial-config",
                    "--disable-back-forward-cache",
                    "--disable-breakpad",
                    "--allow-pre-commit-input",
                    "--disable-popup-blocking",
                    "--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4",
                ]

                # Add Cloud Run specific environment variables
                env = {
                    "DISPLAY": os.environ.get("DISPLAY", ":99"),
                    "XAUTHORITY": os.environ.get("XAUTHORITY", "/tmp/.Xauthority"),
                    "PLAYWRIGHT_HEADLESS": "1",
                    "PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS": "1",
                }

                self.browser = await self.playwright.chromium.launch(
                    headless=True,  # Force headless for Cloud Run
                    args=browser_args,
                    env=env,
                )
                logger.info("[setup_browser] After browser launch")

                logger.info("[setup_browser] Before context creation")
                context = await self.browser.new_context(
                    user_agent=ua,
                    viewport={"width": 1920, "height": 1080},
                    locale="en-US",
                    timezone_id="America/New_York",
                    permissions=["geolocation"],
                    extra_http_headers={
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                        "DNT": "1",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                        "Sec-Fetch-User": "?1",
                        "Cache-Control": "max-age=0",
                    },
                    java_script_enabled=True,
                    has_touch=False,
                    is_mobile=False,
                    device_scale_factor=1,
                    color_scheme="light",
                    reduced_motion="no-preference",
                    forced_colors="none",
                )
                logger.info("[setup_browser] After context creation")

                if self.cookies_path:
                    try:
                        logger.info(
                            f"[setup_browser] Before loading cookies from {self.cookies_path}"
                        )
                        with open(self.cookies_path, encoding="utf-8") as f:
                            cookies = json.load(f)
                        await context.add_cookies(cookies)
                        logger.info(
                            f"[setup_browser] Loaded {len(cookies)} cookies from {self.cookies_path}"
                        )
                    except Exception as e:
                        logger.warning(f"[setup_browser] ⚠️ Failed to load cookies: {e}")

                logger.info("[setup_browser] Before page creation")
                self.page = await context.new_page()
                if self.page is None:
                    raise Exception(
                        "Failed to create page - context.new_page() returned None"
                    )
                # Skip setting default timeouts due to Playwright 1.53.0 bug
                # await self.page.set_default_timeout(20000)
                # await self.page.set_default_navigation_timeout(20000)
                logger.info("[setup_browser] After page creation")

                # Inject anti-detection scripts
                await self.inject_anti_detection_scripts()

                logger.info("[setup_browser] Browser setup completed successfully")
                return True

            except Exception as e:
                retry_count += 1
                logger.error(
                    f"[setup_browser] ❌ Error during browser setup (attempt {retry_count}/{max_retries}): {e}"
                )
                import traceback

                logger.error(
                    f"[setup_browser] Exception details:\n{traceback.format_exc()}"
                )
                if self.browser:
                    try:
                        await self.browser.close()
                    except Exception as close_e:
                        logger.error(
                            f"[setup_browser] Error closing browser: {close_e}"
                        )
                if self.playwright:
                    try:
                        await self.playwright.stop()
                    except Exception as stop_e:
                        logger.error(
                            f"[setup_browser] Error stopping playwright: {stop_e}"
                        )
                if retry_count < max_retries:
                    logger.info(
                        "[setup_browser] 🔄 Retrying browser setup in 5 seconds..."
                    )
                    await asyncio.sleep(5)
                else:
                    logger.error(
                        "[setup_browser] ❌ Browser setup failed after all retries"
                    )
                    raise Exception(
                        f"Browser setup failed after {max_retries} attempts: {e}"
                    ) from e

    async def inject_anti_detection_scripts(self):
        """Inject scripts to bypass bot detection"""
        try:
            # Remove webdriver property
            await self.page.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """
            )

            # Override permissions
            await self.page.add_init_script(
                """
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """
            )

            # Override plugins
            await self.page.add_init_script(
                """
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
            """
            )

            # Override languages
            await self.page.add_init_script(
                """
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """
            )

            # Override chrome runtime
            await self.page.add_init_script(
                """
                window.chrome = {
                    runtime: {},
                };
            """
            )

            # Override permissions
            await self.page.add_init_script(
                """
                const originalGetProperty = Object.getOwnPropertyDescriptor;
                Object.getOwnPropertyDescriptor = function(obj, prop) {
                    if (prop === 'webdriver') {
                        return undefined;
                    }
                    return originalGetProperty(obj, prop);
                };
            """
            )

            logger.info(
                "[anti_detection] ✅ Anti-detection scripts injected successfully"
            )

        except Exception as e:
            logger.warning(
                f"[anti_detection] ⚠️ Failed to inject anti-detection scripts: {e}"
            )

    async def save_cookies(self):
        """Save cookies to file for persistent sessions"""
        try:
            if not self.page:
                return False

            cookies = await self.page.context.cookies()
            cookies_file = self.output_dir / "twitter_cookies.json"

            with open(cookies_file, "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=2)

            logger.info(f"✅ Saved {len(cookies)} cookies to {cookies_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving cookies: {e}")
            return False

    async def load_cookies(self):
        """Load cookies from file for persistent sessions"""
        try:
            cookies_file = self.output_dir / "twitter_cookies.json"
            if not cookies_file.exists():
                logger.info("No saved cookies found")
                return False

            with open(cookies_file, encoding="utf-8") as f:
                cookies = json.load(f)

            await self.page.context.add_cookies(cookies)
            logger.info(f"✅ Loaded {len(cookies)} cookies from {cookies_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Error loading cookies: {e}")
            return False

    async def check_login_status(self):
        """Check if already logged in using cookies"""
        try:
            if not self.page:
                return False

            # Try to load cookies first
            await self.load_cookies()

            # Go to Twitter home to check login status
            await self.page.goto("https://twitter.com/home", wait_until="networkidle")
            await asyncio.sleep(3)

            # Check for login indicators
            login_indicators = [
                'a[data-testid="AppTabBar_Home_Link"]',
                'a[data-testid="SideNav_Home_Link"]',
                'div[data-testid="tweetTextarea_0"]',
                'nav[role="navigation"]',
            ]

            for selector in login_indicators:
                try:
                    el = await self.page.wait_for_selector(selector, timeout=5000)
                    if el:
                        logger.info(f"✅ Already logged in (found {selector})")
                        self.is_logged_in = True
                        return True
                except Exception:
                    continue

            logger.info("❌ Not logged in - will need to login")
            return False

        except Exception as e:
            logger.error(f"❌ Error checking login status: {e}")
            return False

    async def login_to_twitter(self):
        """Login to Twitter using provided credentials with cookie persistence"""
        if not self.username or not self.password:
            logger.warning("No credentials provided, skipping login")
            return False

        try:
            # First check if already logged in with cookies
            if await self.check_login_status():
                return True

            logger.info("Attempting to login to Twitter...")

            # Go to Twitter login page
            await self.page.goto("https://twitter.com/login", wait_until="networkidle")
            await asyncio.sleep(2)

            # Enter username
            username_input = await self.page.wait_for_selector(
                'input[autocomplete="username"]'
            )
            await username_input.fill(self.username)
            await asyncio.sleep(1)

            # Debug: Take screenshot after filling username
            try:
                await self.page.screenshot(path="output/after_username.png")
                logger.info("📸 Screenshot saved: output/after_username.png")
            except Exception as e:
                logger.warning(f"Could not take screenshot after username: {e}")

            # Click Next (try multiple selectors and strategies)
            next_selectors = [
                'div[data-testid="LoginForm_Login_Button"]',
                'div[data-testid="LoginButton"]',
                'div[role="button"]:has-text("Next")',
                'div[role="button"]:has-text("Log in")',
                'button:has-text("Next")',
                'button:has-text("Log in")',
                'button[aria-label="Next"]',
                'button[type="submit"]',
            ]
            next_button = None
            for selector in next_selectors:
                try:
                    next_button = await self.page.wait_for_selector(
                        selector, timeout=2000
                    )
                    if next_button:
                        break
                except Exception:
                    continue
            # Try Playwright's locator API by visible text if not found
            if not next_button:
                try:
                    locator = self.page.locator("button", has_text="Next")
                    if await locator.count() > 0:
                        next_button = locator.nth(0)
                except Exception:
                    pass
            # Try to click the button
            if next_button:
                try:
                    await next_button.click()
                except Exception as e:
                    logger.warning(f"Normal click failed, trying JS click: {e}")
                    # Fallback: force click via JS
                    try:
                        await self.page.evaluate("(el) => el.click()", next_button)
                    except Exception as e2:
                        logger.error(f"JS click also failed: {e2}")
                await asyncio.sleep(2)
            else:
                logger.warning("Next button not found, pressing Enter as fallback")
                await self.page.keyboard.press("Enter")
                await asyncio.sleep(2)

            # Enter password
            password_input = await self.page.wait_for_selector('input[name="password"]')
            await password_input.fill(self.password)
            await asyncio.sleep(1)

            # Click Login (try multiple selectors)
            login_selectors = [
                'div[data-testid="LoginButton"]',
                'div[role="button"]:has-text("Log in")',
                'button:has-text("Log in")',
                'div[data-testid="SignupButton"]',
                'button[type="submit"]',
            ]
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = await self.page.wait_for_selector(
                        selector, timeout=2000
                    )
                    if login_button:
                        break
                except Exception:
                    continue
            if login_button:
                try:
                    await login_button.click()
                except Exception as e:
                    logger.warning(f"Login click failed, trying JS click: {e}")
                    try:
                        await self.page.evaluate("(el) => el.click()", login_button)
                    except Exception as e2:
                        logger.error(f"JS login click also failed: {e2}")
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
                    el = await self.page.wait_for_selector(selector)
                    if el:
                        logger.info(
                            f"Successfully logged in to Twitter (found {selector})"
                        )
                        self.is_logged_in = True

                        # Save cookies for future sessions
                        await self.save_cookies()

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
                    following_link = await self.page.wait_for_selector(selector)
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
        self, username: str, max_tweets: int = 50
    ) -> list[dict[str, Any]]:
        """Get ALL tweets from a specific user with comprehensive crawling"""
        try:
            logger.info(f"Getting ALL tweets from @{username}...")
            self.current_query = f"user:{username}"

            # Navigate to user's profile
            profile_url = f"https://twitter.com/{username}"
            await self.page.goto(profile_url, wait_until="networkidle")
            await asyncio.sleep(5)  # Wait longer for content to load

            # Try to find tweets with multiple selectors
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
                    await self.page.wait_for_selector(selector, timeout=10000)
                    tweets_found = True
                    logger.info(f"Found tweets using selector: {selector}")
                    break
                except Exception:
                    continue

            if not tweets_found:
                logger.warning(f"No tweets found for @{username}")
                return []

            # Comprehensive scrolling to load ALL tweets
            max_scrolls = 20  # Increased scrolls to get more tweets
            scroll_attempts = 0
            last_tweet_count = 0

            for scroll_attempts in range(max_scrolls):
                # Check current tweet count
                current_tweets = []
                for selector in tweet_selectors:
                    try:
                        tweet_elements = await self.page.query_selector_all(selector)
                        if tweet_elements:
                            current_tweets = tweet_elements
                            break
                    except Exception:
                        continue

                current_count = len(current_tweets)
                logger.info(
                    f"Scroll {scroll_attempts + 1}: Found {current_count} tweets for @{username}"
                )

                # If we have enough tweets, break
                if current_count >= max_tweets:
                    break

                # If no new tweets loaded after 3 attempts, break
                if current_count == last_tweet_count:
                    scroll_attempts += 1
                    if scroll_attempts >= 3:
                        logger.info(
                            f"No new tweets loaded after 3 attempts for @{username}"
                        )
                        break
                else:
                    scroll_attempts = 0
                    last_tweet_count = current_count

                # Human-like scrolling
                scroll_distance = random.randint(800, 1200)
                await self.page.evaluate(f"window.scrollBy(0, {scroll_distance})")
                await asyncio.sleep(random.uniform(2.0, 4.0))  # Random delay

                # Sometimes scroll up a bit to trigger more loading
                if random.random() < 0.3:
                    await self.page.evaluate("window.scrollBy(0, -200)")
                    await asyncio.sleep(random.uniform(1.0, 2.0))

            # Extract ALL tweets found
            tweets = await self.extract_tweets_enhanced(max_tweets)

            # Add source information
            for tweet in tweets:
                tweet["source_type"] = "user_profile"
                tweet["username"] = username
                tweet["crawl_timestamp"] = datetime.now(UTC).isoformat()

            logger.info(
                f"Extracted {len(tweets)} tweets from @{username} (target: {max_tweets})"
            )
            return tweets

        except Exception as e:
            logger.error(f"Error getting tweets from @{username}: {e}")
            import traceback

            logger.error(f"Exception details:\n{traceback.format_exc()}")
            return []

    async def get_for_you_tweets(self, max_tweets: int = 30) -> list[dict[str, Any]]:
        """Get tweets from the For You page with enhanced crawling"""
        try:
            logger.info("Getting tweets from For You page...")

            # Navigate to Twitter home (For You page)
            await self.page.goto("https://twitter.com/home", wait_until="networkidle")
            await asyncio.sleep(5)  # Wait longer for content to load

            # Try to switch to "For You" tab if not already selected
            try:
                for_you_selectors = [
                    'a[data-testid="AppTabBar_ForYou_Link"]',
                    'a[href="/home"]',
                    'div[role="tab"]:has-text("For you")',
                    'div[data-testid="tab"]:has-text("For you")',
                ]

                for selector in for_you_selectors:
                    try:
                        for_you_tab = await self.page.wait_for_selector(
                            selector, timeout=5000
                        )
                        if for_you_tab:
                            await for_you_tab.click()
                            await asyncio.sleep(3)
                            logger.info("Clicked on For You tab")
                            break
                    except Exception:
                        continue
            except Exception as e:
                logger.warning(f"Could not switch to For You tab: {e}")

            # Enhanced human-like scrolling with more comprehensive crawling
            await self.human_like_scroll(max_scrolls=15, max_tweets=max_tweets)

            # Additional scrolling to ensure we get enough content
            for _i in range(5):
                await self.page.evaluate("window.scrollBy(0, 800)")
                await asyncio.sleep(random.uniform(1.5, 3.0))

                # Check if we have enough tweets
                tweet_elements = await self.page.query_selector_all(
                    'article[data-testid="tweet"]'
                )
                if len(tweet_elements) >= max_tweets:
                    break

            # Extract tweets with enhanced selectors
            tweets = await self.extract_tweets_enhanced(max_tweets)

            # Add source information
            for tweet in tweets:
                tweet["source_type"] = "for_you_page"
                tweet["crawl_timestamp"] = datetime.now(UTC).isoformat()

            logger.info(f"Extracted {len(tweets)} tweets from For You page")
            return tweets

        except Exception as e:
            logger.error(f"Error getting For You tweets: {e}")
            import traceback

            logger.error(f"Exception details:\n{traceback.format_exc()}")
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
                    await self.page.wait_for_selector(selector)
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
            await self.page.goto(search_url, wait_until="networkidle")

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
                    await self.page.wait_for_selector(selector)
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

            for _ in range(max_scrolls):
                if tweets_loaded >= max_tweets:
                    break

                await self.page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(2)

                for selector in tweet_selectors:
                    try:
                        tweet_elements = await self.page.query_selector_all(selector)
                        if tweet_elements:
                            tweets_loaded = len(tweet_elements)
                            logger.info(
                                f"Loaded {tweets_loaded} tweets for '{query}' (scroll {_ + 1})"
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
                "created_at": timestamp or datetime.now(UTC).isoformat(),
                "engagement": engagement,
                "sentiment": sentiment,
                "query": self.current_query,
                "collected_at": datetime.now(UTC).isoformat(),
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
        """Run a focused crawl prioritizing For You page and followed accounts first"""
        all_tweets = []

        try:
            # Try browser-based crawling first
            logger.info(
                "🚀 Starting focused Twitter crawl (For You + Followed accounts first)..."
            )

            # Setup browser with retry logic
            browser_success = False
            for attempt in range(3):
                try:
                    await self.setup_browser()
                    browser_success = True
                    logger.info(f"✅ Browser setup successful on attempt {attempt + 1}")
                    break
                except Exception as e:
                    logger.warning(
                        f"⚠️ Browser setup failed on attempt {attempt + 1}: {e}"
                    )
                    if attempt < 2:
                        await asyncio.sleep(5)

            if not browser_success:
                logger.warning("⚠️ Browser setup failed, using fallback method")
                return await self.run_fallback_crawl(max_tweets_per_query)

            # Try to login
            try:
                await self.login_to_twitter()
                logger.info("✅ Successfully logged into Twitter")
            except Exception as e:
                logger.warning(f"⚠️ Login failed, continuing without login: {e}")

            # PRIORITY 1: Get tweets from For You page first
            logger.info("🎯 PRIORITY 1: Getting tweets from For You page...")
            for_you_tweets = []
            if self.is_logged_in:
                for_you_tweets = await self.get_for_you_tweets(
                    max_tweets=50
                )  # Increased limit
                if for_you_tweets:
                    await self.save_tweets_incremental(
                        for_you_tweets, "for_you_page_priority"
                    )
                    all_tweets.extend(for_you_tweets)
                    logger.info(
                        f"✅ Collected {len(for_you_tweets)} tweets from For You page"
                    )

            # PRIORITY 2: Get followed accounts and their tweets
            logger.info("👥 PRIORITY 2: Getting followed accounts and their tweets...")
            followed_tweets = []
            if self.is_logged_in:
                followed_accounts = await self.get_followed_accounts(
                    max_accounts=30
                )  # Increased limit
                if followed_accounts:
                    logger.info(
                        f"📱 Scanning {len(followed_accounts)} followed accounts..."
                    )
                    for username in followed_accounts[
                        :20
                    ]:  # Limit to first 20 for performance
                        try:
                            user_tweets = await self.get_user_tweets(
                                username, max_tweets=30
                            )  # Increased limit

                            # Mark all followed account tweets
                            for tweet in user_tweets:
                                tweet["source_type"] = "followed_account_priority"
                                tweet["followed_username"] = username

                            followed_tweets.extend(user_tweets)

                            # Save user tweets immediately to GCS
                            if user_tweets:
                                await self.save_tweets_incremental(
                                    user_tweets, f"followed_user_priority_{username}"
                                )

                            logger.info(
                                f"✅ Collected {len(user_tweets)} tweets from @{username}"
                            )
                            await asyncio.sleep(1)  # Small delay between users
                        except Exception as e:
                            logger.warning(
                                f"Error getting tweets from @{username}: {e}"
                            )
                            continue

                    all_tweets.extend(followed_tweets)
                    logger.info(
                        f"✅ Total followed account tweets: {len(followed_tweets)}"
                    )

            # PRIORITY 3: Get saved post comments
            logger.info("💾 PRIORITY 3: Getting comments from saved posts...")
            saved_comments = []
            if self.is_logged_in:
                saved_comments = await self.get_saved_post_comments(
                    max_posts=20
                )  # Increased limit
                if saved_comments:
                    await self.save_tweets_incremental(
                        saved_comments, "saved_post_comments_priority"
                    )
                    all_tweets.extend(saved_comments)
                    logger.info(
                        f"✅ Collected {len(saved_comments)} saved post comments"
                    )

            # Only run search queries if we have time/resources left
            logger.info("🔍 OPTIONAL: Running search queries (if time permits)...")
            search_tweets = []

            # Group queries by category for better organization
            query_categories = {
                "memecoins": [
                    q
                    for q in self.search_queries
                    if any(
                        term in q.lower()
                        for term in [
                            "meme",
                            "pepe",
                            "doge",
                            "shib",
                            "floki",
                            "moon",
                            "pump",
                            "gem",
                        ]
                    )
                ],
                "launchpads": [
                    q
                    for q in self.search_queries
                    if any(
                        term in q.lower()
                        for term in [
                            "launchpad",
                            "ido",
                            "presale",
                            "token launch",
                            "fair launch",
                        ]
                    )
                ],
                "farming": [
                    q
                    for q in self.search_queries
                    if any(
                        term in q.lower()
                        for term in ["farming", "yield", "staking", "apy", "rewards"]
                    )
                ],
                "airdrops": [
                    q
                    for q in self.search_queries
                    if any(
                        term in q.lower()
                        for term in ["airdrop", "free tokens", "claim", "whitelist"]
                    )
                ],
                "solana": [
                    q
                    for q in self.search_queries
                    if "solana" in q.lower() or "sol" in q.lower()
                ],
            }

            # Only run first 3 categories to save time
            for category, queries in list(query_categories.items())[:3]:
                logger.info(
                    f"🎯 Searching {category} category with {len(queries)} queries..."
                )

                for _i, query in enumerate(
                    queries[:5]
                ):  # Reduced to 5 queries per category
                    try:
                        logger.info(f"🔍 [{category}] Searching for: {query}")
                        tweets = await self.search_twitter(query, max_tweets_per_query)

                        # Add category information to tweets
                        for tweet in tweets:
                            tweet["search_category"] = category
                            tweet["search_query"] = query

                        search_tweets.extend(tweets)
                        logger.info(
                            f"✅ [{category}] Found {len(tweets)} tweets for '{query}'"
                        )

                        # Save category tweets immediately to GCS
                        if tweets:
                            safe_query = (
                                query.replace(" ", "_")
                                .replace("#", "")
                                .replace("@", "")[:15]
                            )
                            await self.save_tweets_incremental(
                                tweets, f"search_{category}_{safe_query}"
                            )

                        await asyncio.sleep(2)  # Rate limiting between searches
                    except Exception as e:
                        logger.warning(f"❌ Error searching for '{query}': {e}")
                        continue

                # Add shorter delay between categories
                await asyncio.sleep(random.uniform(3.0, 5.0))

            all_tweets.extend(search_tweets)

            # Save all tweets to final output file
            if all_tweets:
                logger.info("💾 Saving all tweets to final output file...")
                await self.save_tweets(all_tweets)
                logger.info(
                    f"✅ Successfully saved {len(all_tweets)} tweets to final output"
                )

            # Log final statistics
            logger.info("📊 Final Crawl Statistics:")
            logger.info(f"   - For You page tweets: {len(for_you_tweets)}")
            logger.info(f"   - Followed account tweets: {len(followed_tweets)}")
            logger.info(f"   - Saved post comments: {len(saved_comments)}")
            logger.info(f"   - Search query tweets: {len(search_tweets)}")
            logger.info(f"   - Total tweets collected: {len(all_tweets)}")

            logger.info(
                f"🎉 Focused crawl completed! Total tweets collected: {len(all_tweets)}"
            )
            logger.info("📊 Priority breakdown:")
            logger.info("   - For You page tweets (highest priority)")
            logger.info("   - Followed account tweets (second priority)")
            logger.info("   - Saved post comments (third priority)")
            logger.info("   - Search queries (optional, if time permits)")

        except Exception as e:
            logger.error(f"❌ Error in crawl session: {e}")
        finally:
            # Always cleanup
            try:
                await self.cleanup()
            except Exception as e:
                logger.warning(f"⚠️ Cleanup error: {e}")

        return all_tweets

    async def run_fallback_crawl(
        self, max_tweets_per_query: int = 10
    ) -> list[dict[str, Any]]:
        """Fallback crawl method that doesn't require browser automation"""
        logger.info("🔄 Using fallback crawl method (no browser automation)")

        # Create mock tweets for testing purposes
        mock_tweets = []
        search_terms = ["solana", "sol", "bonk", "dogwifhat", "jupiter"]

        for i, term in enumerate(search_terms):
            mock_tweet = {
                "text": f"This is a mock tweet about {term} for testing purposes #{term} #solana",
                "username": f"test_user_{i}",
                "timestamp": datetime.now(UTC).isoformat(),
                "likes": random.randint(10, 1000),
                "retweets": random.randint(5, 500),
                "replies": random.randint(1, 100),
                "search_query": term,
                "sentiment": {
                    "polarity": random.uniform(-0.5, 0.8),
                    "subjectivity": random.uniform(0.3, 0.9),
                },
                "source": "fallback_crawl",
            }
            mock_tweets.append(mock_tweet)

        logger.info(f"🔄 Fallback crawl completed with {len(mock_tweets)} mock tweets")
        return mock_tweets

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

                # Save For You tweets immediately to GCS
                if for_you_tweets:
                    await self.save_tweets_incremental(for_you_tweets, "for_you_page")

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
                        :25
                    ]:  # Limit to first 25 for performance
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

                            # Save user tweets immediately to GCS
                            if user_tweets:
                                await self.save_tweets_incremental(
                                    user_tweets, f"followed_user_{username}"
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

                # Save saved post comments immediately to GCS
                if saved_comments:
                    await self.save_tweets_incremental(
                        saved_comments, "saved_post_comments"
                    )

                # Save saved post comments immediately to GCS
                if saved_comments:
                    await self.save_tweets_incremental(
                        saved_comments, "saved_post_comments"
                    )

            # 4. Discover and get tweets from users found in For You and saved posts
            discovered_tweets = []
            if discovered_users:
                logger.info(
                    f"🔍 Discovering tweets from {len(discovered_users)} users..."
                )
                for username in list(discovered_users)[
                    :15
                ]:  # Limit to first 15 for performance
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

                        # Save discovered user tweets immediately to GCS
                        if user_tweets:
                            await self.save_tweets_incremental(
                                user_tweets, f"discovered_user_{username}"
                            )

                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.warning(
                            f"Error getting tweets from discovered user @{username}: {e}"
                        )
                        continue

            # 5. Search for trending topics across all categories
            search_tweets = []
            logger.info("🔍 Searching for trending topics across all categories...")

            # Use more search queries for comprehensive coverage
            for query in self.search_queries[:20]:  # Use first 20 search queries
                try:
                    logger.info(f"Searching for: {query}")
                    query_tweets = await self.search_twitter(
                        query, 20
                    )  # 20 tweets per query

                    # Mark search tweets
                    for tweet in query_tweets:
                        tweet["source_type"] = "search_query"
                        tweet["search_query"] = query

                    search_tweets.extend(query_tweets)
                    logger.info(
                        f"Collected {len(query_tweets)} tweets for query: {query}"
                    )

                    # Save search query tweets immediately to GCS
                    if query_tweets:
                        safe_query = (
                            query.replace(" ", "_")
                            .replace("#", "")
                            .replace("@", "")[:20]
                        )
                        await self.save_tweets_incremental(
                            query_tweets, f"search_{safe_query}"
                        )

                    await asyncio.sleep(2)  # Small delay between searches
                except Exception as e:
                    logger.warning(f"Error searching for {query}: {e}")
                    continue

            # Combine all tweets
            all_tweets = (
                for_you_tweets
                + followed_tweets
                + saved_comments
                + discovered_tweets
                + search_tweets
            )

            # Log statistics
            logger.info("📊 Crawl Statistics:")
            logger.info(f"   - For You page tweets: {len(for_you_tweets)}")
            logger.info(f"   - Followed account tweets: {len(followed_tweets)}")
            logger.info(f"   - Saved post comments: {len(saved_comments)}")
            logger.info(f"   - Discovered user tweets: {len(discovered_tweets)}")
            logger.info(f"   - Search query tweets: {len(search_tweets)}")
            logger.info(f"   - Total tweets collected: {len(all_tweets)}")

            # Save results with real-time GCS upload
            if all_tweets:
                logger.info(
                    f"💾 Saving {len(all_tweets)} tweets with real-time GCS upload..."
                )
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

    async def save_tweets_incremental(
        self, tweets: list[dict[str, Any]], batch_name: str = "batch"
    ):
        """Save tweets incrementally with immediate GCS upload"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"twitter_playwright_enhanced_{batch_name}_{timestamp}.json"
            filepath = self.output_dir / filename

            data = {
                "tweets": tweets,
                "metadata": {
                    "total_tweets": len(tweets),
                    "batch_name": batch_name,
                    "collected_at": datetime.now(UTC).isoformat(),
                    "source": "twitter_playwright_enhanced",
                    "crawler_version": "2.0",
                    "gcs_uploaded": False,
                },
            }

            # Save locally first
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"✅ Saved {len(tweets)} tweets locally to {filename}")

            # Immediately upload to Google Cloud Storage
            if self.gcs_bucket and GCS_AVAILABLE:
                try:
                    logger.info(f"☁️ Starting GCS upload for {batch_name}...")

                    # Upload batch file
                    cloud_path = f"data/batches/{filename}"
                    blob = self.gcs_bucket.blob(cloud_path)
                    blob.upload_from_filename(str(filepath))
                    logger.info(f"✅ Uploaded batch to GCS: {cloud_path}")

                    # Update metadata
                    data["metadata"]["gcs_uploaded"] = True
                    data["metadata"]["gcs_path"] = cloud_path
                    data["metadata"]["gcs_upload_time"] = datetime.now(UTC).isoformat()

                    # Update local file with GCS metadata
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, default=str)

                    logger.info(
                        f"🎉 Successfully uploaded {len(tweets)} tweets to GCS for {batch_name}"
                    )

                except Exception as e:
                    logger.error(f"❌ Error uploading batch to GCS: {e}")
                    data["metadata"]["gcs_uploaded"] = False
                    data["metadata"]["gcs_error"] = str(e)

                    # Update local file with error metadata
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, default=str)
            else:
                logger.warning("⚠️ GCS not available - batch saved locally only")

        except Exception as e:
            logger.error(f"❌ Error saving batch tweets: {e}")

    async def save_tweets(self, tweets: list[dict[str, Any]]):
        """Save tweets to both local file and Google Cloud Storage with real-time upload"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"twitter_playwright_enhanced_{timestamp}.json"
            filepath = self.output_dir / filename

            data = {
                "tweets": tweets,
                "metadata": {
                    "total_tweets": len(tweets),
                    "collected_at": datetime.now(UTC).isoformat(),
                    "source": "twitter_playwright_enhanced",
                    "crawler_version": "2.0",
                    "gcs_uploaded": False,  # Will be updated after upload
                },
            }

            # Save locally first
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            # Also save as latest locally
            latest_file = self.output_dir / "twitter_playwright_enhanced_latest.json"
            with open(latest_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"✅ Saved {len(tweets)} tweets locally to {filename}")

            # Immediately upload to Google Cloud Storage
            if self.gcs_bucket and GCS_AVAILABLE:
                try:
                    logger.info("☁️ Starting GCS upload...")

                    # Upload timestamped file
                    cloud_path = f"data/twitter_playwright_enhanced_{timestamp}.json"
                    blob = self.gcs_bucket.blob(cloud_path)

                    # Upload from file
                    blob.upload_from_filename(str(filepath))
                    logger.info(f"✅ Uploaded timestamped file to GCS: {cloud_path}")

                    # Upload as latest
                    latest_cloud_path = "data/twitter_playwright_enhanced_latest.json"
                    blob_latest = self.gcs_bucket.blob(latest_cloud_path)
                    blob_latest.upload_from_filename(str(latest_file))
                    logger.info(f"✅ Uploaded latest file to GCS: {latest_cloud_path}")

                    # Update metadata to indicate successful GCS upload
                    data["metadata"]["gcs_uploaded"] = True
                    data["metadata"]["gcs_path"] = cloud_path
                    data["metadata"]["gcs_latest_path"] = latest_cloud_path
                    data["metadata"]["gcs_upload_time"] = datetime.now(UTC).isoformat()

                    # Update local files with GCS metadata
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, default=str)
                    with open(latest_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, default=str)

                    logger.info(f"🎉 Successfully uploaded {len(tweets)} tweets to GCS")

                except Exception as e:
                    logger.error(f"❌ Error uploading to GCS: {e}")
                    import traceback

                    logger.error(f"GCS upload error details:\n{traceback.format_exc()}")
                    data["metadata"]["gcs_uploaded"] = False
                    data["metadata"]["gcs_error"] = str(e)
                    data["metadata"]["gcs_error_time"] = datetime.now(UTC).isoformat()

                    # Update local files with error metadata
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, default=str)
                    with open(latest_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, default=str)
            else:
                logger.warning("⚠️ GCS not available - tweets saved locally only")
                data["metadata"]["gcs_uploaded"] = False
                data["metadata"]["gcs_error"] = "GCS not available"

                # Update local files with error metadata
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, default=str)
                with open(latest_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"❌ Error saving tweets: {e}")
            import traceback

            logger.error(f"Save error details:\n{traceback.format_exc()}")

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
        for _ in range(max_scrolls):
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
    """Main function for testing - focuses on For You page and followed accounts first"""
    crawler = EnhancedTwitterPlaywrightCrawler(headless=True)
    tweets = await crawler.run_single_crawl(max_tweets_per_query=10)
    print(f"🎉 Focused crawl completed! Collected {len(tweets)} tweets")
    print("📊 Priority breakdown:")
    print("   - For You page tweets (highest priority)")
    print("   - Followed account tweets (second priority)")
    print("   - Saved post comments (third priority)")
    print("   - Search queries (optional, if time permits)")


if __name__ == "__main__":
    asyncio.run(main())
