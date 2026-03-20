from biometric_normalizer.schema import BiometricSnapshot, MaternalPhase
from biometric_normalizer.calibration import apply_pregnancy_calibration
from biometric_normalizer.registry import AdapterRegistry
import logging

logger = logging.getLogger(__name__)

class BiometricNormalizer:
    def __init__(self, registry: AdapterRegistry):
        self.registry = registry

    async def ingest(
        self,
        source_device: str,
        access_token: str,
        start_date: str,
        end_date: str,
        phase: MaternalPhase | None = None,
        gestational_week: int | None = None,
        postpartum_week: int | None = None,
        apply_calibration: bool = True,
    ) -> list[BiometricSnapshot]:
        adapter = self.registry.get(source_device)
        raw_records = await adapter.fetch(access_token, start_date, end_date)

        snapshots = []
        for raw in raw_records:
            try:
                snap = adapter.transform(
                    raw,
                    phase=phase,
                    gestational_week=gestational_week,
                    postpartum_week=postpartum_week,
                )
                if apply_calibration and phase in ("pregnant", "postpartum"):
                    snap = apply_pregnancy_calibration(snap)
                snapshots.append(snap)
            except Exception as e:
                logger.warning(
                    f"[{source_device}] transform failed for record: {e}",
                    exc_info=True,
                )
                continue  # never crash on bad device data

        return snapshots
