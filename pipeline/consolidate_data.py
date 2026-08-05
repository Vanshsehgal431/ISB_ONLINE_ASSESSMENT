import json
from pathlib import Path

import numpy as np
import pandas as pd
from logger import logger

output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)


def clean_numeric(value):
    """
    clean_numeric() : Convert string values to numeric, stripping commas and handling blanks.

    Args:
        value -> The value to convert (can be string, int, float, or NaN).

    Returns:
        Float value or NaN if conversion fails.
    """

    # Handle NaN and empty strings
    if pd.isna(value) or value == "":
        return np.nan

    # If already numeric, just convert to float
    if isinstance(value, (int, float)):
        return float(value)

    # Convert to string and strip whitespace
    value_str = str(value).strip()

    # Check for NA indicators
    if value_str == "" or value_str.lower() in ["na", "n/a", "none"]:
        return np.nan

    # Remove commas and convert to float
    try:
        cleaned = value_str.replace(",", "")
        return float(cleaned)
    except ValueError:
        logger.warning(f"Could not convert '{value_str}' to numeric. Returning NaN.")
        return np.nan


def standardize_column_names(df):
    """
    standardize_column_names() : Convert column names to snake_case format.

    Args:
        df -> Pandas DataFrame with original column names.

    Returns:
        DataFrame with standardized column names (lowercase, underscores, no special chars).
    """

    # Apply transformations: lowercase -> remove special chars -> replace spaces with underscores
    df.columns = (
        df.columns.str.lower()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
        .str.strip("_")
    )

    return df


def identify_numeric_columns(df):
    """
    identify_numeric_columns() : Find columns that should be treated as numeric.

    Args:
        df -> Pandas DataFrame to inspect.

    Returns:
        List of column names that match numeric keywords.
    """

    # Keywords that indicate numeric columns
    numeric_keywords = [
        "transaction",
        "ration",
        "card",
        "wheat",
        "rice",
        "barley",
        "bajra",
        "maize",
        "jowar",
        "ragi",
        "kodo",
        "commodity",
        "authenticated",
        "total",
    ]

    # Collect columns that contain any numeric keyword
    numeric_cols = []
    for col in df.columns:
        if any(keyword in col for keyword in numeric_keywords):
            numeric_cols.append(col)

    return numeric_cols


def clean_dataframe(df):
    """
    clean_dataframe() : Apply cleaning to dataframe (standardize names and numeric fields).

    Args:
        df -> Pandas DataFrame to clean.

    Returns:
        Cleaned DataFrame with standardized columns and numeric values.
    """

    # Standardize column names
    df = standardize_column_names(df)

    # Identify and clean numeric columns
    numeric_cols = identify_numeric_columns(df)

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric)

    return df


def validate_data_quality(combined_df):
    """
    validate_data_quality() : Check data quality and flag inconsistencies.

    Args:
        combined_df -> Consolidated Pandas DataFrame.

    Returns:
        Dictionary containing quality report with missing values, inactive FPS, and anomalies.
    """

    # Initialize report structure
    report = {
        "total_records": len(combined_df),
        "total_fps": (
            combined_df["fps_id"].nunique()
            if "fps_id" in combined_df.columns
            else "N/A"
        ),
        "months_covered": (
            sorted(combined_df["month_year"].unique().tolist())
            if "month_year" in combined_df.columns
            else []
        ),
        "districts_covered": (
            sorted(combined_df["district"].unique().tolist())
            if "district" in combined_df.columns
            else []
        ),
        "missing_values": {},
        "inactive_fps": [],
        "data_anomalies": [],
    }

    # Check for missing values per column
    missing_counts = combined_df.isnull().sum()
    report["missing_values"] = missing_counts[missing_counts > 0].to_dict()

    # Identify FPS with zero transactions (likely data loading issues)
    if "total_e_transaction" in combined_df.columns:
        inactive = combined_df[combined_df["total_e_transaction"] == 0]
        if len(inactive) > 0:
            report["inactive_fps"] = inactive[
                ["fps_id", "district", "month_year"]
            ].to_dict("records")

    # Check for negative values in transaction columns (should not occur)
    transaction_cols = [col for col in combined_df.columns if "transaction" in col]
    for col in transaction_cols:
        if col in combined_df.columns:
            negatives = combined_df[combined_df[col] < 0]
            if len(negatives) > 0:
                report["data_anomalies"].append(
                    {"column": col, "issue": "negative_values", "count": len(negatives)}
                )

    # Validate commodity totals match sum of parts (e.g., wheat_total = wheat_regular + wheat_intra_state + wheat_inter_state)
    commodities = {
        "wheat": ["wheat_regular", "wheat_intra_state", "wheat_inter_state"],
        "rice": ["rice_regular", "rice_intra_state", "rice_inter_state"],
        "barley": ["barley_regular", "barley_intra_state", "barley_inter_state"],
        "total_commodity": [
            "total_commodity_regular",
            "total_commodity_intra_state",
            "total_commodity_inter_state",
        ],
    }

    for commodity_name, parts in commodities.items():
        total_col = f"{commodity_name}_total"
        if total_col in combined_df.columns and all(
            p in combined_df.columns for p in parts
        ):
            mismatches = 0
            for _, row in combined_df.iterrows():
                if pd.notna(row[total_col]) and all(pd.notna(row[p]) for p in parts):
                    calc_total = row[parts].sum()
                    # Allow small floating point differences
                    if abs(row[total_col] - calc_total) > 0.01:
                        mismatches += 1

            if mismatches > 0:
                report["data_anomalies"].append(
                    {
                        "column": total_col,
                        "issue": "total_mismatch_with_parts",
                        "count": mismatches,
                    }
                )

    return report


