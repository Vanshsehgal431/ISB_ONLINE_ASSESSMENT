from pathlib import Path

import pandas as pd
from logger import logger

output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)


def consolidate_data():
    logger.info("Started consolidating data ... ")

    # 1. Point directly to 'data/raw' and use rglob to search recursively
    base_path = Path("data/raw")
    all_files = list(base_path.rglob("*.csv"))

    if not all_files:
        logger.warning("No CSV files found in data/raw!")
        return

    df_list = []

    for file_path in all_files:
        df = pd.read_csv(file_path)

        # 2. Extract month-year from the folder structure:
        # data/raw / month-year / district_name / file.csv
        # file_path.parts[-3] targets the month-year folder
        month_year = file_path.parts[-3]
        df["Month-Year"] = month_year

        df_list.append(df)

    combined_df = pd.concat(df_list, ignore_index=True)
    output_file = output_dir / "fps-level-records-Goa.csv"

    combined_df.to_csv(output_file, index=False)
    logger.info(f"Consolidation finished. Saved to {output_file}")


if __name__ == "__main__":
    consolidate_data()
