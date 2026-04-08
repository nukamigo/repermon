from pathlib import Path
from gql import gql

GRAPHQL_DIR = Path(__file__).parent


def load_query(relative_path: str):
    return gql((GRAPHQL_DIR / relative_path).read_text())
