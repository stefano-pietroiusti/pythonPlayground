import json
import csv
import uuid
from datetime import datetime

# Load schema
with open("party_schema.json", "r", encoding="utf-8") as f:
    schema = json.load(f)


def write_csv(base_filename, rows, schema_def, load_id, load_date):
    # Build headers dynamically from schema definition
    fieldnames = ["LoadID", "LoadDateUTC", "PartyIdentifier", "OwnerType"]
    if "AddressType" in rows[0]:
        fieldnames.append("AddressType")
    fieldnames.extend(schema_def["properties"].keys())

    # Append LoadID + UTC date to filename
    safe_date = (
        load_date.replace(":", "").replace("-", "").replace("T", "_").replace("Z", "")
    )
    filename = f"{base_filename}_{load_id}_{safe_date}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return filename, len(rows)


def log(message):
    with open("process.log", "a", encoding="utf-8") as logf:
        logf.write(f"{datetime.utcnow().isoformat()}Z - {message}\n")


def flatten_array(array, schema_def, extra_fields):
    rows = []
    for item in array:
        row = {prop: item.get(prop) for prop in schema_def["properties"].keys()}
        row.update(extra_fields)
        rows.append(row)
    return rows


if __name__ == "__main__":
    # Generate LoadID and LoadDateUTC
    load_id = str(uuid.uuid4())
    load_date = datetime.utcnow().isoformat() + "Z"
    log(f"Starting load {load_id} at {load_date}")

    with open("input.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    all_emails, all_phones, all_addresses, all_formatted, all_individuals, all_orgs = (
        [],
        [],
        [],
        [],
        [],
        [],
    )

    for party in data:
        # Individual
        ind = party.get("IndividualDetails")
        if ind:
            pid = ind.get("PartyIdentifier")
            all_individuals.append(
                {
                    "LoadID": load_id,
                    "LoadDateUTC": load_date,
                    "PartyIdentifier": pid,
                    "OwnerType": "I",
                    "FirstName": ind.get("FirstName"),
                    "LastName": ind.get("LastName"),
                    "MiddleName": ind.get("MiddleName"),
                }
            )
            all_emails.extend(
                flatten_array(
                    ind.get("Emails", []),
                    schema["definitions"]["email"],
                    {
                        "LoadID": load_id,
                        "LoadDateUTC": load_date,
                        "PartyIdentifier": pid,
                        "OwnerType": "I",
                    },
                )
            )
            all_phones.extend(
                flatten_array(
                    ind.get("Phones", []),
                    schema["definitions"]["phone"],
                    {
                        "LoadID": load_id,
                        "LoadDateUTC": load_date,
                        "PartyIdentifier": pid,
                        "OwnerType": "I",
                    },
                )
            )
            for addr_type in [
                "PhysicalAddress",
                "PostalAddress",
                "PreviousPhysicalAddress",
            ]:
                addr = ind.get(addr_type)
                if addr:
                    # AddressLines
                    all_addresses.append(
                        {
                            "LoadID": load_id,
                            "LoadDateUTC": load_date,
                            "PartyIdentifier": pid,
                            "OwnerType": "I",
                            "AddressType": addr_type.replace("Address", ""),
                            "AddressLines": "|".join(addr.get("AddressLines", [])),
                        }
                    )
                    # FormattedAddress
                    fa = addr.get("FormattedAddress", {})
                    fa_row = {
                        prop: fa.get(prop)
                        for prop in schema["definitions"]["address"]["properties"][
                            "FormattedAddress"
                        ]["properties"].keys()
                    }
                    fa_row.update(
                        {
                            "LoadID": load_id,
                            "LoadDateUTC": load_date,
                            "PartyIdentifier": pid,
                            "OwnerType": "I",
                            "AddressType": addr_type.replace("Address", ""),
                        }
                    )
                    all_formatted.append(fa_row)

        # Organisation
        org = party.get("OrganisationDetails")
        if org:
            pid = org.get("PartyIdentifier")
            all_orgs.append(
                {
                    "LoadID": load_id,
                    "LoadDateUTC": load_date,
                    "PartyIdentifier": pid,
                    "OwnerType": "O",
                    "Name": org.get("Name"),
                }
            )
            all_emails.extend(
                flatten_array(
                    org.get("Emails", []),
                    schema["definitions"]["email"],
                    {
                        "LoadID": load_id,
                        "LoadDateUTC": load_date,
                        "PartyIdentifier": pid,
                        "OwnerType": "O",
                    },
                )
            )
            all_phones.extend(
                flatten_array(
                    org.get("Phones", []),
                    schema["definitions"]["phone"],
                    {
                        "LoadID": load_id,
                        "LoadDateUTC": load_date,
                        "PartyIdentifier": pid,
                        "OwnerType": "O",
                    },
                )
            )
            for addr_type in ["PhysicalAddress", "PostalAddress"]:
                addr = org.get(addr_type)
                if addr:
                    all_addresses.append(
                        {
                            "LoadID": load_id,
                            "LoadDateUTC": load_date,
                            "PartyIdentifier": pid,
                            "OwnerType": "O",
                            "AddressType": addr_type.replace("Address", ""),
                            "AddressLines": "|".join(addr.get("AddressLines", [])),
                        }
                    )
                    fa = addr.get("FormattedAddress", {})
                    fa_row = {
                        prop: fa.get(prop)
                        for prop in schema["definitions"]["address"]["properties"][
                            "FormattedAddress"
                        ]["properties"].keys()
                    }
                    fa_row.update(
                        {
                            "LoadID": load_id,
                            "LoadDateUTC": load_date,
                            "PartyIdentifier": pid,
                            "OwnerType": "O",
                            "AddressType": addr_type.replace("Address", ""),
                        }
                    )
                    all_formatted.append(fa_row)

    # Write CSVs dynamically
    files = []
    if all_emails:
        files.append(
            write_csv(
                "emails", all_emails, schema["definitions"]["email"], load_id, load_date
            )
        )
    if all_phones:
        files.append(
            write_csv(
                "phones", all_phones, schema["definitions"]["phone"], load_id, load_date
            )
        )
    if all_addresses:
        files.append(
            write_csv(
                "addresses",
                all_addresses,
                {"properties": {"AddressLines": {"type": "string"}}},
                load_id,
                load_date,
            )
        )
    if all_formatted:
        files.append(
            write_csv(
                "formattedAddresses",
                all_formatted,
                schema["definitions"]["address"]["properties"]["FormattedAddress"],
                load_id,
                load_date,
            )
        )
    if all_individuals:
        files.append(
            write_csv(
                "individual",
                all_individuals,
                schema["properties"]["IndividualDetails"],
                load_id,
                load_date,
            )
        )
    if all_orgs:
        files.append(
            write_csv(
                "organisation",
                all_orgs,
                schema["properties"]["OrganisationDetails"],
                load_id,
                load_date,
            )
        )

    # Log summary
    for fname, count in files:
        log(f"Wrote {count} rows to {fname}")

    log(f"Completed load {load_id} with {len(data)} parties processed")
