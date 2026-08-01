from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_driver(headless: bool = False) -> webdriver.Chrome:
    """
    get_driver(): It's only job is to configure the browser -> Start Browser -> Return driver

    args:
      headless: It is an argument that is in selenium,
                it allows us to run scripts in background without GUI.

    returns:
      driver : In our case it returns a latest Chrome Version driver.

    """
    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(
        service=service,
        options=options,
    )

    return driver
