import undetected_chromedriver as uc
import random
import time
import os
import sys
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ✅ **Step 1: Define Human-Like Wait Function**
def human_like_wait(min_time=0.5, max_time=2.5):
    """Waits for a random time in the range (in hundredths of a second)."""
    wait_time = round(random.uniform(min_time, max_time), 2)
    time.sleep(wait_time)


# ✅ **Step 2: Take Substack URL from Command Line & Fix Double Slash Issue**
if len(sys.argv) < 2:
    print("❌ Error: Please provide a Substack link as an argument.")
    print(
        "Example: python script.py https://thebearcave.substack.com/?utm_source=global-search"
    )
    sys.exit(1)

input_url = sys.argv[1]
parsed_url = urlparse(input_url)
base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

# ✅ Ensure only one `/archive`
archive_url = f"{base_url}/archive"
print(f"📌 Extracted Substack Archive URL: {archive_url}")


# ✅ **Step 3: Set Up Chrome with Stealth Mode**
options = uc.ChromeOptions()
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-notifications")
options.add_argument("--save-page-as-mhtml")  # ✅ Ensures full page is saved

driver = uc.Chrome(options=options, use_subprocess=True)
driver.maximize_window()


# ✅ **Step 4: Navigate to Substack Login Page**
driver.get("https://substack.com/sign-in")
human_like_wait(1, 3)

# ✅ **Step 5: Enter Email Address**
try:
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    email_input.send_keys("sasha.p.podolsky@gmail.com")
    print("✅ Email entered successfully.")
except:
    print("❌ Email input field not found.")
    driver.quit()
    exit()

human_like_wait(1, 2.5)

# ✅ **Step 6: Click 'Sign in with password' using JavaScript Click**
password_clicked = False
try:
    password_link = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a.login-option.substack-login__login-option")
        )
    )
    driver.execute_script("arguments[0].click();", password_link)  # JavaScript Click
    print("✅ Clicked 'Sign in with password' (Method 3 - CSS Selector).")
    password_clicked = True
except:
    print("❌ 'Sign in with password' link not found or not clickable.")

if not password_clicked:
    driver.quit()
    exit()

human_like_wait(1.5, 3.2)

# ✅ **Step 7: Enter Password**
try:
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    password_input.send_keys("rpa5AEB-zbq6jbr5uqe")
    print("✅ Password entered successfully.")
except:
    print("❌ Password input field not found.")
    driver.quit()
    exit()

human_like_wait(1.2, 2.7)

# ✅ **Step 8: Click "Continue" Button**
try:
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
    )
    driver.execute_script("arguments[0].click();", submit_button)  # JavaScript Click
    print("✅ Continue button clicked successfully.")
except:
    print("❌ Continue button not found.")

# ✅ **Step 9: Handle CAPTCHA if Present**
if "catchypka" in driver.page_source.lower():
    input("🚨 CAPTCHA detected! Solve it manually, then press Enter to continue...")

human_like_wait(2, 4)

# ✅ **Step 10: Navigate to Substack Archive Page**
driver.get(archive_url)
human_like_wait(2, 4)


# ✅ **Step 11: Scroll Down Using Key Presses**
def scroll_with_keys(driver, times=50, delay=(0.3, 0.7)):
    """Scrolls down using PAGE DOWN key multiple times with a human-like delay."""
    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(times):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(random.uniform(*delay))


print("📜 Scrolling down to load all content...")
scroll_with_keys(driver, times=50, delay=(0.3, 0.7))
print("✅ Finished scrolling.")

# ✅ **Step 12: Extract All Post Links**
try:
    post_links = driver.find_elements(
        By.XPATH, "//a[@data-testid='post-preview-title']"
    )
    links = [link.get_attribute("href") for link in post_links]
    print(f"✅ Found {len(links)} posts.")
except:
    print("❌ No post links found.")
    driver.quit()
    exit()

# ✅ **Step 13: Create a Folder to Store Posts**
if not os.path.exists("substack_posts"):
    os.makedirs("substack_posts")


# ✅ **Step 14: Click Each Post Link, Load Content, and Save as MHTML**
for index, link in enumerate(links):
    print(f"🔗 Opening post {index+1}/{len(links)}: {link}")

    # Open a new tab
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])  # Switch to new tab

    # Navigate to the post
    driver.get(link)
    human_like_wait(3, 6)

    # ✅ **Step 15: Save Full Page as MHTML**
    try:
        # DevTools protocol to capture the page as MHTML (full snapshot)
        driver.execute_cdp_cmd("Page.enable", {})
        mhtml = driver.execute_cdp_cmd("Page.captureSnapshot", {})

        filename = f"substack_posts/post_{index+1}.mhtml"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(mhtml["data"])

        print(f"✅ Successfully saved {filename} (full snapshot).")

    except Exception as e:
        print(f"❌ Failed to save post {index+1}: {str(e)}")

    # ✅ **Step 16: Close the Tab and Return to Archive Page**
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    human_like_wait(2, 4)

# ✅ **Step 17: Close the Browser After Processing**
print("🎉 Finished loading and saving all posts with full context!")
time.sleep(35.12)
driver.quit()
