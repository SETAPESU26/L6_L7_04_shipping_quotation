import pytest

from shipping_quote import (
    process_shipments,
    monitor_container_pressures
)


def test_invalid_shipments():
    with pytest.raises(ValueError):
        process_shipments("invalid", 20.0)


def test_negative_handling_fee():
    with pytest.raises(ValueError):
        process_shipments([], -5.0)


def test_unapproved_shipment():
    result = process_shipments(
        [{"manifest_approved": False}],
        20.0
    )
    assert result["status"] == "NO_CARGO"


def test_air_shipment():
    shipments = [{
        "manifest_approved": True,
        "mode": "air",
        "packages": [{"weight_kg": 10}]
    }]
    result = process_shipments(shipments, 20.0)
    assert result["total_quote"] == 140.0
    assert result["status"] == "CLEARED"


def test_unknown_transport_mode():
    shipments = [{
        "manifest_approved": True,
        "mode": "sea",
        "packages": []
    }]
    result = process_shipments(shipments, 20.0)
    assert result["status"] == "NO_CARGO"


def test_zero_or_negative_weight():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [
            {"weight_kg": 0},
            {"weight_kg": -5}
        ]
    }]
    result = process_shipments(shipments, 20.0)
    assert result["status"] == "CLEARED"


def test_hazmat_non_fragile():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "is_fragile": False,
        "packages": [{"weight_kg": 5, "is_hazmat": True}]
    }]
    result = process_shipments(shipments, 20.0)
    assert result["total_quote"] == 70.0


def test_hazmat_fragile():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "is_fragile": True,
        "packages": [{"weight_kg": 5, "is_hazmat": True}]
    }]
    result = process_shipments(shipments, 20.0)
    assert result["total_quote"] == 0.0
    assert result["status"] == "NO_CARGO"


def test_heavy_package():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [{"weight_kg": 40}]
    }]
    result = process_shipments(shipments, 20.0)
    assert result["total_quote"] == 260.0


def test_express_priority():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "express_priority": True,
        "packages": [{"weight_kg": 10}]
    }]
    result = process_shipments(shipments, 20.0)
    assert result["total_quote"] == 75.0


def test_flagged_review():
    shipments = [{
        "manifest_approved": True,
        "mode": "ground",
        "packages": [
            {"weight_kg": 0},
            {"weight_kg": 0},
            {"weight_kg": 0},
            {"weight_kg": 0}
        ]
    }]
    result = process_shipments(shipments, 20.0)
    assert result["status"] == "FLAGGED_REVIEW"


def test_empty_pressure_logs():
    assert monitor_container_pressures([]) == "NO_DATA"


def test_leak_detected():
    assert monitor_container_pressures([[15.0, 13.0, 12.0]]) == "LEAK_DETECTED"


def test_stable_pressure():
    assert monitor_container_pressures([[15.0, 13.0, 14.5, 13.5]]) == "STABLE"