import pytest

from bus_transit_fare import (
    process_commute_manifest,
    inspect_smartcard_turnstiles,
)


# --------------------------------------------------
# 1. Input validation
# --------------------------------------------------

def test_non_list_manifests():
    with pytest.raises(ValueError):
        process_commute_manifest("invalid", 2.0)


def test_negative_booking_fee():
    with pytest.raises(ValueError):
        process_commute_manifest([], -1.0)


def test_valid_empty_manifest_list():
    result = process_commute_manifest([], 2.0)
    assert result == {
        "total_fare": 0.0,
        "status": "ZERO_RIDERSHIP",
    }


# --------------------------------------------------
# 2. Route activation and route types
# --------------------------------------------------

def test_inactive_route_is_skipped():
    result = process_commute_manifest(
        [{"route_active": False, "route_type": "local"}],
        2.0,
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_default_route_type_and_empty_commuters():
    result = process_commute_manifest(
        [{"route_active": True}],
        2.0,
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_express_route():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "express",
            "commuters": [{"zones": 2, "type": "regular"}],
        }],
        2.0,
    )
    assert result == {
        "total_fare": 8.0,
        "status": "COMPLETED",
    }


def test_shuttle_route():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "shuttle",
            "commuters": [{"zones": 2, "type": "regular"}],
        }],
        2.0,
    )
    assert result == {
        "total_fare": 6.0,
        "status": "COMPLETED",
    }


def test_local_route():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 2, "type": "regular"}],
        }],
        2.0,
    )
    assert result == {
        "total_fare": 4.5,
        "status": "COMPLETED",
    }


def test_unknown_route_type():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "metro",
            "commuters": [],
        }],
        2.0,
    )
    assert result == {
        "total_fare": 0.0,
        "status": "ZERO_RIDERSHIP",
    }


# --------------------------------------------------
# 3. Commuter validation and fare categories
# --------------------------------------------------

def test_zero_zones_rejected():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 0, "type": "regular"}],
        }],
        2.0,
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_negative_zones_rejected():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": -1, "type": "regular"}],
        }],
        2.0,
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_student_concession():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "shuttle",
            "commuters": [{"zones": 2, "type": "student"}],
        }],
        2.0,
    )
    assert result["total_fare"] == 2.5
    assert result["status"] == "COMPLETED"


def test_senior_concession():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 2, "type": "senior"}],
        }],
        2.0,
    )
    assert result["total_fare"] == 2.45
    assert result["status"] == "COMPLETED"


def test_regular_passenger_default_type():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 1}],
        }],
        2.0,
    )
    assert result["total_fare"] == 3.5
    assert result["status"] == "COMPLETED"


# --------------------------------------------------
# 4. Blacklisted cards and priority boarding
# --------------------------------------------------

def test_blacklisted_card_on_local_route():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 2, "blacklisted": True}],
        }],
        2.0,
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_blacklisted_card_on_express_route():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "express",
            "commuters": [
                {"zones": 2, "type": "regular"},
                {"zones": 1, "blacklisted": True},
                {"zones": 3, "type": "regular"},
            ],
        }],
        2.0,
    )
    assert result["total_fare"] == 0.0
    assert result["status"] == "ZERO_RIDERSHIP"


def test_priority_boarding_fee_applied():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "priority_boarding": True,
            "commuters": [{"zones": 2, "type": "regular"}],
        }],
        2.0,
    )
    assert result["total_fare"] == 6.5
    assert result["status"] == "COMPLETED"


def test_priority_boarding_fee_not_applied():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "priority_boarding": False,
            "commuters": [{"zones": 2, "type": "regular"}],
        }],
        2.0,
    )
    assert result["total_fare"] == 4.5
    assert result["status"] == "COMPLETED"


# --------------------------------------------------
# 5. Audit rejection and final status
# --------------------------------------------------

def test_audit_rejected_after_five_invalid_routes():
    manifests = [
        {"route_active": True, "route_type": "unknown"}
        for _ in range(5)
    ]

    result = process_commute_manifest(manifests, 2.0)

    assert result["status"] == "AUDIT_REJECTED"


def test_four_rejections_do_not_trigger_audit():
    manifests = [
        {"route_active": True, "route_type": "unknown"}
        for _ in range(4)
    ]

    result = process_commute_manifest(manifests, 2.0)

    assert result["status"] == "ZERO_RIDERSHIP"


def test_completed_status_with_positive_fare():
    result = process_commute_manifest(
        [{
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 1, "type": "regular"}],
        }],
        2.0,
    )
    assert result["status"] == "COMPLETED"


# --------------------------------------------------
# 6. Smartcard turnstile decision branches
# --------------------------------------------------

def test_empty_turnstile_matrix():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


def test_empty_device_readings():
    assert inspect_smartcard_turnstiles([[]]) == "OPERATIONAL"


def test_turnstile_operational_with_low_failures():
    assert inspect_smartcard_turnstiles([[1, 2, 3]]) == "OPERATIONAL"


def test_single_high_failure_does_not_cause_jam():
    assert inspect_smartcard_turnstiles([[4]]) == "OPERATIONAL"


def test_failure_streak_reset_by_low_reading():
    assert inspect_smartcard_turnstiles([[4, 2, 4]]) == "OPERATIONAL"


def test_two_consecutive_high_failures_cause_jam():
    assert inspect_smartcard_turnstiles([[4, 5]]) == "TURNSTILE_JAM"


def test_high_failures_on_separate_devices():
    assert inspect_smartcard_turnstiles([[4], [5]]) == "OPERATIONAL"