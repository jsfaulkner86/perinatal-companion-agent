from abc import ABC, abstractmethod
from typing import Any
from biometric_normalizer.schema import BiometricSnapshot

class BaseAdapter(ABC):
    """
    Every device adapter implements this interface.
    Community contributors add a new file in adapters/ and
    register in registry.py — nothing else changes.
    """
    source_device: str  # must match SourceDevice literal

    @abstractmethod
    async def fetch(
        self,
        access_token: str,
        start_date: str,
        end_date: str,
    ) -> list[dict[str, Any]]:
        """Pull raw data from device API. Returns raw payloads."""
        ...

    @abstractmethod
    def transform(
        self,
        raw: dict[str, Any],
        phase: str | None = None,
        gestational_week: int | None = None,
    ) -> BiometricSnapshot:
        """Map raw device payload → BiometricSnapshot."""
        ...
