import dagger
from dagger import dag, function, object_type


@object_type
class LocalDev:
    @function
    def local_dev(
        self,
    ) -> dagger.Service:
        """Spin containers running elasticsearch and kibana

        Elasticsearch available at http://localhost:9200
        Kibana available at http://localhost:5601
        """
        elasticsearch_service = (
            dag.container()
            .from_("docker.elastic.co/elasticsearch/elasticsearch:9.1.1")
            .with_env_variable("discovery.type", "single-node")
            .with_env_variable("xpack.security.enabled", "false")
            .with_env_variable("ES_JAVA_OPTS", "-Xmx2g -Xms2g")
            .with_exposed_port(9200)
            .as_service()
        )
        elasticsearch_service
        kibana_service = (
            dag.container()
            .from_("docker.elastic.co/kibana/kibana:9.1.0")
            .with_exposed_port(5601)
            .with_service_binding("elasticsearch_service", elasticsearch_service)
            .with_env_variable(
                "ELASTICSEARCH_HOSTS", "http://elasticsearch_service:9200"
            )
            .as_service()
        )
        return (
            dag.proxy()
            .with_service(kibana_service, "kibana_service", 5601, 5601)
            .with_service(elasticsearch_service, "elasticsearch_service", 9200, 9200)
            .service()
        )
