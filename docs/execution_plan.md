# LEELA Studio Execution Plan & Graph Documentation

Once an episode is successfully validated, the compiler generates a provider-agnostic execution map.

---

## 📋 Execution Plan (`ExecutionPlan.json`)
The Execution Plan lists all resolved jobs flatly. Each job defines:
- **`job_id`**: Computed unique identifier (e.g. `Scene1_Shot1`).
- **`prompt`**: Final resolved text prompt after rendering Jinja templates.
- **`negative_prompt`**: Final resolved negative prompt (supporting defaults).
- **`references`**: Fully resolved local path references of assets (e.g. master images resolved via `AssetResolver`).
- **`output_path`**: Destination where the downloaded file should reside (e.g. `downloads/Episode001/Scene001/Shot001.mp4`).

---

## 🕸️ Execution Graph (`ExecutionGraph.json`)
Specifies the dependency graph (DAG) mapping relationships between jobs:
- **Nodes**: Complete list of job IDs.
- **Edges**: Paths detailing parent-child dependencies. For example, an `image_to_video` shot depends on a preceding `text_to_image` shot if they reference each other.

---

## ⏳ Scheduler & Cost Estimation
- **Scheduler**: Analyzes the dependency graph and computes a topological sort, ensuring parent tasks execute before child tasks in the processing pipeline.
- **Cost Estimator**: Aggregates all job operations and estimates expected credit consumption and pipeline runtime prior to execution.
