from hypothesis import given, strategies as st
from processor import parse_transit_corridor, lookup_concession_discount, compute_passenger_density


@given(st.text() | st.none())
def test_parse_transit_corridor_no_crash(s):
    # Using try and except: the function must not crash for any random input.
    try:
        parse_transit_corridor(s)
    except Exception as e:
        assert False, f"parse_transit_corridor crashed with: {e}"


@given(st.text() | st.none())
def test_lookup_concession_discount_safe(s):
    # Using try and except: the function must not crash for any random input.
    try:
        lookup_concession_discount(s)
    except Exception as e:
        assert False, f"lookup_concession_discount crashed with: {e}"


@given(st.text() | st.none())
def test_compute_passenger_density_safe(s):
    # Using try and except: the function must not crash for any random input.
    try:
        compute_passenger_density(s)
    except Exception as e:
        assert False, f"compute_passenger_density crashed with: {e}"
