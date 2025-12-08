import json
import csv
import os
import uuid
import logging
from datetime import datetime, timezone
import pyodbc
import pandas as pd
from sqlalchemy import create_engine


def normalize_key(key: str) -> str:
    return key.strip().lower()


def flatten_address(
    addr: dict, party_id: str, run_guid: str, run_date_local: str, run_date_utc: str
) -> dict:
    flat = {
        "partyidentifier": party_id,
        "run_guid": run_guid,
        "run_date_local": run_date_local,
        "run_date_utc": run_date_utc,
    }
    if not addr:
        return flat
    if "AddressLines" in addr and addr["AddressLines"]:
        flat["addresslines"] = " | ".join(addr["AddressLines"])
    if "FormattedAddress" in addr and addr["FormattedAddress"]:
        for k, v in addr["FormattedAddress"].items():
            flat[normalize_key(k)] = v
    return flat


def lower_dict_keys(record: dict) -> dict:
    return {normalize_key(k): v for k, v in record.items()}


def write_csv(file_path, records):
    if not records:
        logging.info(f"No records to write for {file_path}")
        return
    records = [lower_dict_keys(r) for r in records]
    headers = set()
    for r in records:
        headers.update(r.keys())
    ordered_headers = []
    if "partyidentifier" in headers:
        ordered_headers.append("partyidentifier")
    middle_headers = sorted(
        [
            h
            for h in headers
            if h
            not in ["partyidentifier", "run_guid", "run_date_local", "run_date_utc"]
        ]
    )
    ordered_headers.extend(middle_headers)
    for tail in ["run_guid", "run_date_local", "run_date_utc"]:
        if tail in headers:
            ordered_headers.append(tail)
    logging.info(f"Writing {len(records)} records to {file_path}")
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ordered_headers)
        writer.writeheader()
        writer.writerows(records)


# def bulk_upload_to_sql(csv_dir, server, database, user, password):
#     """Bulk upload each CSV in csv_dir to SQL Server, drop/recreate tables dynamically."""
#     conn_str = (
#         f"DRIVER={{ODBC Driver 17 for SQL Server}};"
#         f"SERVER={server};DATABASE={database};UID={user};PWD={password};TrustServerCertificate=yes;"
#     )
#     conn = pyodbc.connect(conn_str)
#     cursor = conn.cursor()

#     for file in os.listdir(csv_dir):
#         if file.endswith(".csv"):
#             table_name = os.path.splitext(file)[0]
#             file_path = os.path.join(csv_dir, file)
#             logging.info(f"Uploading {file_path} to table {table_name}")

#             # Drop table if exists
#             cursor.execute(
#                 f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE {table_name};"
#             )
#             conn.commit()

#             # Load CSV into pandas
#             df = pd.read_csv(file_path)

#             # Create table dynamically using SELECT * INTO
#             # Write to a temp table first
#             temp_table = f"##temp_{table_name}"
#             df.to_sql(
#                 temp_table, conn, if_exists="replace", index=False
#             )  # requires sqlalchemy, alternative below

#             # Alternative: use OPENROWSET (simpler, no pandas dependency)
#             cursor.execute(f"""
#                 SELECT * INTO {table_name}
#                 FROM OPENROWSET(
#                     BULK '{file_path}',
#                     FORMAT='CSV',
#                     FIRSTROW=2
#                 ) AS rows;
#             """)
#             conn.commit()

#     cursor.close()
#     conn.close()
#     logging.info("Bulk upload complete.")


def bulk_upload_to_sql(csv_dir, server, database, user, password):
    """
    Bulk upload each CSV in csv_dir to SQL Server using SQLAlchemy + pyodbc.
    Tables are dropped/recreated dynamically.
    """
    # Build SQLAlchemy connection string
    conn_str = (
        f"mssql+pyodbc://{user}:{password}@{server}/{database}"
        "?driver=ODBC+Driver+17+for+SQL+Server"
    )
    engine = create_engine(conn_str, fast_executemany=True)

    for file in os.listdir(csv_dir):
        if file.lower().endswith(".csv"):
            table_name = os.path.splitext(file)[0]
            file_path = os.path.join(csv_dir, file)
            logging.info(f"Uploading {file_path} to table {table_name}")

            # Load CSV into pandas
            df = pd.read_csv(file_path)

            # Drop/recreate table
            df.to_sql(
                table_name,
                engine,
                if_exists="replace",  # or "append" depending on your needs
                index=False,
                method="multi",  # efficient batch insert
            )

    logging.info("Bulk upload complete.")


def process_json(json_data, base_output_dir="src/data"):
    run_guid = str(uuid.uuid4())
    run_date_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_date_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    output_dir = os.path.join(base_output_dir, run_guid)
    os.makedirs(output_dir, exist_ok=True)

    logging.info(f"Run GUID: {run_guid}")
    logging.info(f"Run Local Date: {run_date_local}")
    logging.info(f"Run UTC Date: {run_date_utc}")
    logging.info(f"Output directory: {output_dir}")

    emails, phones, postal_addresses, physical_addresses, previous_addresses = (
        [],
        [],
        [],
        [],
        [],
    )

    logging.info("Starting JSON processing...")
    for obj in json_data:
        details = None
        for k, v in obj.items():
            if normalize_key(k) in ["individualdetails", "organisationdetails"]:
                details = v
                break
        if not details:
            continue
        party_id = details.get("PartyIdentifier")

        for email in details.get("Emails", []):
            rec = {
                "partyidentifier": party_id,
                "run_guid": run_guid,
                "run_date_local": run_date_local,
                "run_date_utc": run_date_utc,
            }
            rec.update(email)
            emails.append(rec)

        for phone in details.get("Phones", []):
            rec = {
                "partyidentifier": party_id,
                "run_guid": run_guid,
                "run_date_local": run_date_local,
                "run_date_utc": run_date_utc,
            }
            rec.update(phone)
            phones.append(rec)

        if details.get("PhysicalAddress"):
            physical_addresses.append(
                flatten_address(
                    details["PhysicalAddress"],
                    party_id,
                    run_guid,
                    run_date_local,
                    run_date_utc,
                )
            )
        if details.get("PostalAddress"):
            postal_addresses.append(
                flatten_address(
                    details["PostalAddress"],
                    party_id,
                    run_guid,
                    run_date_local,
                    run_date_utc,
                )
            )
        if details.get("PreviousPhysicalAddress"):
            previous_addresses.append(
                flatten_address(
                    details["PreviousPhysicalAddress"],
                    party_id,
                    run_guid,
                    run_date_local,
                    run_date_utc,
                )
            )

    logging.info("Finished processing JSON. Writing CSVs...")
    write_csv(os.path.join(output_dir, "emails.csv"), emails)
    write_csv(os.path.join(output_dir, "phones.csv"), phones)
    write_csv(os.path.join(output_dir, "physical_addresses.csv"), physical_addresses)
    write_csv(os.path.join(output_dir, "postal_addresses.csv"), postal_addresses)
    write_csv(
        os.path.join(output_dir, "previous_physical_addresses.csv"), previous_addresses
    )

    logging.info("CSV files written. Starting bulk upload...")
    bulk_upload_to_sql(
        output_dir,
        server="LAPTOP-4HIJQT67\\SQLEXPRESS",
        database="CRMDSL",
        user="sa",
        password="St3fan0p!",
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    input_path = os.path.join("src", "json", "input.json")
    logging.info(f"Loading input JSON from {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        sample_json = json.load(f)
    process_json(sample_json, base_output_dir=os.path.join("src", "data"))
