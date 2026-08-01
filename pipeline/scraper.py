import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def scrape_summary(driver):

    totalETransaction = driver.find_element(
        By.XPATH,
        "//div[@key='trs']/following-sibling::div[@class='info infi_count']/span",
    )

    aadhaarAuthenticated = driver.find_element(
        By.XPATH,
        "//div[@key='aafioc']/following-sibling::div[@class='info infi_count']/span",
    )

    otherModeAuthenticated = driver.find_element(
        By.XPATH,
        "//div[@key='aom1']/following-sibling::div[@class='info infi_count']/span",
    )

    nonAuthenticated = driver.find_element(
        By.XPATH,
        "//div[@key='nat1']/following-sibling::div[@class='info infi_count']/span",
    )

    return {
        "Total e-Transaction": totalETransaction.text,
        "Aadhaar Authenticated": aadhaarAuthenticated.text,
        "Other Mode Authenticated": otherModeAuthenticated.text,
        "Non-Authenticated": nonAuthenticated.text,
    }


def scrape_transaction_table(driver):
    table = driver.find_element(
        By.XPATH,
        "//h4/span[text()='Number of Transaction']/ancestor::div[contains(@class,'dash-row2')]//table",
    )

    rows = table.find_elements(By.XPATH, ".//tbody/tr")

    data = []

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")

        data.append(
            {
                "Card Type": cols[0].text,
                "Regular": cols[1].text,
                "Intra State": cols[2].text,
                "Inter State": cols[3].text,
                "Total": cols[4].text,
            }
        )

    return data


def scrape_transacted_ration_card_table(driver):
    table = driver.find_element(
        By.XPATH, "//table[@aria-label='Number of Transacted Ration Card']"
    )

    rows = table.find_elements(By.XPATH, ".//tbody/tr")

    data = []

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")

        data.append(
            {
                "NFSA Ration Card Type": cols[0].text,
                "Regular": cols[1].text,
                "Intra State": cols[2].text,
                "Inter State": cols[3].text,
                "Total": cols[4].text,
            }
        )

    return data


def scrape_distributed_quantity_table(driver, max_retries=3):
    """
    Scrape distributed quantity table with retry logic for click intercepted errors.

    Args:
        driver: WebDriver object
        max_retries: Number of retry attempts for clicking the button

    Returns:
        List of commodity data
    """
    button = None

    # Try to find and click the Coarse Grains button with retry
    for attempt in range(max_retries):
        try:
            # Wait for button to be clickable
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Coarse Grains')]")
                )
            )

            # Check if already expanded
            if button.get_attribute("aria-expanded") == "false":
                print(
                    f"Attempt {attempt + 1}/{max_retries} - Clicking Coarse Grains button"
                )

                # Strategy 1: Scroll into view + regular click
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(0.5)

                try:
                    button.click()
                    print("Successfully clicked with Selenium click")
                except Exception as selenium_click_error:
                    print(
                        f"Selenium click failed: {selenium_click_error}, trying JavaScript click"
                    )
                    # Strategy 2: JavaScript click as fallback
                    driver.execute_script("arguments[0].click();", button)
                    print("Successfully clicked with JavaScript click")

                # Wait for the table rows to appear
                WebDriverWait(driver, 10).until(
                    lambda d: len(
                        d.find_elements(
                            By.XPATH,
                            "//table[@aria-label='Distributed Quantity(In Kg)']//tr[contains(@class,'customRow') and not(contains(@class,'d-none'))]",
                        )
                    )
                    > 0
                )
                break  # Success, exit retry loop
            else:
                print("Coarse Grains already expanded")
                break  # Already expanded, no need to click

        except Exception as e:
            print(f"Click attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                print(
                    f"Failed to click Coarse Grains button after {max_retries} attempts"
                )

    # Locate the table
    table = driver.find_element(
        By.XPATH,
        "//table[@aria-label='Distributed Quantity(In Kg)']",
    )

    data = []

    # Read tbody rows
    rows = table.find_elements(By.XPATH, ".//tbody/tr")

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")

        if len(cols) != 5:
            continue

        commodity = cols[0].text.replace("+", "").replace("-", "").strip()

        data.append(
            {
                "Commodity": commodity,
                "Regular Txn": cols[1].text,
                "Intra State Txn": cols[2].text,
                "Inter State Txn": cols[3].text,
                "Total": cols[4].text,
            }
        )

    # Read footer (Total Commodity)
    footer_cols = table.find_elements(By.XPATH, ".//tfoot/tr/td")

    if len(footer_cols) == 5:
        data.append(
            {
                "Commodity": "Total",
                "Regular Txn": footer_cols[1].text,
                "Intra State Txn": footer_cols[2].text,
                "Inter State Txn": footer_cols[3].text,
                "Total": footer_cols[4].text,
            }
        )

    return data


def scrape_fps(driver, state, district, fps_id):
    """
    Scrape all FPS dashboard data.

    Args:
        driver: WebDriver object
        state: State name
        district: District name
        fps_id: FPS ID

    Returns:
        Dictionary with all scraped data
    """
    fps_data = {
        "State": state,
        "District": district,
        "FPS ID": fps_id,
    }

    # Summary
    print("Scraping summary data...")
    fps_data.update(scrape_summary(driver))

    # Transaction Table
    print("Scraping transaction table...")
    for row in scrape_transaction_table(driver):

        if "PHH" in row["Card Type"]:
            card = "PHH"
        elif "AAY" in row["Card Type"]:
            card = "AAY"
        else:
            continue

        fps_data[f"Transaction {card} Regular"] = row["Regular"]
        fps_data[f"Transaction {card} Intra State"] = row["Intra State"]
        fps_data[f"Transaction {card} Inter State"] = row["Inter State"]
        fps_data[f"Transaction {card} Total"] = row["Total"]

    # Transacted Ration Card Table
    print("Scraping transacted ration card table...")
    for row in scrape_transacted_ration_card_table(driver):

        if "PHH" in row["NFSA Ration Card Type"]:
            card = "PHH"
        elif "AAY" in row["NFSA Ration Card Type"]:
            card = "AAY"
        else:
            continue

        fps_data[f"Ration Card {card} Regular"] = row["Regular"]
        fps_data[f"Ration Card {card} Intra State"] = row["Intra State"]
        fps_data[f"Ration Card {card} Inter State"] = row["Inter State"]
        fps_data[f"Ration Card {card} Total"] = row["Total"]

    # Distributed Quantity Table
    print("Scraping distributed quantity table...")
    for row in scrape_distributed_quantity_table(driver, max_retries=3):

        commodity = row["Commodity"].strip()

        if commodity == "Coarse Grains":
            commodity = "Coarse Grains Total"
        elif commodity == "Total":
            commodity = "Total Commodity"

        fps_data[f"{commodity} Regular"] = row["Regular Txn"]
        fps_data[f"{commodity} Intra State"] = row["Intra State Txn"]
        fps_data[f"{commodity} Inter State"] = row["Inter State Txn"]
        fps_data[f"{commodity} Total"] = row["Total"]

    return fps_data
