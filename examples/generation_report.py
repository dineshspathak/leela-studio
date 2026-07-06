import json
from pathlib import Path


def main():
    print("=== READING GENERATION REPORTS AND ANALYTICS ===")

    analytics_path = Path(
        "workspace/projects/Krishna Janm/reports/production_analytics.json"
    )
    if not analytics_path.exists():
        # Fallback to general workspace locations
        analytics_path = Path(
            "workspace/projects/leela/reports/production_analytics.json"
        )

    if not analytics_path.exists():
        print("No analytics reports generated yet. Run generation first.")
        return

    with open(analytics_path, encoding="utf-8") as f:
        data = json.load(f)

    print("\n--- Analytics Summary ---")
    print(f"Asset Reuse Rate: {data.get('asset_reuse_percentage')}%")
    print(f"Credits Saved: {data.get('credits_saved')}")
    print(f"Cache Efficiency: {data.get('cache_efficiency')}")
    print(f"Average Gen Time: {data.get('average_generation_time')} seconds")


if __name__ == "__main__":
    main()
