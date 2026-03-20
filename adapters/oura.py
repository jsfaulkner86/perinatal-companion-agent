import httpx
from biometric_normalizer.schema import BiometricSnapshot, MaternalPhase
from biometric_normalizer.adapters.base import BaseAdapter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

OURA_BASE = "https://api.ouraring.com/v2/usercollection"

class OuraAdapter(BaseAdapter):
    source_device = "oura"

    async def fetch(
        self,
        access_token: str,
        start_date: str,
        end_date: str,
    ) -> list[dict]:
        headers = {"Authorization": f"Bearer {access_token}"}
        endpoints = ["sleep", "readiness", "heartrate"]
        results = {}

        async with httpx.AsyncClient() as client:
            for endpoint in endpoints:
                resp = await client.get(
                    f"{OURA_BASE}/{endpoint}",
                    headers=headers,
                    params={"start_date": start_date, "end_date": end_date},
                    timeout=10.0,
                )
                resp.raise_for_status()
                results[endpoint] = resp.json().get("data", [])

        # Merge by date
        merged = {}
        for sleep in results.get("sleep", []):
            date = sleep.get("day")
            merged[date] = {"sleep": sleep}
        for readiness in results.get("readiness", []):
            date = readiness.get("day")
            merged.setdefault(date, {})["readiness"] = readiness

        return [{"date": d, **v} for d, v in merged.items()]

    def transform(
        self,
        raw: dict,
        phase: MaternalPhase | None = None,
        gestational_week: int | None = None,
        postpartum_week: int | None = None,
    ) -> BiometricSnapshot:
        sleep = raw.get("sleep", {})
        readiness = raw.get("readiness", {})

        return BiometricSnapshot(
            timestamp=datetime.fromisoformat(raw["date"]),
            source_device="oura",
            confidence=0.88,  # Oura validated accuracy tier
            phase=phase,
            gestational_week=gestational_week,
            postpartum_week=postpartum_week,
            sleep_duration_hrs=round(
                sleep.get("total_sleep_duration", 0) / 3600, 2
            ) or None,
            sleep_efficiency_pct=sleep.get("efficiency"),
            deep_sleep_hrs=round(
                sleep.get("deep_sleep_duration", 0) / 3600, 2
            ) or None,
            rem_sleep_hrs=round(
                sleep.get("rem_sleep_duration", 0) / 3600, 2
            ) or None,
            awakenings=sleep.get("awakenings_count"),
            hrv_avg_ms=sleep.get("average_hrv"),
            resting_hr_bpm=sleep.get("lowest_heart_rate"),
            readiness_score=readiness.get("score"),
            raw_device_payload=raw,
        )
