import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


def navigate_to_month(driver, month, year):
    """
    navigate_to_month() : This function navigate to the specific month and year
                          (In our case it will take us to 3-2026 and 4-2026)

    Args: driver -> Return object by browser.py.
          month -> The month have to be queried.
          year -> The year have to be queried.

    Return: Nothing
    """

    # Getting the website .
    driver.get("https://impds.nic.in/sale/")

    # Waiting for 10 seconds so that javascript finishes rendeering and calender's modal appears.
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-bs-target="#myModal10"]'))
    ).click()

    # Waiting for 10 seconds so that calender's modal-content appears.
    modal = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "modal-content"))
    )

    # Selecting the year.
    year_dropdown = Select(modal.find_element(By.ID, "selectedyear"))
    year_dropdown.select_by_visible_text(str(year))

    # After selecting the year waiting for 10 seconds so that the months are clickable and choosing the month.
    month_dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, f'a[onclick*="OnorcStateWisePage({month})"]')
        )
    )

    # Storing current-url to check in future if we are redirecting or not
    current_url = driver.current_url

    # Clicking on the targeted month.
    month_dropdown.click()

    # Waiting for 10 seconds to check if url changed or not.
    # As url changes from ("https://impds.nic.in/sale/")
    # to ("https://impds.nic.in/sale/stateUnautmated?month={month}&year={year}")
    WebDriverWait(driver, 10).until(EC.url_changes(current_url))


def get_districts(driver) -> list:
    """
    get_districts() : Returns the list of district associated with that particular state.

      Args: driver -> Return object by browser.py.

      Return: list of the district.
    """
    # Initialised empty list for districts
    districts = []

    # As the driver keeps the navigated url,
    # , url corresponds to the particular state map
    # just keep selecting all the blinks on map for active districts
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.blink_icon_img"))
    )

    blink_icons = driver.find_elements(By.CSS_SELECTOR, "div.blink_icon_img")

    print("Total blink icons:", len(blink_icons))

    # Appending the district name from attribute("aria-label") of a to districts list
    for icon in blink_icons:
        if not icon.is_displayed():
            continue

        link = icon.find_element(By.TAG_NAME, "a")
        district = link.get_attribute("aria-label")

        if district:
            districts.append(district)

    # Returning list of Districts
    return districts


def get_fps(driver) -> list:
    """
    get_fps() : Returns the list of FPS IDs associated with the current district.
                IMPORTANT: Does NOT store element references to avoid stale elements.

    Args:
        driver -> WebDriver object.

    Returns:
        List of FPS IDs.
    """

    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.menu_list a"))
    )

    fps_ids = []
    fps_links = driver.find_elements(By.CSS_SELECTOR, "li.menu_list a")

    # Extract IDs from onclick attributes (don't store element references)
    for link in fps_links:
        onclick = link.get_attribute("onclick")
        match = re.search(r"'(\d+)'", onclick)

        if match:
            fps_ids.append(match.group(1))

    print(f"Extracted FPS IDs: {len(fps_ids)}")
    return fps_ids


def navigate_fps(driver):
    """
    navigate_fps() : Navigate from the district page to the
                     FAIR PRICE SHOPS page.

    Args:
        driver -> WebDriver object returned by browser.py.

    Returns:
        None
    """

    # Wait until the fps card is clickable
    fps_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[onclick^='liveFpsdata']"))
    )

    # Store the current url
    current_url = driver.current_url

    # Click fps card
    fps_button.click()

    # If the page navigates, wait for the URL to change
    try:
        WebDriverWait(driver, 10).until(EC.url_changes(current_url))
    except Exception:
        # Some districts load via AJAX without changing the URL
        pass

    # Wait until the FPS list is loaded
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.menu_list a"))
    )


