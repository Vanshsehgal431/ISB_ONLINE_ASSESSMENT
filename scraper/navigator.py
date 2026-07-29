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
    blink_icons = driver.find_elements(By.CSS_SELECTOR, "div.blink_icon_img")

    print("Total blink icons:", len(blink_icons))

    # Appending the district name from attribute("aria-label") of a to districts list
    # for icon in blink_icons:
    # link = icon.find_element(By.TAG_NAME, "a")
    # districts.append(link.get_attribute("aria-label"))
    for icon in blink_icons:
        if not icon.is_displayed():
            continue

        link = icon.find_element(By.TAG_NAME, "a")
        districts.append(link.get_attribute("aria-label"))

    return districts
    # Returning list of Districts
    return districts


import re


def get_fps(driver) -> list:
    """
    get_fps() : Returns the list of FPS IDs associated with the current district.

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

    for link in fps_links:
        onclick = link.get_attribute("onclick")
        fps_id = re.search(r"'(\d+)'", onclick).group(1)
        fps_ids.append(fps_id)

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
    except:
        # Some districts load via AJAX without changing the URL
        pass

        # Wait until the fps list/table is loaded
        # Waiting until the FPS list is loaded

    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.menu_list a"))
    )


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

    navigate_fps(driver=driver)


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

    districts = get_districts(driver=driver)

    # Navigating through each active district
    for district in districts:

        # Navigate to the district page and then to the FPS list
        navigate_district(driver=driver, district=district)

        # Getting all FPS IDs present in the current district
        fps_ids = get_fps(driver)

        # Navigating through each FPS of the current district
        for fps_id in fps_ids:

            # Waiting for the FPS link to become clickable
            fps = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//a[contains(@onclick, '{fps_id}')]")
                )
            )

            # Clicking on the FPS
            fps.click()

            # TODO: Scrape FPS details here

            # Returning back to the FPS list
            driver.back()

            # Waiting until the FPS list is loaded again
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.menu_list a"))
            )

        # Finished processing all FPS of the current district

        # Returning back to the district page
        driver.back()

        # Waiting until the FAIR PRICE SHOPS card is visible again
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[onclick^='liveFpsdata']")
            )
        )

        # Returning back to the state map
        driver.back()

        # Waiting until all active districts are visible again
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.blink_icon_img"))
        )
