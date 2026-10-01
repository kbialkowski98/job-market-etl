import logging

from azure.storage.blob import BlobServiceClient

from src import config
from src.utils.logger_setup import setup_logger


setup_logger()
logger = logging.getLogger(__name__)


def upload_to_blob(file_path: str, container_name: str, blob_name: str) -> None:
    if not config.AZURE_CONNECTION_STRING:
        logger.error("Brak klucza AZURE_CONNECTION_STRING w pliku .env.")
        raise ValueError("Brak klucza AZURE_CONNECTION_STRING w pliku .env.")

    try:
        blob_service_client = BlobServiceClient.from_connection_string(config.AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        logger.info(f"Wysylanie pliku do Azure (kontener: {container_name})...")

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        logger.info(f"Plik {blob_name} wyslany pomyslnie.")

    except Exception as e:
        logger.error(f"Krytyczny blad podczas wysylania do Azure: {e}")
        # Podnosimy oryginalny wyjatek, zeby nie zgubic przyczyny.
        raise
