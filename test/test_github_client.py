import pytest
from src.github_client import GitHubClientError, WorkflowRuns
from test.data import test_github_client_data


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

        assert "owner/name" in str(exc.value)
