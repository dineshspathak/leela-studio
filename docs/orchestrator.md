# LEELA Studio Orchestrator Architecture

The Generation Orchestrator automates the execution of compiled plans, orchestrating parallel worker pools and resilient pipeline components.

## 🏗️ Architecture

```mermaid
graph TD
    Engine["OrchestratorEngine (engine.py)"]
    Queue["OrchestratorQueue (queue.py)"]
    Worker["OrchestratorWorker (worker.py)"]
    Executor["OrchestratorExecutor (executor.py)"]
    Monitor["Dashboard API (monitor.py)"]
    Budget["BudgetManager (budget/manager.py)"]
    Cache["AssetRegistry (cache.py)"]

    Engine --> Queue
    Engine --> Budget
    Engine --> Monitor
    Engine --> Worker
    Worker --> Queue
    Worker --> Executor
    Worker --> Cache
```

---

## 🏃 Sequence Diagram

```mermaid
sequenceDiagram
    participant Pipeline as OrchestratorEngine
    participant Queue as OrchestratorQueue
    participant Worker as Worker Pool
    participant Executor as OrchestratorExecutor
    participant API as PixVerse API

    Pipeline->>Queue: Load ExecutionPlan.json
    Pipeline->>Worker: Spawn worker tasks
    Worker->>Queue: Fetch READY job
    Queue-->>Worker: Job payload
    Worker->>Executor: Execute job
    Executor->>API: POST /video/generate
    API-->>Executor: video_id
    loop Poll status
        Executor->>API: GET /video/result/{id}
        API-->>Executor: status
    end
    Executor->>API: Stream download media
    Executor-->>Worker: download local Path
    Worker->>Queue: Update job to SUCCESS
```
