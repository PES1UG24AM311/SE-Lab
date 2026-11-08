def parse_transit_corridor(corridor_code):
    """Parse a transit corridor code of the form ORIG-DEST-ZONES.

    Defensive: never crashes on unexpected input. Returns a descriptive
    error string when the input cannot be parsed.
    """
    if corridor_code is None or not isinstance(corridor_code, str):
        return "Error: corridor code must be a non-empty string."
    corridor_code = corridor_code.strip()
    if not corridor_code:
        return "Error: corridor code must be a non-empty string."
    parts = corridor_code.split('-')
    if len(parts) != 3:
        return (f"Error: invalid corridor code '{corridor_code}'. "
                f"Expected format ORIG-DEST-ZONES.")
    orig, dest, zones_str = parts
    if not orig or not dest or not zones_str:
        return (f"Error: invalid corridor code '{corridor_code}'. "
                f"All three fields (origin, destination, zones) are required.")
    try:
        zones = int(zones_str)
    except ValueError:
        return (f"Error: zones must be an integer, got '{zones_str}'.")
    base_fare = 2.50 + (zones * 0.75)
    return f"Route {orig.upper()}->{dest.upper()}: {zones} Zones, Fare ${base_fare:.2f}"


def lookup_concession_discount(category_name):
    """Return the fare multiplier for a concession category.

    Defensive: returns 0.0 (no discount) for unknown or invalid categories
    instead of raising KeyError/AttributeError.
    """
    if category_name is None or not isinstance(category_name, str):
        return 0.0
    category = category_name.strip().upper()
    if not category:
        return 0.0
    discounts = {
        "STANDARD": 1.00,
        "STUDENT": 0.50,
        "SENIOR": 0.35,
        "MILITARY": 0.20,
        "CHILD": 0.00
    }
    return discounts.get(category, 0.0)


def compute_passenger_density(occupancy_ratio_str):
    """Compute passengers per km from a 'passengers/km' string.

    Defensive: returns 0.0 for invalid input or zero distance instead of
    raising ValueError/ZeroDivisionError.
    """
    if occupancy_ratio_str is None or not isinstance(occupancy_ratio_str, str):
        return 0.0
    occupancy_ratio_str = occupancy_ratio_str.strip()
    if not occupancy_ratio_str:
        return 0.0
    parts = occupancy_ratio_str.split('/')
    if len(parts) != 2:
        return 0.0
    try:
        passengers = float(parts[0])
        km = float(parts[1])
    except ValueError:
        return 0.0
    if km == 0:
        return 0.0
    density = passengers / km
    return round(density, 2)


def main():
    print("==== Running parse_transit_corridor ====")
    c_input = input("Enter corridor (e.g. DT-UP-3): ")
    print(parse_transit_corridor(c_input))

    print("\n==== Running lookup_concession_discount ====")
    cat_input = input("Enter concession category (e.g. STUDENT, SENIOR): ")
    print("Multiplier:", lookup_concession_discount(cat_input))

    print("\n==== Running compute_passenger_density ====")
    d_input = input("Enter passengers/km (e.g. 50/10.0): ")
    print("Density:", compute_passenger_density(d_input))


if __name__ == "__main__":
    main()
