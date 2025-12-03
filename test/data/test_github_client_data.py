VALID_REPO = "owner/repo"
VALID_TOKEN = "token-123"

GRAPHQL_SUCCESS_SINGLE_RUN = {
    "data": {
        "repository": {
            "refs": {
                "nodes": [
                    {
                        "name": "main",
                        "target": {
                            "history": {
                                "nodes": [
                                    {
                                        "oid": "sha1",
                                        "messageHeadline": "Commit 1",
                                        "author": {
                                            "name": "Alice",
                                            "user": {"login": "alice-login"},
                                        },
                                        "committedDate": "2024-01-01T00:00:00Z",
                                        "checkSuites": {
                                            "nodes": [
                                                {
                                                    "id": "suite-1",
                                                    "conclusion": "SUCCESS",
                                                    "status": "COMPLETED",
                                                    "workflowRun": {
                                                        "id": "run-1",
                                                        "databaseId": 1,
                                                        "runNumber": 42,
                                                        "event": "push",
                                                        "workflow": {"name": "CI"},
                                                        "createdAt": "2024-01-01T01:00:00Z",
                                                        "url": "https://example.com/run-1",
                                                    },
                                                    "checkRuns": {
                                                        "totalCount": 1,
                                                        "nodes": [
                                                            {
                                                                "name": "job-1",
                                                                "conclusion": "SUCCESS",
                                                                "status": "COMPLETED",
                                                                "startedAt": "2024-01-01T01:00:00Z",
                                                                "completedAt": "2024-01-01T01:05:00Z",
                                                            }
                                                        ],
                                                    },
                                                }
                                            ]
                                        },
                                    }
                                ]
                            }
                        },
                    }
                ]
            }
        }
    }
}

GRAPHQL_ERRORS_RESPONSE = {"errors": [{"message": "Something went wrong"}]}

GRAPHQL_REPOSITORY_NONE = {"data": {"repository": None}}


def build_many_runs_payload(count: int = 15) -> dict:
    """Return a payload with `count` unique workflow runs on one branch."""
    check_suites = []
    for i in range(count):
        check_suites.append(
            {
                "id": f"suite-{i}",
                "conclusion": "SUCCESS",
                "status": "COMPLETED",
                "workflowRun": {
                    "id": f"run-{i}",
                    "databaseId": i,
                    "runNumber": i,
                    "event": "push",
                    "workflow": {"name": "CI"},
                    "createdAt": f"2024-01-01T0{i:02d}:00:00Z",
                    "url": f"https://example.com/run-{i}",
                },
                "checkRuns": {"totalCount": 1, "nodes": []},
            }
        )

    return {
        "data": {
            "repository": {
                "refs": {
                    "nodes": [
                        {
                            "name": "main",
                            "target": {
                                "history": {
                                    "nodes": [
                                        {
                                            "oid": "sha1",
                                            "messageHeadline": "Commit 1",
                                            "author": {"name": "Alice", "user": None},
                                            "committedDate": "2024-01-01T00:00:00Z",
                                            "checkSuites": {"nodes": check_suites},
                                        }
                                    ]
                                }
                            },
                        }
                    ]
                }
            }
        }
    }
