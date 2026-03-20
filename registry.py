from biometric_normalizer.adapters.base import BaseAdapter

class AdapterRegistry:
    """
    Dynamic adapter registration.
    Community contributors register here — agent core never changes.
    """
    def __init__(self):
        self._registry: dict[str, BaseAdapter] = {}

    def register(self, adapter: BaseAdapter) -> None:
        self._registry[adapter.source_device] = adapter
        
    def get(self, source_device: str) -> BaseAdapter:
        if source_device not in self._registry:
            raise ValueError(
                f"No adapter registered for '{source_device}'. "
                f"Available: {list(self._registry.keys())}"
            )
        return self._registry[source_device]

    def available(self) -> list[str]:
        return list(self._registry.keys())


# Default registry with built-in adapters
def build_default_registry() -> AdapterRegistry:
    from biometric_normalizer.adapters.oura import OuraAdapter
    from biometric_normalizer.adapters.apple_health import AppleHealthAdapter
    from biometric_normalizer.adapters.manual import ManualAdapter

    registry = AdapterRegistry()
    for adapter in [OuraAdapter(), AppleHealthAdapter(), ManualAdapter()]:
        registry.register(adapter)
    return registry
