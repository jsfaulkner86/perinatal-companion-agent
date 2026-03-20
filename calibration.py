from biometric_normalizer.schema import BiometricSnapshot

# Pregnancy-stage physiological offset table
# Sources: ACOG, obstetric physiology literature
# HR increases ~10-15 bpm by T3; HRV naturally declines in T2/T3
PREGNANCY_OFFSETS = {
    "trimester_1": {"resting_hr_bpm": -3.0,  "hrv_avg_ms": +2.0},
    "trimester_2": {"resting_hr_bpm": -7.0,  "hrv_avg_ms": +5.0},
    "trimester_3": {"resting_hr_bpm": -12.0, "hrv_avg_ms": +8.0},
    "postpartum":  {"resting_hr_bpm": -5.0,  "hrv_avg_ms": +3.0},
}

def get_trimester(gestational_week: int) -> str:
    if gestational_week <= 13:
        return "trimester_1"
    elif gestational_week <= 26:
        return "trimester_2"
    return "trimester_3"

def apply_pregnancy_calibration(snapshot: BiometricSnapshot) -> BiometricSnapshot:
    """
    Apply physiological offsets to normalize wearable readings
    against pregnancy-stage baseline shifts.
    Raw values are preserved in raw_device_payload.
    """
    if snapshot.phase == "pregnant" and snapshot.gestational_week:
        stage = get_trimester(snapshot.gestational_week)
    elif snapshot.phase == "postpartum":
        stage = "postpartum"
    else:
        return snapshot  # TTC — no calibration needed

    offsets = PREGNANCY_OFFSETS[stage]
    data = snapshot.model_dump()

    if data.get("resting_hr_bpm") and offsets.get("resting_hr_bpm"):
        data["resting_hr_bpm"] = round(
            data["resting_hr_bpm"] + offsets["resting_hr_bpm"], 1
        )
    if data.get("hrv_avg_ms") and offsets.get("hrv_avg_ms"):
        data["hrv_avg_ms"] = round(
            data["hrv_avg_ms"] - offsets["hrv_avg_ms"], 1
        )

    data["pregnancy_calibrated"] = True
    return BiometricSnapshot(**data)
