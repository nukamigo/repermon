from typing import Any, List

from gql import Client
from gql.transport.requests import RequestsHTTPTransport

from src.utils.graphql.loader import load_query
from src.utils.logger import setup_logger

GITHUB_API_URL = "https://api.github.com/graphql"
logger = setup_logger(__name__)


class GitHubClientError(Exception):
    pass


class WorkflowRuns:
    def __init__(self, repo_name: str, token: str) -> None:
        self.repo_name = repo_name
        self.token = token

    def get_last_workflow_runs(self) -> List[dict[str, Any]]:
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
        variable_values = {"owner": owner, "name": name}
        query_path = "queries/get_workflow_runs.graphql"

        data = self.__fetch_data(
            query_path=query_path, headers=headers, variable_values=variable_values
        )

        if "errors" in data:
            logger.error(f"GraphQL API request error: {data['errors']}")
            raise GitHubClientError(f"GraphQL API request error: {data['errors']}")

        return self.__process_data(data)

    def __fetch_data(
        self, query_path: str, headers: dict[str, str], variable_values: dict[str, str]
    ) -> dict[str, Any]:
        query = load_query(query_path)
        query.variable_values = variable_values

        _transport = RequestsHTTPTransport(
            url=GITHUB_API_URL,
            headers=headers,
            use_json=True,
        )
        client = Client(
            transport=_transport,
            fetch_schema_from_transport=True,
        )

        with client as session:
            assert client.schema is not None

            return session.execute(query)

    def __process_data(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        repository = data.get("repository")
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

        workflow_runs.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return workflow_runs
