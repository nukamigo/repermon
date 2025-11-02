import kopf
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@kopf.on.create("myresources")
def create_fn(spec, **kwargs):
    name = spec.get("name", "default-name")
    namespace = kwargs.get("namespace", "default-namespace")
    logger.info(f"A new MyResource was created: {name} in namespace {namespace}")
    return {"message": "MyResource creation logged successfully"}
