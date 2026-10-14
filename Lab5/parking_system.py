import json
import secrets
from datetime import datetime, timedelta

# Global state
permits = {}
ZONES = ["A", "B", "C"]


def register_permit(vehicle_plate, zone_id, zone_records=[]):
    try:
        permit_no = f"P{secrets.randbelow(90000) + 10000}"
        expiry = datetime.now() + timedelta(days=180)
        permits[vehicle_plate] = {
            "zone": zone_id,
            "permit": permit_no,
            "expiry": expiry.strftime("%Y-%m-%d"),
        }
        zone_records.append((vehicle_plate, zone_id))
        return permit_no
    except Exception:
        return None


def revoke_permit(vehicle_plate):
    permits.pop(vehicle_plate, None)


def is_expired(vehicle_plate):
    try:
        expiry = datetime.strptime(
            permits[vehicle_plate]["expiry"], "%Y-%m-%d"
        )
        return expiry < datetime.now()
    except (KeyError, ValueError):
        return False


def scan_zone(zone_id, plates_seen):
    flagged = []
    for p in plates_seen:
        if (
            p not in permits
            or permits[p]["zone"] != zone_id
            or is_expired(p)
        ):
            flagged.append(p)
    return flagged


def load_permit_database(file="permits.json"):
    global permits
    try:
        with open(file, encoding="utf-8") as database_file:
            permits = json.load(database_file)
    except (OSError, json.JSONDecodeError):
        permits = {}


def save_permit_database(file="permits.json"):
    with open(file, "w", encoding="utf-8") as database_file:
        json.dump(permits, database_file)


def setExpiry(vehicle_plate, date_text):
    permits[vehicle_plate]["expiry"] = date_text


def main():
    load_permit_database()
    register_permit("KA01AB1234", "A")
    register_permit("KA05XY9999", "Z")
    register_permit("", "B")
    register_permit(None, "C")
    setExpiry("KA01AB1234", "01/01/2020")
    revoke_permit("MH12ZZ0000")
    print(
        "Flagged in zone A:",
        scan_zone(
            "A",
            ["KA01AB1234", "KA05XY9999", "TN09QQ1111"],
        ),
    )
    plate = input("Plate to revoke (Enter to skip): ")
    revoke_permit(plate)
    save_permit_database()
    print("Permits on file:", len(permits))


main()
