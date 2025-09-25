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
    async def build(self) -> str:
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
    async def test_manifests(self) -> str:
        """Tests the manifests in the source directory"""
        await self.cluster().start()
        kubeconfig = self.get_config()
        return (
            dag.container()
            .from_("bitnami/kubectl:latest")
            .with_mounted_directory("/manifests", self.source)
            .with_mounted_file("/kubeconfig", kubeconfig)
            .with_env_variable("KUBECONFIG", "/kubeconfig")
            .with_exec(["kubectl", "apply", "-f", "/manifests"])
            .as_service()
        )
