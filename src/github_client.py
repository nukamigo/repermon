import requests
from src.utils.logger import setup_logger

GITHUB_API_URL = "https://api.github.com/graphql"
logger = setup_logger(__name__)


class GitHubClientError(Exception):
    pass


def get_last_workflow_runs(repo_name: str, token: str):
    try:
        owner, name = repo_name.split("/", 1)
    except ValueError as exc:
        logger.error("Repository name must be in the format 'owner/name'.")
        raise GitHubClientError(
            "Repository name must be in the format 'owner/name'."
        ) from exc

    if not token:
        logger.error("GitHub API token must be provided.")
        raise GitHubClientError("GitHub API token must be provided.")

    headers = {"Authorization": f"Bearer {token}"}

    query = """
    query GetWorkflowRuns($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        name
        owner {
          login
        }
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 50) {
                nodes {
                  checkSuites(first: 20) {
                    nodes {
                      workflowRun {
                        id
                        databaseId
                        event
                        workflow {
                          name
                        }
                        createdAt
                        updatedAt
                        url
                        checkSuite {
                          conclusion
                          status
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

    default_branch = repository.get("defaultBranchRef", {})
    target = default_branch.get("target", {})
    history = target.get("history", {})
    commits = history.get("nodes", [])

    workflow_runs = []
    seen_ids = set()

    for commit in commits:
        check_suites = commit.get("checkSuites", {}).get("nodes", [])
        for suite in check_suites:
            workflow_run = suite.get("workflowRun")
            if workflow_run and workflow_run.get("id") not in seen_ids:
                seen_ids.add(workflow_run.get("id"))
                workflow_runs.append(workflow_run)

                if len(workflow_runs) >= 10:
                    break

        if len(workflow_runs) >= 10:
            break

    workflow_runs.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    workflow_runs = workflow_runs[:10]

    logger.info(f"Found {len(workflow_runs)} workflow runs.")
    return workflow_runs
