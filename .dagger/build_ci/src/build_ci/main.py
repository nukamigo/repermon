from typing import Annotated
import dagger
from dagger import Doc, dag, function, object_type


@object_type
class BuildCi:
    """^Dagger build module"""

    source: dagger.Directory
    commit: str

    def __init__(
        self,
        source: Annotated[
            dagger.Directory | None,
            Doc("The source directory to run the pre-commit"),
        ] =  None,
        commit: Annotated[
            str,
            Doc("Checkout the repository (at the designated ref) and use it as the source directory instead of the local one.")
        ] = "",
    ) -> None:
        self.commit = commit
        if source is not None:
            self.source = source
        elif commit:
            self.source = dag.git("https://github.com/nukamigo/repermon.git").commit(commit).tree()

    @function
    def build(self) -> str:
        """Runs pre-commit for a given source (git or local)"""
        return dag.ci(self.source).pch()
