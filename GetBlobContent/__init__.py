import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    blob_name = req.params.get('name')
    container = req.params.get('container')

    if not blob_name or not container:
        return func.HttpResponse(
            "Missing 'name' or 'container' parameter.",
            status_code=400
        )

    try:
        blob_service_client = BlobServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])
        blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)
        blob_data = blob_client.download_blob().readall()

        return func.HttpResponse(blob_data, mimetype="application/octet-stream")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            f"Error retrieving blob: {str(e)}",
            status_code=500
        )
