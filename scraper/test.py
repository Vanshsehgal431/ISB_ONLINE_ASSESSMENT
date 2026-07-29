import time

from browser import get_driver
from navigator import (
    get_districts,
    get_fps,
    navigate_district,
    navigate_fps,
    navigate_to_month,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

driver = get_driver()

# Navigate to month
navigate_to_month(driver, 3, 2026)

# Click GOA
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="GOA"]'))
).click()

time.sleep(15)

print("Current URL after state:", driver.current_url)

# Get districts
districts = get_districts(driver)
print("Districts:", districts)

# Test only the first district
district = districts[0]
print("Opening district:", district)

navigate_district(driver, district)

print("Current URL after district:", driver.current_url)

# Get FPS list
fps_ids = get_fps(driver)

print("FPS Count:", len(fps_ids))
print("First 10 FPS IDs:", fps_ids[:10])

# Open only the first FPS
fps_id = fps_ids[0]

print("Opening FPS:", fps_id)

fps = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, f"//a[contains(@onclick, '{fps_id}')]"))
)

fps.click()

print("Current URL after FPS:", driver.current_url)

input("Press Enter to close...")

driver.quit()
