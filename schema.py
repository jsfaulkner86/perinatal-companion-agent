#Biometric Normalizer Package - Full Implementation

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal

SourceDevice = Literal[
    "oura", "apple_health", "google_fit",
    "fitbit", "garmin", "clue", "flo", "manual"
]

MaternalPhase = Literal["ttc", "pregnant", "postpartum"]

class BiometricSnapshot(BaseModel):
    """Unified, device-agnostic biometric record."""
    timestamp: datetime
    source_device: SourceDevice
    confidence: float = Field(ge=0.0, le=1.0)
    phase: MaternalPhase | None = None
    gestational_week: int | None = Field(default=None, ge=1, le=42)
    postpartum_week: int | None = Field(default=None, ge=0, le=52)

    # Sleep
    sleep_duration_hrs: float | None = Field(default=None, ge=0.0, le=24.0)
    sleep_efficiency_pct: float | None = Field(default=None, ge=0.0, le=100.0)
    deep_sleep_hrs: float | None = None
    rem_sleep_hrs: float | None = None
    awakenings: int | None = None

    # Autonomic
    hrv_avg_ms: float | None = Field(default=None, ge=0.0)
    resting_hr_bpm: float | None = Field(default=None, ge=20.0, le=220.0)
    readiness_score: int | None = Field(default=None, ge=0, le=100)

    # Activity
    steps: int | None = Field(default=None, ge=0)
    active_minutes: int | None = None

    # Reproductive
    cycle_day: int | None = Field(default=None, ge=1, le=60)
    bbt_celsius: float | None = Field(default=None, ge=35.0, le=40.0)

    # Computed
    stress_proxy: float | None = Field(
        default=None, ge=0.0, le=1.0,
        description="HRV delta from personal baseline, normalized 0–1"
    )
    pregnancy_calibrated: bool = False
    raw_device_payload: dict | None = None  # original device JSON, never sent to LLM

    @field_validator("gestational_week")
    @classmethod
    def week_requires_pregnant_phase(cls, v, info):
        if v is not None and info.data.get("phase") != "pregnant":
            raise ValueError("gestational_week only valid during pregnant phase")
        return v
