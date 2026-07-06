from orchestrator.queue import OrchestratorQueue


def main():
    queue = OrchestratorQueue()
    if queue.load_checkpoint():
        total = len(queue.jobs)
        completed = sum(1 for j in queue.jobs.values() if j["status"] == "SUCCESS")
        running = sum(1 for j in queue.jobs.values() if j["status"] == "RUNNING")
        failed = sum(1 for j in queue.jobs.values() if j["status"] == "FAILED")
        waiting = sum(1 for j in queue.jobs.values() if j["status"] == "WAITING")

        print("Active Queue Status:")
        print(f"  Total Jobs: {total}")
        print(f"  Completed:  {completed}")
        print(f"  Running:    {running}")
        print(f"  Failed:     {failed}")
        print(f"  Waiting:    {waiting}")
    else:
        print("No active queue checkpoint found. Status is idle.")


if __name__ == "__main__":
    main()
