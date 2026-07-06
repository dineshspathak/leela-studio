# Dynamic Provider Selection & Health Management

## 1. Provider Selection Philosophy
The filmmaker engine decouples execution plans from individual backend services. Instead of hardcoding API targets, it queries the `PluginRegistry` for available model instances.

## 2. Health Monitoring
The `ProviderHealthManager` tracks:
- Availability (healthy / unhealthy / overloaded).
- API response times and queue durations.
- Daily credit quotas and rate limit triggers.

## 3. Adaptive Scheduling
If a chosen provider goes down or experiences severe delays:
1. The `AdaptiveScheduler` detects the health change.
2. It redirects pending jobs to the cheapest healthy fallback provider.
3. Once the main provider recovers, scheduling returns to the primary target.
