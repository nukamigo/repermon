import pytest
from src.github_client import GitHubClientError, WorkflowRuns
from test.data import test_github_client_data
from unittest.mock import patch
from requests.exceptions import RequestException


@pytest.fixture
def valid_repo():
    return test_github_client_data.VALID_REPO


@pytest.fixture
def valid_token():
    return test_github_client_data.VALID_TOKEN


@pytest.fixture
def workflow_client(valid_repo, valid_token):
    return WorkflowRuns(valid_repo, valid_token)


class TestWorkflowRun:
    def test_invalid_repo_format(self, workflow_client):
        workflow_client.repo_name = "this-is-no-good"

        with pytest.raises(GitHubClientError) as exc:
            workflow_client.get_last_workflow_runs()

        assert "Repository name must be in the format 'owner/name'." in str(exc.value)

    def test_invalid_token(self, valid_repo):
        workflow_client = WorkflowRuns(repo_name=valid_repo, token="")

        with pytest.raises(GitHubClientError) as exc:
            workflow_client.get_last_workflow_runs()

        assert "GitHub API token must be provided." in str(exc.value)

    @patch("src.github_client.requests.post")
    def test_get_last_workflow_runs_request_exception(self, mock_post, workflow_client):
        """Should raise GitHubClientError on network errors."""
        mock_post.side_effect = RequestException("Network error")
        with pytest.raises(GitHubClientError) as exc_info:
            workflow_client.get_last_workflow_runs()

        assert "Request error" in str(exc_info.value)
        mock_post.assert_called_once()
