"""Spin a kubernetes cluster locallly

Cluster available at http://localhost:6443
"""

from typing import Annotated
import dagger
from dagger import Doc, dag, function, object_type


@object_type
class Kubernetes:
    """Module to spin a local single node k3s kubernetes cluster for local development and testing"""

    name: Annotated[
        str, Doc('Name of for the single node cluster (defaults to "test")')
    ] = "test"

    @function
    def service(self) -> dagger.Service:
        """Returns the single node cluster as a service"""
        k3s_container = dag.k3_s(self.name).container()
        k3s_container = k3s_container.with_mounted_cache(
            "/var/lib/dagger", dag.cache_volume("varlibdagger")
        )
        server = dag.k3_s("test").with_container(k3s_container).server()
        return server

    @function
    def get_config(self) -> dagger.File:
        """Returns the kubeconfig"""
        return dag.k3_s(self.name).config(local=False)

    @function
    async def kns_server(self) -> dagger.Container:
        """Returns k9s as a container that can be opened to see the pods running"""
        await self.service().start()
        return dag.k3_s(self.name).kns().terminal()