def click_fps_with_retry(driver, fps_id, max_retries=3):
    """
    click_fps_with_retry() : Click FPS by ID with retry logic.
                             First tries JavaScript approach (most reliable),
                             then falls back to element click with scroll.

    Args:
        driver -> WebDriver object.
        fps_id -> FPS ID to click.
        max_retries -> Number of retry attempts.

    Returns:
        True if successful, False otherwise.
    """

    # Strategy 1: JavaScript function call (most reliable for AJAX pages)
    try:
        print(f"Attempting JS approach for FPS: {fps_id}")
        driver.execute_script(f"stateData('{fps_id}');")

        # Wait for FPS data to load
        WebDriverWait(driver, 20).until(lambda d: fps_id in d.page_source)

        # Small delay for AJAX sections
        time.sleep(2)
        print(f"Successfully loaded FPS {fps_id} via JavaScript")
        return True
    except Exception as e:
        print(f"JS approach failed for {fps_id}: {str(e)}")

    # Strategy 2: Element click with scroll and retry
    for attempt in range(max_retries):
        try:
            print(
                f"Attempt {attempt + 1}/{max_retries} - Element click for FPS: {fps_id}"
            )

            # Wait for FPS links to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.menu_list a"))
            )

            # Re-fetch elements fresh each time (critical to avoid stale references)
            fps_links = driver.find_elements(By.CSS_SELECTOR, "li.menu_list a")

            found = False
            for link in fps_links:
                onclick = link.get_attribute("onclick")

                # Check if this link contains our target FPS ID
                if f"'{fps_id}'" in onclick:
                    found = True

                    # Scroll element into view to avoid "click intercepted" error
                    driver.execute_script("arguments[0].scrollIntoView(true);", link)
                    time.sleep(0.5)

                    # Try regular click first
                    try:
                        link.click()
                        print(f"Successfully clicked FPS {fps_id} with Selenium click")
                        time.sleep(2)
                        return True
                    except Exception as click_error:
                        print(
                            f"Selenium click failed, trying JavaScript click: {click_error}"
                        )
                        # Fall back to JavaScript click
                        driver.execute_script("arguments[0].click();", link)
                        print(
                            f"Successfully clicked FPS {fps_id} with JavaScript click"
                        )
                        time.sleep(2)
                        return True

            if not found:
                print(
                    f"FPS {fps_id} not found in links (attempt {attempt + 1}/{max_retries})"
                )

            # Wait before retry
            if attempt < max_retries - 1:
                time.sleep(1)

        except Exception as e:
            print(f"Click attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(1)

    print(f"Failed to click FPS {fps_id} after {max_retries} attempts")
    return False


def open_fps(driver, fps_id):
    """
    open_fps() : Open the selected FPS dashboard using JavaScript (most reliable).
                 This function is kept for backward compatibility but delegates to
                 click_fps_with_retry for actual implementation.

    Args:
        driver -> WebDriver object returned by browser.py.
        fps_id -> FPS ID.

    Returns:
        True if successful, False otherwise.
    """
    return click_fps_with_retry(driver, fps_id)


def navigate_district(driver, district):
    """
    navigate_district() : Navigate to the active district page.

    Args:
        driver: WebDriver object returned by browser.py.
        district: District name passed from navigate_state().

    Returns:
        None
    """
    # Wait for the district button to be clickable
    district_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f'a[title="{district}"]'))
    )

    # Click the district button
    district_button.click()

    # As loading of page took about 10-12 seconds so waiting for 15 seconds
    time.sleep(15)


def navigate_state(driver, state):
    """
    navigate_state() : Navigate to the specific state.

    Args: driver -> Return object by browser.py.
          state  -> State name we want to filter out.

    Return: Nothing
    """
    # Convert the state name to Upper case, as while selecting state the to check state we have to select
    # element by state's name which is in upper case
    state_name = state.upper()

    # Waiting for 10 seconds, so that state_button becomes clickable
    state_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f'a[title="{state_name}"]'))
    )

    # Clicking on state_button (E.g. state_name = "GOA", click on the button hyperlink where title = state_name)
    state_button.click()

    # This is added intentionally as the url not changing and buffering is happening for atmost 10-12 seconds,
    # so added a waiting time for 15 seconds.
    time.sleep(15)
