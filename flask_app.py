from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient
import tempfile
import requests
import os

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        data = request.get_json()
        filename = data.get('filename')
        if not filename:
            return jsonify({'error': 'Missing filename'}), 400

        # Azure Blob Storage setup
        connect_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        container_name = "recordings"
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

        # Download file to temp
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_file.write(blob_client.download_blob().readall())
        temp_file.close()

        # Whisper API call
        openai_key = os.environ.get("OPENAI_API_KEY")
        headers = {
            "Authorization": f"Bearer {openai_key}"
        }
        files = {
            "file": (filename, open(temp_file.name, "rb"), "audio/mpeg")
        }
        data = {
            "model": "whisper-1"
        }

        response = requests.post("https://api.openai.com/v1/audio/transcriptions",
                                 headers=headers, files=files, data=data)

        os.unlink(temp_file.name)

        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500
