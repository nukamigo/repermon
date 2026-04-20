import pytest
from src.github_client import GitHubClientError, WorkflowRuns
from test.data.test_github_client_data import (
    GRAPHQL_REPOSITORY_NONE,
    GRAPHQL_SUCCESS_EMPTY_RUN,
    GRAPHQL_SUCCESS_SINGLE_RUN,
    GRAPHQL_ERRORS_RESPONSE,
    VALID_REPO,
    VALID_TOKEN,
)


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

    def test_get_gets_successful_workflow_runs(self, mocker, workflow_client):
        mocker_transport = mocker.Mock()
        mocker_transport.fetch_schema_from_transport = False

        mock_schema = mocker.Mock()
        mock_schema.types = {}

        mocker_client = mocker.Mock()
        mocker_client.schema = mock_schema
        mocker_client.__enter__ = mocker.Mock(return_value=mocker_client)
        mocker_client.__exit__ = mocker.Mock(return_value=False)
        mocker_client.execute.return_value = GRAPHQL_SUCCESS_SINGLE_RUN["data"]

        mocker.patch("src.github_client.Client", return_value=mocker_client)

        actual = workflow_client.get_last_workflow_runs()

        assert len(actual) == 1
        assert actual[0]["id"] == "run-1"
        assert actual[0]["run_number"] == 42
        assert actual[0]["workflow_name"] == "CI"
        assert actual[0]["conclusion"] == "SUCCESS"
        assert actual[0]["branch"] == "main"

    def test_get_commit_info_from_sucessful_workflow_run(self, mocker, workflow_client):
        mocker_client = mocker.Mock()
        mocker_client.schema = mocker.Mock()
        mocker_client.__enter__ = mocker.Mock(return_value=mocker_client)
        mocker_client.__exit__ = mocker.Mock(return_value=False)
        mocker_client.execute.return_value = GRAPHQL_SUCCESS_SINGLE_RUN["data"]

        mocker.patch("src.github_client.Client", return_value=mocker_client)

        response = workflow_client.get_last_workflow_runs()

        actual = response[0]["commit"]

        assert actual["sha"] == "sha1"
        assert actual["message"] == "Commit 1"
        assert actual["author"] == "Alice"
        assert actual["author_login"] == "alice-login"
        assert actual["date"] == "2024-01-01T00:00:00Z"

    def test_empty_response_from_sucessful_workflow_run(self, mocker, workflow_client):
        mocker_client = mocker.Mock()
        mocker_client.schema = mocker.Mock()
        mocker_client.__enter__ = mocker.Mock(return_value=mocker_client)
        mocker_client.__exit__ = mocker.Mock(return_value=False)
        mocker_client.execute.return_value = GRAPHQL_SUCCESS_EMPTY_RUN["data"]

        mocker.patch("src.github_client.Client", return_value=mocker_client)

        actual = workflow_client.get_last_workflow_runs()

        assert actual == []

    def test_graphql_api_error(self, mocker, workflow_client):
        mocker_client = mocker.Mock()
        mocker_client.schema = mocker.Mock()
        mocker_client.__enter__ = mocker.Mock(return_value=mocker_client)
        mocker_client.__exit__ = mocker.Mock(return_value=False)
        mocker_client.execute.return_value = GRAPHQL_ERRORS_RESPONSE

        mocker.patch("src.github_client.Client", return_value=mocker_client)

        with pytest.raises(GitHubClientError) as exc:
            workflow_client.get_last_workflow_runs()

        assert "Something went wrong" in str(exc.value)

    def test_repository_not_found(self, mocker, workflow_client):
        mocker_client = mocker.Mock()
        mocker_client.schema = mocker.Mock()
        mocker_client.__enter__ = mocker.Mock(return_value=mocker_client)
        mocker_client.__exit__ = mocker.Mock(return_value=False)
        mocker_client.execute.return_value = GRAPHQL_REPOSITORY_NONE["data"]

        mocker.patch("src.github_client.Client", return_value=mocker_client)
        with pytest.raises(GitHubClientError) as exc:
            workflow_client.get_last_workflow_runs()

        assert "Repository not available" in str(exc.value)
