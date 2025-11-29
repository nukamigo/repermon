from datetime import datetime
import json


class Utils:
    def format_json_outputself(self, runs):
        """Format workflow runs as JSON."""
        output = {"total_runs": len(runs), "runs": []}

        for run in runs:
            run_data = {
                "run_number": run.get("run_number"),
                "workflow_name": run.get("workflow_name"),
                "conclusion": run.get("conclusion"),
                "status": run.get("status"),
                "branch": run.get("branch"),
                "event": run.get("event"),
                "created_at": run.get("created_at"),
                "url": run.get("url"),
            }

            commit = run.get("commit", {})
            run_data["commit"] = {
                "sha": commit.get("sha"),
                "message": commit.get("message"),
                "author": commit.get("author"),
                "author_login": commit.get("author_login"),
                "date": commit.get("date"),
            }

            jobs = run.get("jobs", [])
            run_data["jobs"] = {
                "count": run.get("jobs_count", 0),
                "details": [
                    {
                        "name": job.get("name"),
                        "conclusion": job.get("conclusion"),
                        "status": job.get("status"),
                        "started_at": job.get("startedAt"),
                        "completed_at": job.get("completedAt"),
                        "duration": self.__format_duration(
                            job.get("startedAt"), job.get("completedAt")
                        ),
                    }
                    for job in jobs
                ],
            }

            output["runs"].append(run_data)

        print(json.dumps(output, indent=2))

    def __format_duration(self, started_at, completed_at):
        """
        Calculate duration between start and completion times.

        Args:
            started_at: ISO format timestamp string
            completed_at: ISO format timestamp string

        Returns:
            Human-readable duration string (e.g., "1m 23s", "2h 15m")
        """
        if not started_at or not completed_at:
            return "N/A"
        try:
            started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            completed = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
            duration = completed - started

            seconds = int(duration.total_seconds())
            if seconds < 60:
                return f"{seconds}s"
            minutes = seconds // 60
            if minutes < 60:
                return f"{minutes}m {seconds % 60}s"
            hours = minutes // 60
            return f"{hours}h {minutes % 60}m"
        except (ValueError, AttributeError):
            return "N/A"


utils = Utils()
format_json_output = utils.format_json_outputself
