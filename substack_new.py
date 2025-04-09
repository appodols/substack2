import random
import time
import os
import sys
import re
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ✅ Human-like wait
def human_like_wait(min_time=0.5, max_time=2.5):
    time.sleep(round(random.uniform(min_time, max_time), 2))


# ✅ Clean text for filenames
def sanitize_filename(text):
    text = re.sub(r'[\\/*?:"<>|]', "", text)  # Remove illegal filename characters
    text = text.strip().replace(" ", "-")
    return text[:100]  # Limit filename length


# ✅ Take Substack URL from CLI
if len(sys.argv) < 2:
    print("❌ Error: Please provide a Substack link as an argument.")
    print("Example: python script.py https://thebearcave.substack.com/")
    sys.exit(1)

input_url = sys.argv[1]
parsed_url = urlparse(input_url)
base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
archive_url = f"{base_url}/archive"
print(f"📌 Extracted Substack Archive URL: {archive_url}")


# ✅ Driver setup
options = webdriver.ChromeOptions()
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-notifications")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)


# ✅ Log in
driver.get("https://substack.com/sign-in")
human_like_wait(1, 3)

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

try:
    password_link = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a.login-option.substack-login__login-option")
        )
    )
    driver.execute_script("arguments[0].click();", password_link)
    print("✅ Clicked 'Sign in with password'.")
except:
    print("❌ 'Sign in with password' link not found.")
    driver.quit()
    exit()

human_like_wait(1.5, 3.2)

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

try:
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
    )
    driver.execute_script("arguments[0].click();", submit_button)
    print("✅ Continue button clicked successfully.")
except:
    print("❌ Continue button not found.")

if "captcha" in driver.page_source.lower():
    input("🚨 CAPTCHA detected! Solve it manually, then press Enter to continue...")

human_like_wait(2, 4)


# ✅ Go to archive page
driver.get(archive_url)
human_like_wait(2, 4)


# ✅ Scroll to load posts
def scroll_with_keys(driver, times=50, delay=(0.3, 0.7)):
    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(times):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(random.uniform(*delay))


print("📜 Scrolling to load content...")
scroll_with_keys(driver)
print("✅ Finished scrolling.")


# ✅ Extract post links
try:
    post_links = driver.find_elements(By.XPATH, "//a[@data-testid='post-preview-title']")
    links = [link.get_attribute("href") for link in post_links]
    print(f"✅ Found {len(links)} posts.")
except:
    print("❌ No post links found.")
    driver.quit()
    exit()


# ✅ Create folder
if not os.path.exists("substack_posts"):
    os.makedirs("substack_posts")


# ✅ Visit each post, save with a valid title
for index, link in enumerate(links):
    print(f"🔗 Opening post {index+1}/{len(links)}: {link}")
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(link)
    human_like_wait(3, 6)

    try:
        # ✅ Try getting <h1> title
        try:
            post_title = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            ).text.strip()
        except:
            post_title = ""

        # ✅ Fallback to slug from URL if title is empty
        if not post_title:
            post_title = link.rstrip("/").split("/")[-1]

        # ✅ Final fallback if everything fails
        filename = sanitize_filename(post_title)
        if not filename:
            filename = f"post_{index+1}"

        # ✅ Save as MHTML
        driver.execute_cdp_cmd("Page.enable", {})
        mhtml = driver.execute_cdp_cmd("Page.captureSnapshot", {})

        full_path = f"substack_posts/{filename}.mhtml"
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(mhtml["data"])

        print(f"✅ Saved {full_path}")

    except Exception as e:
        print(f"❌ Could not save post {index+1}: {e}")

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    human_like_wait(2, 4)


print("🎉 All posts saved.")
time.sleep(10)
driver.quit()
