from dataclasses import dataclass
from typing import Annotated
import dagger
from dagger import DefaultPath, Doc, dag, function, object_type


@dataclass
@object_type
class BuildCi:
    """^Dagger build module"""

    source: dagger.Directory

    def __init__(
        self,
        source: Annotated[
            dagger.Directory,
            DefaultPath("/"),
            Doc("The source directory to run the pre-commit"),
        ],
        commit: Annotated[
            str,
            Doc(
                "Checkout the repository (at the designated ref) and use it as the source directory instead of the local one."
            ),
        ] = "",
    ) -> None:
        if commit:
            self.source = (
                dag.git("https://github.com/nukamigo/repermon.git")
                .commit(commit)
                .tree()
            )
        else:
            self.source = source

    @function
    async def pre_commit(self) -> str:
        """Runs pre-commit for a given source (git or local)"""
        return await dag.ci(self.source).pch()

    @function
    def cluster(self) -> dagger.Service:
        """Returns a service with the created cluster"""
        return dag.kubernetes().service()

    @function
    def kns(self) -> dagger.Container:
        """Returns a k9s container with the created cluster"""
        return dag.kubernetes().kns_server()

    @function
    def get_config(self) -> dagger.File:
        """Returns the kubeconfig for the created cluster"""
        return dag.kubernetes().get_config()

    @function
    async def test_cluster(self) -> str:
        """Tests the manifests in the source directory"""
        await self.cluster().start()
        output = await self.__test_manifests()
        return output

    def __test_manifests(self) -> str:
        kubeconfig = self.get_config()
        return (
            dag.container()
            .from_("alpine/kubectl:1.34.1")
            .with_mounted_directory("/manifests", self.source.directory("kubernetes"))
            .with_mounted_file("/kubeconfig", kubeconfig)
            .with_env_variable("KUBECONFIG", "/kubeconfig")
            .with_exec(["chown", "1001:0", "/kubeconfig"])
            .with_exec(["kubectl", "apply", "-f", "/manifests"])
            .combined_output()
        )

    @function
    def build_container(self) -> dagger.Container:
        """Builds the container for the source directory"""
        return (
            dag.container()
            .from_("ghcr.io/astral-sh/uv:python3.12-alpine")
            .with_mounted_directory("/app", self.source)
            .with_workdir("/app")
            .with_exec(["sh", "-c", "apk update"])
            .with_exec(["sh", "-c", "uv sync --project repermon"])
            .with_exec(["sh", "-c", "source .venv/bin/activate"])
            .with_entrypoint(["kopf", "run", "/app/operator.py"])
        )
