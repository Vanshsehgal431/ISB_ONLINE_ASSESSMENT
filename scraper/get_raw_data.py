from browser import get_driver
from navigator import (click_fps_with_retry, get_districts, get_fps,
                       navigate_district, navigate_fps, navigate_state,
                       navigate_to_month)
from writer import write_to_csv

from scraper import scrape_fps

MONTH = 3
YEAR = 2026
STATE = "GOA"


def main():
    driver = get_driver()

    try:
        # First load to collect districts
        navigate_to_month(driver, MONTH, YEAR)
        navigate_state(driver, STATE)

        print(f"\nOpened State: {STATE}")

        districts = get_districts(driver)

        print(f"Districts Found: {districts}")

        if not districts:
            print("No districts found.")
            return

        # Loop through every district
        for district in districts:

            print(f"\n{'=' * 80}")
            print(f"Processing District : {district}")
            print(f"{'=' * 80}")

            # Reload state page for every district
            navigate_to_month(driver, MONTH, YEAR)
            navigate_state(driver, STATE)
            navigate_district(driver, district)
            navigate_fps(driver)

            fps_ids = get_fps(driver)

            print(f"Total FPS: {len(fps_ids)}")

            if not fps_ids:
                print(f"No FPS found in {district}")
                continue

            # Loop through every FPS
            for index, fps_id in enumerate(fps_ids, start=1):

                print(f"\n[{index}/{len(fps_ids)}] FPS : {fps_id}")

                try:
                    # Reload navigation for every FPS
                    navigate_to_month(driver, MONTH, YEAR)
                    navigate_state(driver, STATE)
                    navigate_district(driver, district)
                    navigate_fps(driver)

                    success = click_fps_with_retry(
                        driver,
                        fps_id,
                        max_retries=3,
                    )

                    if not success:
                        print(f"Skipping FPS {fps_id}")
                        continue

                    fps_data = scrape_fps(
                        driver=driver,
                        state=STATE,
                        district=district,
                        fps_id=fps_id,
                    )

                    write_to_csv(
                        fps_data=fps_data,
                        month=MONTH,
                        year=YEAR,
                    )

                    print(f"✓ Saved FPS {fps_id}")

                except Exception as e:
                    print(f"Error while scraping FPS {fps_id}")
                    print(e)
                    continue

        print("\nAll districts completed successfully.")

    except Exception as e:
        print("\nFatal Error:")
        print(e)

        import traceback
        traceback.print_exc()

    finally:
        driver.quit()


if __name__ == "__main__":
    main()    main()