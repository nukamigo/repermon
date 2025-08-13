import dagger
from dagger import dag, function, object_type


@object_type
class Kubernetes:

    @function
    def server(self) -> dagger.Container:
        return dag.k3s("test")

    @function
    def kns_server(self) -> dagger.Container:
        return self.server().kns()
