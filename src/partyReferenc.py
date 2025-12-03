import json
import csv
import uuid
from datetime import datetime


def write_csv(base_filename, fieldnames, rows, load_id, load_date):
    # Append LoadID and UTC date to filename
    safe_date = (
        load_date.replace(":", "").replace("-", "").replace("T", "_").replace("Z", "")
    )
    filename = f"{base_filename}_{load_id}_{safe_date}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return filename


def log(message):
    with open("process.log", "a", encoding="utf-8") as logf:
        logf.write(f"{datetime.utcnow().isoformat()}Z - {message}\n")


def process_party(party_obj, load_id, load_date):
    addresses, formatted_addresses, emails, phones, individuals, organisations = (
        [],
        [],
        [],
        [],
        [],
        [],
    )

    def extract_address(addr, party_id, owner_type, addr_type):
        if not addr:
            return
        if "AddressLines" in addr:
            addresses.append(
                {
                    "LoadID": load_id,
                    "LoadDateUTC": load_date,
                    "PartyIdentifier": party_id,
                    "OwnerType": owner_type,
                    "AddressType": addr_type,
                    "AddressLines": "|".join(addr["AddressLines"]),
                }
            )
        if "FormattedAddress" in addr:
            fa = addr["FormattedAddress"]
            formatted_addresses.append(
                {
                    "LoadID": load_id,
                    "LoadDateUTC": load_date,
                    "PartyIdentifier": party_id,
                    "OwnerType": owner_type,
                    "AddressType": addr_type,
                    "BuildingName": fa.get("BuildingName"),
                    "City": fa.get("City"),
                    "CountryCode": fa.get("CountryCode"),
                    "PostCode": fa.get("PostCode"),
                    "StreetName": fa.get("StreetName"),
                    "StreetNumber": fa.get("StreetNumber"),
                    "Suburb": fa.get("Suburb"),
                    "TownName": fa.get("TownName"),
                }
            )

    # Individual
    ind = party_obj.get("IndividualDetails")
    if ind:
        party_id = ind.get("PartyIdentifier")
        individuals.append(
            {
                "LoadID": load_id,
                "LoadDateUTC": load_date,
                "PartyIdentifier": party_id,
                "OwnerType": "I",
                "FirstName": ind.get("FirstName"),
                "LastName": ind.get("LastName"),
                "MiddleName": ind.get("MiddleName"),
            }
        )
        for e in ind.get("Emails", []):
            emails.append(
                {
                    "LoadID": load_id,
                    "LoadDateUTC": load_date,
                    "PartyIdentifier": party_id,
                    "OwnerType": "I",
                    **e,
                }
            )
        for p in ind.get("Phones", []):
            phones.append(
                {
                    "LoadID": load_id,
                    "LoadDateUTC": load_date,
                    "PartyIdentifier": party_id,
                    "OwnerType": "I",
                    **p,
                }
            )
        extract_address(ind.get("PhysicalAddress"), party_id, "I", "Physical")
        extract_address(ind.get("PostalAddress"), party_id, "I", "Postal")
        extract_address(
            ind.get("PreviousPhysicalAddress"), party_id, "I", "PreviousPhysical"
        )

    # Organisation
    org = party_obj.get("OrganisationDetails")
    if org:
        party_id = org.get("PartyIdentifier")
        organisations.append(
            {
                "LoadID": load_id,
                "LoadDateUTC": load_date,
                "PartyIdentifier": party_id,
                "OwnerType": "O",
                "Name": org.get("Name"),
            }
        )
        for e in org.get("Emails", []):
            emails.append(
                {
                    "LoadID": load_id,
                    "LoadDateUTC": load_date,
                    "PartyIdentifier": party_id,
                    "OwnerType": "O",
                    **e,
                }
            )
        for p in org.get("Phones", []):
            phones.append(
                {
                    "LoadID": load_id,
                    "LoadDateUTC": load_date,
                    "PartyIdentifier": party_id,
                    "OwnerType": "O",
                    **p,
                }
            )
        extract_address(org.get("PhysicalAddress"), party_id, "O", "Physical")
        extract_address(org.get("PostalAddress"), party_id, "O", "Postal")

    return addresses, formatted_addresses, emails, phones, individuals, organisations


if __name__ == "__main__":
    # Generate LoadID and LoadDateUTC
    load_id = str(uuid.uuid4())
    load_date = datetime.utcnow().isoformat() + "Z"

    log(f"Starting load {load_id} at {load_date}")

    with open("input.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    all_addresses, all_formatted, all_emails, all_phones, all_individuals, all_orgs = (
        [],
        [],
        [],
        [],
        [],
        [],
    )

    for party in data:
        addresses, formatted_addresses, emails, phones, individuals, organisations = (
            process_party(party, load_id, load_date)
        )
        all_addresses.extend(addresses)
        all_formatted.extend(formatted_addresses)
        all_emails.extend(emails)
        all_phones.extend(phones)
        all_individuals.extend(individuals)
        all_orgs.extend(organisations)
        log(
            f"Processed party {party.get('IndividualDetails', {}).get('PartyIdentifier') or party.get('OrganisationDetails', {}).get('PartyIdentifier')}"
        )

    # Write CSVs with LoadID + Date in filenames
    write_csv(
        "addresses",
        [
            "LoadID",
            "LoadDateUTC",
            "PartyIdentifier",
            "OwnerType",
            "AddressType",
            "AddressLines",
        ],
        all_addresses,
        load_id,
        load_date,
    )
    write_csv(
        "formattedAddresses",
        [
            "LoadID",
            "LoadDateUTC",
            "PartyIdentifier",
            "OwnerType",
            "AddressType",
            "BuildingName",
            "City",
            "CountryCode",
            "PostCode",
            "StreetName",
            "StreetNumber",
            "Suburb",
            "TownName",
        ],
        all_formatted,
        load_id,
        load_date,
    )
    write_csv(
        "emails",
        [
            "LoadID",
            "LoadDateUTC",
            "PartyIdentifier",
            "OwnerType",
            "EmailAddress",
            "IsPrimary",
        ],
        all_emails,
        load_id,
        load_date,
    )
    write_csv(
        "phones",
        [
            "LoadID",
            "LoadDateUTC",
            "PartyIdentifier",
            "OwnerType",
            "PhoneNumber",
            "IsPrimary",
            "Type",
        ],
        all_phones,
        load_id,
        load_date,
    )
    write_csv(
        "individual",
        [
            "LoadID",
            "LoadDateUTC",
            "PartyIdentifier",
            "OwnerType",
            "FirstName",
            "LastName",
            "MiddleName",
        ],
        all_individuals,
        load_id,
        load_date,
    )
    write_csv(
        "organisation",
        ["LoadID", "LoadDateUTC", "PartyIdentifier", "OwnerType", "Name"],
        all_orgs,
        load_id,
        load_date,
    )

    log(f"Completed load {load_id} with {len(data)} parties processed")
