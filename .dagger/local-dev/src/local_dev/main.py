import dagger
from dagger import dag, function, object_type


@object_type
class LocalDev:
    @function
    def local_dev(self) -> dagger.Service:
        elasticsearch_service = (
            dag.container()
            .from_("docker.elastic.co/elasticsearch/elasticsearch:9.1.1")
            .with_exposed_port(9200)
            .as_service()
        )
        kibana_service = (
            dag.container().from_("docker.elastic.co/kibana/kibana:9.1.0").with_exposed_port(5601).as_service()
        )
        return (
            dag.proxy()
            .with_service(elasticsearch_service, "elasticsearch service", 9200, 9200)
            .with_service(kibana_service, "kibana service", 5601, 5601)
            .service()
        )
