import pytest

from scripts.raw_to_gold_parquet import VacuumLogic


def test_vacuum_logic_valid():
    logic = VacuumLogic()
    # vendor_id, pickup, dropoff, passenger_count, trip_distance, fare_amount
    element = ["1", "2023-01-01 00:00:00", "2023-01-01 00:10:00", "1", "2.5", "10.0"]
    results = list(logic.process(element))
    assert len(results) == 1
    assert results[0]["vendor_id"] == 1
    assert results[0]["trip_distance"] == 2.5
    assert results[0]["fare_amount"] == 10.0


def test_vacuum_logic_invalid_distance():
    logic = VacuumLogic()
    element = ["1", "2023-01-01 00:00:00", "2023-01-01 00:10:00", "1", "0.0", "10.0"]
    results = list(logic.process(element))
    assert len(results) == 0


def test_vacuum_logic_invalid_fare():
    logic = VacuumLogic()
    element = ["1", "2023-01-01 00:00:00", "2023-01-01 00:10:00", "1", "2.5", "2.0"]
    results = list(logic.process(element))
    assert len(results) == 0


def test_vacuum_logic_outlier():
    logic = VacuumLogic()
    element = ["1", "2023-01-01 00:00:00", "2023-01-01 00:10:00", "1", "101.0", "10.0"]
    results = list(logic.process(element))
    assert len(results) == 0


def test_vacuum_logic_error_handling():
    logic = VacuumLogic()
    # Missing columns or bad data types
    element = ["bad", "data"]
    results = list(logic.process(element))
    assert len(results) == 0


def test_vacuum_logic_null_check():
    logic = VacuumLogic()
    # element[0] is vendor_id, must not be empty
    element = ["", "2023-01-01 00:00:00", "2023-01-01 00:10:00", "1", "2.5", "10.0"]
    results = list(logic.process(element))
    assert len(results) == 0


def test_vacuum_logic_null_check_datetime():
    logic = VacuumLogic()
    # element[1] is pickup_datetime, must not be empty
    element = ["1", "", "2023-01-01 00:10:00", "1", "2.5", "10.0"]
    results = list(logic.process(element))
    assert len(results) == 0
