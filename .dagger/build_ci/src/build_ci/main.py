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
