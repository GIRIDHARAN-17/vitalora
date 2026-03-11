from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Thresholds:
    low_max: float
    medium_max: float
    high_max: float
    critical_min: float


BASE_THRESHOLDS = Thresholds(low_max=3, medium_max=5, high_max=7, critical_min=8)


def critical_threshold_from_severity(severity_score: float) -> float:
    """
    Convert outbreak severity (0..1) to a more sensitive critical threshold.
    - severity > 0.7 => critical at >= 6
    - severity > 0.5 => critical at >= 7
    - else => critical at >= 8
    """
    if severity_score > 0.7:
        return 6.0
    if severity_score > 0.5:
        return 7.0
    return 8.0


def adjusted_thresholds(severity_score: float) -> Thresholds:
    critical_min = critical_threshold_from_severity(severity_score)
    shift = BASE_THRESHOLDS.critical_min - critical_min  # 0..2

    # shift all bands down together (more sensitive) while keeping ordering
    return Thresholds(
        low_max=max(0.0, BASE_THRESHOLDS.low_max - shift),
        medium_max=max(0.0, BASE_THRESHOLDS.medium_max - shift),
        high_max=max(0.0, BASE_THRESHOLDS.high_max - shift),
        critical_min=critical_min,
    )


def compute_alert_level(score: float, thresholds: Thresholds) -> str:
    if score >= thresholds.critical_min:
        return "critical"
    if score > thresholds.high_max:
        return "high"
    if score > thresholds.medium_max:
        return "medium"
    return "low"


def compute_adjusted_score(news_score: float, severity_score: float) -> float:
    """
    Increase the risk score when outbreak severity is high.
    We derive a shift based on the critical threshold reduction (0..2).
    """
    t = adjusted_thresholds(severity_score)
    shift = BASE_THRESHOLDS.critical_min - t.critical_min
    return float(min(10.0, max(0.0, news_score + shift)))

