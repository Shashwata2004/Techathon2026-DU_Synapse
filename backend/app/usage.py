from datetime import datetime


def calculate_incremental_kwh(current_watts: int, previous_time: datetime, current_time: datetime) -> float:
    elapsed_hours = max((current_time - previous_time).total_seconds(), 0) / 3600
    return (current_watts * elapsed_hours) / 1000
