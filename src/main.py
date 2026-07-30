import argparse
import json
import os
import sys
from src.github_client import GitHubClientError, WorkflowRuns
from src.utils.logger import setup_logger
from src.utils.utils import format_json_output

logger = setup_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Query GitHub GraphQL API for the last 10 workflow runs."
    )
    parser.add_argument(
        "repo",
        help="Repository in 'owner/name' format (e.g., 'nukamigo/repermon')",
    )
    parser.add_argument(
        "--token",
        help="GitHub API token for authentication (defaults to GITHUB_TOKEN env var)",
    )
    return parser.parse_args()


def main():
    parsed_args = parse_args()
    token = parsed_args.token or os.getenv("GITHUB_TOKEN")
    workflow_runs = WorkflowRuns(parsed_args.repo, token)

    if not token:
        logger.error(
            "GitHub token not provided. Use --token or set GITHUB_TOKEN environment variable."
        )
        raise ValueError("GitHub token not provided.")

    try:
        runs = workflow_runs.get_last_workflow_runs()
    except GitHubClientError as exc:
        logger.error(f"Error: {exc}")

    if not runs:
        print(json.dumps({"total_runs": 0, "runs": []}, indent=2))

    format_json_output(runs)


if __name__ == "__main__":
    sys.exit(main())
