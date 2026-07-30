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

GRAPHQL_SUCCESS_EMPTY_RUN = {
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
                                        "checkSuites": {"nodes": []},
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
