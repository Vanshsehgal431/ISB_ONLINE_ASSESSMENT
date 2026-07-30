from browser import get_driver
from navigator import click_fps_with_retry  # Use the new retry-enabled function
from navigator import (
    get_districts,
    get_fps,
    navigate_district,
    navigate_fps,
    navigate_state,
    navigate_to_month,
)
from writer import write_to_csv

from scraper import scrape_fps

MONTH = 3
YEAR = 2026
STATE = "GOA"


def main():
    driver = get_driver()

    try:
        # Open required month
        navigate_to_month(driver, MONTH, YEAR)

        # Open state
        navigate_state(driver, STATE)

        print(f"Opened State: {STATE}")

        # Get districts
        districts = get_districts(driver)

        print(f"Districts Found: {districts}")

        if not districts:
            print("No districts found.")
            return

        # Test only first district
        district = districts[0]

        print(f"Opening District: {district}")

        navigate_district(driver, district)

        # Open FAIR PRICE SHOPS page
        navigate_fps(driver)

        # Get FPS list
        fps_ids = get_fps(driver)

        print(f"FPS Count: {len(fps_ids)}")

        if not fps_ids:
            print("No FPS found.")
            return

        # Test only first FPS
        fps_id = fps_ids[0]

        print(f"Opening FPS: {fps_id}")

        # Use new click_fps_with_retry for better error handling
        success = click_fps_with_retry(driver, fps_id, max_retries=3)

        if not success:
            print(f"Failed to load FPS {fps_id} after 3 retries. Exiting.")
            return

        # Scrape FPS page
        fps_data = scrape_fps(
            driver=driver,
            state=STATE,
            district=district,
            fps_id=fps_id,
        )

        print("\n========== SCRAPED DATA ==========\n")

        for key, value in fps_data.items():
            print(f"{key}: {value}")

        print("\n=================================\n")

        # Save CSV
        write_to_csv(
            fps_data=fps_data,
            month=MONTH,
            year=YEAR,
        )

        print("✓ CSV written successfully.")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
