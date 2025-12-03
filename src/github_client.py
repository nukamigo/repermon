from typing import List
import requests
from src.utils.logger import setup_logger

GITHUB_API_URL = "https://api.github.com/graphql"
logger = setup_logger(__name__)


class GitHubClientError(Exception):
    pass


class WorkflowRuns:
    def __init__(self, repo_name: str, token: str) -> None:
        self.repo_name = repo_name
        self.token = token

    def get_last_workflow_runs(self) -> List[str]:
        try:
            owner, name = self.repo_name.split("/", 1)
        except ValueError as exc:
            logger.error("Repository name must be in the format 'owner/name'.")
            raise GitHubClientError(
                "Repository name must be in the format 'owner/name'."
            ) from exc

        if not self.token:
            logger.error("GitHub API token must be provided.")
            raise GitHubClientError("GitHub API token must be provided.")

        headers = {"Authorization": f"Bearer {self.token}"}

        query = """
        query GetWorkflowRuns($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            name
            owner {
            login
            }
            refs(refPrefix: "refs/heads/", first: 100) {
            nodes {
                name
                target {
                ... on Commit {
                    history(first: 10) {
                    nodes {
                        oid
                        messageHeadline
                        author {
                        name
                        user {
                            login
                        }
                        }
                        committedDate
                        checkSuites(first: 20) {
                        nodes {
                            id
                            conclusion
                            status
                            workflowRun {
                            id
                            databaseId
                            runNumber
                            event
                            workflow {
                                name
                            }
                            createdAt
                            url
                            }
                            checkRuns(first: 10) {
                            totalCount
                            nodes {
                                name
                                conclusion
                                status
                                startedAt
                                completedAt
                            }
                            }
                        }
                        }
                    }
                    }
                }
                }
            }
            }
        }
        }
        """
        variables = {"owner": owner, "name": name}

        try:
            response = requests.post(
                GITHUB_API_URL,
                json={"query": query, "variables": variables},
                headers=headers,
                timeout=15,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error(f"Request error: {exc}")
            raise GitHubClientError(f"Request error: {exc}") from exc

        data = response.json()
        if "errors" in data:
            logger.error(f"GraphQL API request error: {data['errors']}")
            raise GitHubClientError(f"GraphQL API request error: {data['errors']}")

        repository = data.get("data", {}).get("repository")
        if repository is None:
            logger.error("Repository not available")
            raise GitHubClientError("Repository not available")

        refs = repository.get("refs", {}).get("nodes", [])

        workflow_runs = []
        seen_ids = set()

        for ref in refs:
            branch_name = ref.get("name")
            target = ref.get("target", {})
            history = target.get("history", {})
            commits = history.get("nodes", [])

            for commit in commits:
                commit_info = {
                    "sha": commit.get("oid"),
                    "message": commit.get("messageHeadline"),
                    "author": commit.get("author", {}).get("name"),
                    "author_login": (commit.get("author", {}).get("user") or {}).get(
                        "login"
                    ),
                    "date": commit.get("committedDate"),
                }

                check_suites = commit.get("checkSuites", {}).get("nodes", [])
                for suite in check_suites:
                    workflow_run = suite.get("workflowRun")
                    if workflow_run and workflow_run.get("id") not in seen_ids:
                        seen_ids.add(workflow_run.get("id"))

                        simplified_run = {
                            "id": workflow_run.get("id"),
                            "run_number": workflow_run.get("runNumber"),
                            "workflow_name": (workflow_run.get("workflow") or {}).get(
                                "name"
                            ),
                            "event": workflow_run.get("event"),
                            "conclusion": suite.get("conclusion"),
                            "status": suite.get("status"),
                            "created_at": workflow_run.get("createdAt"),
                            "url": workflow_run.get("url"),
                            "branch": branch_name,
                            "commit": commit_info,
                            "jobs": suite.get("checkRuns", {}).get("nodes", []),
                            "jobs_count": suite.get("checkRuns", {}).get(
                                "totalCount", 0
                            ),
                        }

                        workflow_runs.append(simplified_run)

                        if len(workflow_runs) >= 10:
                            break

                if len(workflow_runs) >= 10:
                    break

            if len(workflow_runs) >= 10:
                break

        workflow_runs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        workflow_runs = workflow_runs[:10]

        return workflow_runs
