import logging

#DEBUG=True
DEBUG=False

logging.basicConfig(
    level=logging.INFO if DEBUG else logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("rag-api")
