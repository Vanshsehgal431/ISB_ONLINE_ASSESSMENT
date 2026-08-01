# from test import main

from consolidate_data import consolidate_data
from get_raw_data import get_raw_data
from logger import logger


def run_pipeline():
    logger.info("Running the pipeline ... ")
    logger.info("Getting the raw data ... ")

    get_raw_data()

    logger.info("Extraction finished.")
    logger.info("Consolidating Data ...")

    consolidate_data()

    logger.info("Consolidation finished.")
    logger.info("Pipeline ran successfully!")


if __name__ == "__main__":
    run_pipeline()
