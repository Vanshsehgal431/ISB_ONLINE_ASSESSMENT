import os

import pandas as pd


def write_to_csv(fps_data, month, year):
    district = fps_data["District"].strip().replace("/", "-").replace("\\", "-")

    fps_id = fps_data["FPS ID"]

    output_dir = os.path.join(
        "data",
        "raw",
        f"{month}-{year}",
        district,
    )

    # Create folders if they don't exist
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, f"{fps_id}.csv")

    pd.DataFrame([fps_data]).to_csv(
        file_path,
        index=False,
        encoding="utf-8-sig",
    )
