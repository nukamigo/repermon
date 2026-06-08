import dagger
from dagger import dag, function, object_type


@object_type
class BuildContainer:
    """^Dagger module for building the container"""

    @function
    def build_container(self, image: str, source: dagger.Directory) -> dagger.Container:
        """Builds the container for the source directory"""
        return (
            dag.container()
            .from_(image)
            .with_mounted_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["apk", "update"])
            .with_exec(["uv", "sync", "--project", "repermon"])
        )


@object_type
class Ci(BuildContainer):
    """^Dagger module for CI checks"""

    def __init__(self, source: dagger.Directory) -> None:
        self.source = source

    @function
    async def pch(self) -> str:
        """Runs pre-commit for a given source (git or local)"""
        return await (
            self.build_container("ghcr.io/astral-sh/uv:python3.12-alpine", self.source)
            .with_exec(["apk", "add", "--no-cache", "git"])
            .with_exec(["uv", "run", "pre-commit", "run", "--all-files"])
            .stdout()
        )

    # @function
    # async def pch(self) -> str:
    #     """Runs pre-commit for a given source (git or local)"""
    #     return await (
    #         dag.container()
    #         .from_("ghcr.io/astral-sh/uv:python3.12-alpine")
    #         .with_mounted_directory("/app", self.source)
    #         .with_workdir("/app")
    #         .with_exec(["sh", "-c", "apk update && apk add git"])
    #         .with_exec(["sh", "-c", "uv sync --project repermon"])
    #         .with_exec(["sh", "-c", "source .venv/bin/activate"])
    #         .with_exec(["sh", "-c", ".venv/bin/pre-commit run --all-files"])
    #         .stdout()
    #     )


# class Builder:
#     """^Dagger module for building the container"""

#     @function
#     def build_container(self) -> dagger.Container:
#         """Builds the container for the source directory"""
#         return (
#             dag.container()
#             .from_("ghcr.io/astral-sh/uv:python3.12-alpine")
#             .with_mounted_directory("/app", self.source)
#             .with_workdir("/app")
#             .with_exec(["sh", "-c", "apk update"])
#             .with_exec(["sh", "-c", "uv sync --project repermon"])
#             .with_exec(["sh", "-c", "source .venv/bin/activate"])
#             .with_entrypoint(["kopf", "run", "/app/src/operator.py"])
#         )
