import argparse
import os
import sys
from src.github_client import GitHubClientError, get_last_workflow_runs
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Query GitHub GraphQL API for the last 10 workflow runs."
    )
    parser.add_argument(
        "repo", help="Repository in 'owner/name' format, example: 'nukamigo/repermon'."
    )
    parser.add_argument(
        "--token",
        help="GitHub API token for authentication (if omitted, will try GITHUB_TOKEN env var)",
    )
    return parser.parse_args()


def main():
    parsed_args = parse_args()
    token = parsed_args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("Github token not provided. Use --token or set GITHUB_TOKEN")
        return 1

    try:
        runs = get_last_workflow_runs(parsed_args.repo, token)
    except GitHubClientError as exc:
        logger.error(str(exc))
        return 1

    for run in runs:
        workflow_name = (run.get("workflow") or {}).get("name", "Unknown")
        status = run.get("status", "unknown")
        conclusion = run.get("conclusion", "none")
        created_at = run.get("createdAt", "N/A")
        url = run.get("url", "")
        logger.info(
            f"Created: {created_at} | Status: {status} | Conclusion: {conclusion} | Workflow: {workflow_name} | URL: {url}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
