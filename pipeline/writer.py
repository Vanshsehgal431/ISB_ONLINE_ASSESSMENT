import os

import pandas as pd


def write_to_csv(fps_data, month, year):
    """
    write_to_csv(): Write the sraped data into csv files
    Args :
        fps_data : scraped data
        month : which month data it is.
        year : which year data it is.
    Return
        nothing
    """
    # Extract district
    district = fps_data["District"].strip().replace("/", "-").replace("\\", "-")

    # Extract fps id for file_name.
    fps_id = fps_data["FPS ID"]

    # Create data/raw
    output_dir = os.path.join(
        "data",
        "raw",
        f"{month}-{year}",
        district,
    )

    # Create folders if they don't exist
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, f"{fps_id}.csv")

    # Save file
    pd.DataFrame([fps_data]).to_csv(
        file_path,
        index=False,
        encoding="utf-8-sig",
    )
