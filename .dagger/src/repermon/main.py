from dataclasses import dataclass
from typing import Annotated, Optional
import dagger
from dagger import DefaultPath, Doc, dag, function, object_type
from .ci import Ci
from .kubernetes import Kubernetes as kubernetes


@dataclass
@object_type
class Repermon:
    """Dagger build module"""

    source: Annotated[
        Optional[dagger.Directory],
        DefaultPath("/"),
        Doc("The source directory to run the pre-commit"),
    ]

    def __init__(
        self,
        source: Optional[dagger.Directory],
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

    def create_ci(self) -> Ci:
        return Ci(self.source)

    @function
    async def pre_commit(self) -> str:
        """Runs pre-commit for a given source (git or local)"""
        return await self.create_ci().pch()

    @function
    def cluster(self) -> dagger.Service:
        """Returns a service with the created cluster"""
        return kubernetes().service()

    @function
    def kns(self) -> dagger.Container:
        """Returns a k9s container with the created cluster"""
        return kubernetes().kns_server()

    @function
    def get_config(self) -> dagger.File:
        """Returns the kubeconfig for the created cluster"""
        return kubernetes().get_config()

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
            .with_exec(["kubectl", "apply", "-f", "/manifests/crd.yaml"])
            .with_exec(["kubectl", "apply", "-f", "/manifests/rbac.yaml"])
            .with_exec(["kubectl", "apply", "-f", "/manifests/operator.yaml"])
            .combined_output()
        )
