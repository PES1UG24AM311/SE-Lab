"""Expanded tests targeting line/code coverage for bus_transit_fare.py."""
import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


def manifest(route_type="local", commuters=None, **kwargs):
    item = {"route_active": True, "route_type": route_type, "commuters": commuters or []}
    item.update(kwargs)
    return item


def test_regular_local_ride():
    result = process_commute_manifest([manifest(commuters=[{"zones": 2, "type": "regular"}])], 2.0)
    assert result == {"total_fare": 4.5, "status": "COMPLETED"}


def test_invalid_manifests_type_raises():
    with pytest.raises(ValueError):
        process_commute_manifest((manifest(),), 1.0)


def test_negative_booking_fee_raises():
    with pytest.raises(ValueError):
        process_commute_manifest([], -0.01)


def test_inactive_route_is_skipped():
    result = process_commute_manifest([{"route_active": False, "route_type": "express", "commuters": [{"zones": 2}]}], 2.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_route_type_defaults_to_local_and_commuters_to_empty():
    result = process_commute_manifest([{"route_active": True}], 0.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_express_regular_passenger_and_priority_fee():
    result = process_commute_manifest([manifest("express", [{"zones": 2}], priority_boarding=True)], 3.0)
    assert result == {"total_fare": 11.0, "status": "COMPLETED"}


def test_shuttle_student_concession():
    result = process_commute_manifest([manifest("shuttle", [{"zones": 2, "type": "student"}])], 0.0)
    assert result == {"total_fare": 2.5, "status": "COMPLETED"}


def test_local_senior_concession():
    result = process_commute_manifest([manifest("local", [{"zones": 2, "type": "senior"}])], 0.0)
    assert result == {"total_fare": 2.45, "status": "COMPLETED"}


def test_unknown_route_is_rejected():
    result = process_commute_manifest([manifest("night_bus", [{"zones": 2}])], 0.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_nonpositive_zones_rejected_but_valid_commuter_still_charged():
    result = process_commute_manifest([manifest(commuters=[{"zones": 0}, {"zones": -1}, {"zones": 1}])], 0.0)
    assert result == {"total_fare": 3.5, "status": "COMPLETED"}


def test_blacklisted_card_on_local_route_does_not_add_fare():
    result = process_commute_manifest([manifest(commuters=[{"zones": 2, "blacklisted": True}])], 0.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_blacklisted_card_on_express_route_resets_manifest_fare_and_stops_loop():
    result = process_commute_manifest([manifest("express", [
        {"zones": 2}, {"zones": 1, "blacklisted": True}, {"zones": 3}
    ])], 0.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_audit_rejected_after_more_than_four_rejections():
    manifests = [manifest("bad_route") for _ in range(5)]
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 0.0, "status": "AUDIT_REJECTED"}


def test_empty_manifest_list_returns_zero_ridership():
    assert process_commute_manifest([], 0.0) == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_no_turnstile_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


def test_turnstile_operational_after_single_failure_and_reset():
    assert inspect_smartcard_turnstiles([[4, 1, 5], [0, 2]]) == "OPERATIONAL"


def test_turnstile_jam_after_two_consecutive_high_failure_readings():
    assert inspect_smartcard_turnstiles([[4, 5]]) == "TURNSTILE_JAM"
