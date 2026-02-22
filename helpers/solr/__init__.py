import os
import pysolr

SOLR_URL = os.getenv("SOLR_URL", "http://localhost:8983/solr/key-control-core")

solr_client = pysolr.Solr(
    SOLR_URL,
    always_commit=True,
    timeout=10
)