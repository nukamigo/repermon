import pytest
from src.github_client import GitHubClientError, WorkflowRuns
from test.data.test_github_client_data import (
    VALID_REPO,
    VALID_TOKEN,
    GRAPHQL_SUCCESS_SINGLE_RUN,
    GRAPHQL_SUCCESS_EMPTY_RUN,
)
from unittest.mock import MagicMock, patch
from requests.exceptions import RequestException


@pytest.fixture
def valid_repo():
    return VALID_REPO


@pytest.fixture
def valid_token():
    return VALID_TOKEN


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
    def test_get_gets_successful_workflow_runs(
        self,
        mock_post,
        workflow_client,
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = GRAPHQL_SUCCESS_SINGLE_RUN
        mock_post.return_value = mock_response

        actual = workflow_client.get_last_workflow_runs()

        assert len(actual) == 1
        assert actual[0]["id"] == "run-1"
        assert actual[0]["run_number"] == 42
        assert actual[0]["workflow_name"] == "CI"
        assert actual[0]["conclusion"] == "SUCCESS"
        assert actual[0]["branch"] == "main"

    @patch("src.github_client.requests.post")
    def test_get_commit_info_from_sucessful_workflow_run(
        self,
        mock_post,
        workflow_client,
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = GRAPHQL_SUCCESS_SINGLE_RUN
        mock_post.return_value = mock_response

        response = workflow_client.get_last_workflow_runs()

        actual = response[0]["commit"]

        assert actual["sha"] == "sha1"
        assert actual["message"] == "Commit 1"
        assert actual["author"] == "Alice"
        assert actual["author_login"] == "alice-login"
        assert actual["date"] == "2024-01-01T00:00:00Z"

    @patch("src.github_client.requests.post")
    def test_empty_response_from_sucessful_workflow_run(
        self, mock_post, workflow_client
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = GRAPHQL_SUCCESS_EMPTY_RUN
        mock_post.return_value = mock_response

        actual = workflow_client.get_last_workflow_runs()

        assert actual == []

    @patch("src.github_client.requests.post")
    def test_get_last_workflow_runs_request_exception(self, mock_post, workflow_client):
        """Should raise GitHubClientError on network errors."""
        mock_post.side_effect = RequestException("Network error")
        with pytest.raises(GitHubClientError) as exc_info:
            workflow_client.get_last_workflow_runs()

        assert "Request error" in str(exc_info.value)
        mock_post.assert_called_once()
