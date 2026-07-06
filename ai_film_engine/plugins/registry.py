class PluginRegistry:
    def __init__(self):
        self._providers: dict[str, type] = {}
        self._effects: dict[str, type] = {}
        self._transitions: dict[str, type] = {}
        self._voice_engines: dict[str, type] = {}

    def register_provider(self, name: str, cls: type):
        self._providers[name] = cls

    def register_effect(self, name: str, cls: type):
        self._effects[name] = cls

    def register_transition(self, name: str, cls: type):
        self._transitions[name] = cls

    def get_provider(self, name: str) -> type | None:
        return self._providers.get(name)

    def get_effect(self, name: str) -> type | None:
        return self._effects.get(name)

    def get_transition(self, name: str) -> type | None:
        return self._transitions.get(name)


# Global registry instance
plugin_registry = PluginRegistry()