def consolidate_data():
    """
    consolidate_data() : Main consolidation workflow - load, combine, clean, validate, and save FPS data.

    Workflow:
    1. Recursively find all CSV files in data/raw
    2. Extract month_year and district from folder structure (data/raw/month_year/district/file.csv)
    3. Combine all dataframes (flattens nested tables automatically)
    4. Standardize column names and clean numeric fields (strip commas, handle blanks)
    5. Validate data quality and flag inconsistencies (missing values, inactive FPS, anomalies)
    6. Save consolidated CSV and quality report JSON

    Args:
        None

    Returns:
        None
    """

    logger.info("Started consolidating FPS data...")

    # Find all CSV files in data/raw (recursive search)
    base_path = Path("data/raw")
    all_files = sorted(list(base_path.rglob("*.csv")))

    if not all_files:
        logger.warning("No CSV files found in data/raw!")
        return

    logger.info(f"Found {len(all_files)} CSV files to process.")

    # Load all CSVs and extract month_year and district from folder structure
    df_list = []
    file_errors = []

    for file_path in all_files:
        try:
            df = pd.read_csv(file_path)

            # Extract month_year from: data/raw / month_year / district / file.csv
            month_year = file_path.parts[-3]
            district = file_path.parts[-2]

            df["month_year"] = month_year
            df["district"] = district

            print(
                f"Loaded {file_path.name} from {district} ({month_year}) - {len(df)} rows"
            )
            df_list.append(df)

        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            file_errors.append({"file": str(file_path), "error": str(e)})

    if not df_list:
        logger.error("No dataframes loaded. Exiting consolidation.")
        return

    # Combine all dataframes (flattens nested tables into columns automatically)
    logger.info(f"Combining {len(df_list)} dataframes...")
    combined_df = pd.concat(df_list, ignore_index=True)
    logger.info(f"Combined dataframe shape: {combined_df.shape}")

    # Clean the data: standardize column names and numeric fields
    logger.info("Cleaning data - standardizing columns and numeric values...")
    combined_df = clean_dataframe(combined_df)

    # Validate data quality and flag inconsistencies
    logger.info("Validating data quality...")
    quality_report = validate_data_quality(combined_df)

    # Save consolidated CSV
    output_csv = output_dir / "fps-level-records-Goa.csv"
    combined_df.to_csv(output_csv, index=False)
    logger.info(f"Consolidated data saved to {output_csv}")

    # Save quality report as JSON
    output_report = output_dir / "data-quality-report.json"
    with open(output_report, "w") as f:
        report_serializable = json.loads(
            json.dumps(
                quality_report,
                default=lambda x: (
                    int(x) if isinstance(x, (np.integer, np.floating)) else str(x)
                ),
            )
        )
        json.dump(report_serializable, f, indent=2)
    logger.info(f"Data quality report saved to {output_report}")

    # Log consolidation summary
    logger.info("=" * 70)
    logger.info("CONSOLIDATION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total records: {quality_report['total_records']}")
    logger.info(f"Total FPS: {quality_report['total_fps']}")
    logger.info(f"Months covered: {', '.join(quality_report['months_covered'])}")
    logger.info(f"Districts covered: {', '.join(quality_report['districts_covered'])}")

    # Log warnings for data quality issues
    if quality_report["missing_values"]:
        logger.warning(
            f"Missing values detected in {len(quality_report['missing_values'])} columns"
        )

    if quality_report["inactive_fps"]:
        logger.warning(
            f"Inactive FPS (no transactions): {len(quality_report['inactive_fps'])}"
        )
        for fps in quality_report["inactive_fps"][:3]:
            logger.warning(
                f"  - FPS {fps['fps_id']} in {fps['district']} ({fps['month_year']})"
            )

    if quality_report["data_anomalies"]:
        logger.warning(
            f"Data anomalies detected: {len(quality_report['data_anomalies'])}"
        )
        for anomaly in quality_report["data_anomalies"]:
            logger.warning(
                f"  - {anomaly['column']}: {anomaly['issue']} ({anomaly['count']} records)"
            )

    if file_errors:
        logger.warning(f"File read errors: {len(file_errors)}")
        for error in file_errors[:3]:
            logger.warning(f"  - {error['file']}: {error['error']}")

    logger.info("=" * 70)
    logger.info("Consolidation complete!")


if __name__ == "__main__":
    consolidate_data()
