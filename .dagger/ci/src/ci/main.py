import dagger
from dagger import dag, function, object_type


@object_type
class Ci:
    """^Dagger module for CI checks"""

    source: dagger.Directory

    @function
    async def pch(self) -> str:
        """Runs pre-commit for a given source (git or local)"""
        return await (
            dag.container()
            .from_("ghcr.io/astral-sh/uv:python3.12-alpine")
            .with_mounted_directory("/app", self.source)
            .with_workdir("/app")
            .with_exec(["sh", "-c", "apk update && apk add git"])
            .with_exec(["sh", "-c", "uv sync --project repermon --active"])
            .with_exec(["sh", "-c", "source .venv/bin/activate"])
            .with_exec(["sh", "-c", ".venv/bin/pre-commit run --all-files"])
            .stdout()
        )
