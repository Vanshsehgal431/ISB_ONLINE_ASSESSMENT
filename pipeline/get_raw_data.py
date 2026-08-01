import json

from browser import get_driver
from logger import logger
from navigator import (
    click_fps_with_retry,
    get_districts,
    get_fps,
    navigate_district,
    navigate_fps,
    navigate_state,
    navigate_to_month,
)
from scraper import scrape_fps
from writer import write_to_csv

MONTH = [3, 4]
YEAR = 2026
STATE = "GOA"
MAX_RETRY_ROUNDS = 2


def get_raw_data():
    # Init driver
    driver = get_driver()

    try:
        # Process each month
        for month in MONTH:

            logger.info(f"Starting month {month}/{YEAR}")

            # Track failed FPS for retry
            failed_fps = []

            # Navigate to month and state
            navigate_to_month(
                driver, month, YEAR
            )  # FIXED: pass month directly, not [month]
            navigate_state(driver, STATE)

            logger.info(f"Opened state: {STATE}")

            # Get all districts
            districts = get_districts(driver)

            logger.info(f"Districts found: {districts}")

            if not districts:
                logger.warning("No districts found.")
                continue

            # First pass - scrape all fps for each district
            for district in districts:

                logger.info(f"Processing district: {district}")

                navigate_to_month(driver, month, YEAR)  # FIXED: pass month directly
                navigate_state(driver, STATE)
                navigate_district(driver, district)
                navigate_fps(driver)

                # Get all fps for this district
                fps_ids = get_fps(driver)

                logger.info(f"Found {len(fps_ids)} FPS shops.")

                if not fps_ids:
                    logger.warning(f"No FPS found in district: {district}")
                    continue

                # Iterate over fps_ids
                for index, fps_id in enumerate(fps_ids, start=1):

                    logger.info(f"[{index}/{len(fps_ids)}] Processing FPS: {fps_id}")

                    try:
                        success = click_fps_with_retry(
                            driver,
                            fps_id,
                            max_retries=3,
                        )

                        if not success:
                            failed_fps.append(
                                {
                                    "district": district,
                                    "fps_id": fps_id,
                                    "month": month,
                                }
                            )
                            continue

                        fps_data = scrape_fps(
                            driver=driver,
                            state=STATE,
                            district=district,
                            fps_id=fps_id,
                        )

                        write_to_csv(
                            fps_data=fps_data,
                            month=month,
                            year=YEAR,
                        )

                        logger.info(f"Saved FPS {fps_id}")

                    except Exception:
                        logger.exception(f"Error while scraping FPS {fps_id}")

                        failed_fps.append(
                            {
                                "district": district,
                                "fps_id": fps_id,
                                "month": month,
                            }
                        )

                # Retry failed FPS - max 2 rounds, only from current district

                for retry_round in range(1, MAX_RETRY_ROUNDS + 1):

                    district_failed = [
                        item
                        for item in failed_fps
                        if item["district"] == district and item["month"] == month
                    ]

                    if not district_failed:
                        logger.info(f"All failed FPS recovered for {district}")
                        break

                    logger.info(
                        f"Retry round {retry_round} for {district} - {len(district_failed)} failed FPS"
                    )

                    remaining_failed = []

                    # Navigate to FPS list for retry
                    try:
                        navigate_to_month(
                            driver, month, YEAR
                        )  # FIXED: pass month directly
                        navigate_state(driver, STATE)
                        navigate_district(driver, district)
                        navigate_fps(driver)
                    except Exception:
                        logger.exception(f"Nav failed - retry in {district}")
                        remaining_failed.extend(district_failed)
                        failed_fps = [
                            item for item in failed_fps if item not in district_failed
                        ] + remaining_failed
                        continue

                    for item in district_failed:

                        fps_id = item["fps_id"]

                        logger.info(f"Retrying {fps_id}")

                        try:
                            success = click_fps_with_retry(
                                driver,
                                fps_id,
                                max_retries=3,
                            )

                            if not success:
                                remaining_failed.append(item)
                                continue

                            fps_data = scrape_fps(
                                driver=driver,
                                state=STATE,
                                district=district,
                                fps_id=fps_id,
                            )

                            write_to_csv(
                                fps_data=fps_data,
                                month=month,
                                year=YEAR,
                            )

                            logger.info(f"Retry ok - FPS {fps_id}")

                        except Exception:
                            logger.exception(f"Retry failed - FPS {fps_id}")
                            remaining_failed.append(item)

                    # Update failed_fps list
                    failed_fps = [
                        item for item in failed_fps if item not in district_failed
                    ] + remaining_failed

            # Save failed FPS record per month
            month_record_file = f"record_{month}-{YEAR}.json"
            with open(month_record_file, "w") as file:
                json.dump(failed_fps, file, indent=4)
            logger.info(f"Saved record: {month_record_file}")

        logger.info("Done - all months scraped")

    except Exception:
        logger.exception("Fatal error while running scraper.")

    finally:
        driver.quit()


if __name__ == "__main__":
    get_raw_data()
