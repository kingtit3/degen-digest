#!/usr/bin/env python3
"""
Robust local debug script for Twitter crawler - handles browser closure and provides detailed debugging
"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler


async def debug_crawler_robust():
    print("🔍 Starting robust local debug mode...")
    print("📝 This will open a browser window - DO NOT close it manually")
    print("🔑 Credentials will be automatically filled")
    print("⏳ The script will wait for you to complete any CAPTCHA or verification")

    # Set credentials
    os.environ["TWITTER_USERNAME"] = "gorebroai"
    os.environ["TWITTER_PASSWORD"] = "firefireomg4321"

    crawler = EnhancedTwitterPlaywrightCrawler(
        headless=False,
        output_dir="output",  # Show browser window
    )

    try:
        print("🚀 Setting up browser...")
        await crawler.setup_browser()

        print("🔐 Starting login process...")
        print("   Username:", os.getenv("TWITTER_USERNAME"))
        print("   Password:", "***" + os.getenv("TWITTER_PASSWORD")[-4:])

        # Go to login page manually
        print("🌐 Navigating to Twitter login...")
        await crawler.page.goto("https://twitter.com/login", wait_until="networkidle")
        await asyncio.sleep(3)

        print("📝 Filling username...")
        try:
            username_input = await crawler.page.wait_for_selector(
                'input[autocomplete="username"]', timeout=10000
            )
            await username_input.fill(os.getenv("TWITTER_USERNAME"))
            print("✅ Username filled")
        except Exception as e:
            print(f"❌ Error filling username: {e}")
            return

        await asyncio.sleep(2)

        print("⏭️ Clicking Next...")
        try:
            next_button = await crawler.page.wait_for_selector(
                'div[data-testid="SignupButton"]', timeout=5000
            )
            await next_button.click()
            print("✅ Next button clicked")
        except Exception as e:
            print(f"⚠️ Could not find Next button, trying Enter key: {e}")
            await crawler.page.keyboard.press("Enter")

        await asyncio.sleep(3)

        print("🔒 Filling password...")
        try:
            password_input = await crawler.page.wait_for_selector(
                'input[name="password"]', timeout=10000
            )
            await password_input.fill(os.getenv("TWITTER_PASSWORD"))
            print("✅ Password filled")
        except Exception as e:
            print(f"❌ Error filling password: {e}")
            return

        await asyncio.sleep(2)

        print("🚪 Clicking Login...")
        try:
            login_button = await crawler.page.wait_for_selector(
                'div[data-testid="LoginButton"]', timeout=5000
            )
            await login_button.click()
            print("✅ Login button clicked")
        except Exception as e:
            print(f"⚠️ Could not find Login button, trying Enter key: {e}")
            await crawler.page.keyboard.press("Enter")

        print("⏳ Waiting for login to complete...")
        print("💡 If you see a CAPTCHA or verification, please complete it manually")
        print("💡 The script will wait for you to finish...")

        # Wait for login to complete (with manual intervention allowed)
        await asyncio.sleep(10)

        # Check if login was successful
        print("🔍 Checking if login was successful...")
        try:
            # Look for elements that indicate successful login
            success_selectors = [
                'a[data-testid="AppTabBar_Home_Link"]',
                'a[data-testid="SideNav_Home_Link"]',
                'div[data-testid="tweetTextarea_0"]',
                'div[aria-label*="Timeline: Your Home Timeline"]',
                'nav[role="navigation"]',
            ]

            login_success = False
            for selector in success_selectors:
                try:
                    el = await crawler.page.wait_for_selector(selector, timeout=5000)
                    if el:
                        print(f"✅ Login successful! Found: {selector}")
                        login_success = True
                        break
                except Exception:
                    continue

            if not login_success:
                print("❌ Login may have failed - could not find home page elements")
                print("📸 Taking screenshot for debugging...")
                await crawler.page.screenshot(path="login_debug.png")
                print("Screenshot saved as login_debug.png")

                # Ask user to continue anyway
                print(
                    "🤔 Do you want to continue testing tweet extraction anyway? (y/n)"
                )
                # For now, we'll continue
                login_success = True

        except Exception as e:
            print(f"❌ Error checking login status: {e}")
            login_success = False

        if login_success:
            print("🎯 Testing tweet extraction...")

            # Navigate to home page
            print("📱 Navigating to home page...")
            await crawler.page.goto("https://twitter.com/home")
            await asyncio.sleep(5)

            # Take screenshot before extraction
            print("📸 Taking screenshot before tweet extraction...")
            await crawler.page.screenshot(path="before_extraction.png")
            print("Screenshot saved as before_extraction.png")

            print("🔍 Extracting tweets...")
            tweets = await crawler.extract_tweets_enhanced(5)
            print(f"Found {len(tweets)} tweets")

            if tweets:
                print("🎉 SUCCESS! Tweets found:")
                for i, tweet in enumerate(tweets[:3]):
                    print(f"\nTweet {i+1}:")
                    print(f"  Text: {tweet.get('text', 'No text')[:100]}...")
                    print(f"  Username: {tweet.get('username', 'Unknown')}")
                    print(f"  Engagement: {tweet.get('engagement', {})}")
            else:
                print("❌ No tweets found - taking debug screenshot...")
                await crawler.page.screenshot(path="no_tweets_debug.png")
                print("Screenshot saved as no_tweets_debug.png")

                # Debug page content
                print("🔍 Analyzing page content...")
                page_content = await crawler.page.content()
                if "tweet" in page_content.lower():
                    print("✅ 'tweet' found in page content")
                else:
                    print("❌ 'tweet' not found in page content")

                # Check for common tweet selectors
                print("🔍 Checking for tweet elements...")
                selectors_to_check = [
                    'article[data-testid="tweet"]',
                    'article[data-testid="cellInnerDiv"]',
                    'div[data-testid="tweet"]',
                    'article[role="article"]',
                ]

                for selector in selectors_to_check:
                    try:
                        elements = await crawler.page.query_selector_all(selector)
                        print(f"  {selector}: {len(elements)} elements found")
                    except Exception as e:
                        print(f"  {selector}: Error - {e}")

        print("⏳ Waiting 10 seconds before cleanup...")
        await asyncio.sleep(10)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

        # Take error screenshot
        try:
            await crawler.page.screenshot(path="error_debug.png")
            print("Error screenshot saved as error_debug.png")
        except:
            pass
    finally:
        print("🧹 Cleaning up...")
        await crawler.cleanup()
        print("✅ Debug session complete")


if __name__ == "__main__":
    asyncio.run(debug_crawler_robust())
