from os import getenv

import firebase_admin
from firebase_admin import credentials, storage
from google.cloud.exceptions import GoogleCloudError
from google.cloud.storage import transfer_manager
from google.cloud.storage.transfer_manager import THREAD

from api_system.models import InterventionDocument

cred_dict = {
    "type": "service_account",
    "project_id": getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": "d3156e8d2ac57f7ba05e563567c091ef40ada86d",
    "private_key": getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n").replace('"', ""),
    "client_email": getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": "107376563543091697972",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-83jqv%40hackadisc.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com",
}

cred = credentials.Certificate(cred_dict)


firebase_admin.initialize_app(
    cred,
    options={
        "storageBucket": "hackadisc.appspot.com",
    },
)


class FirebaseService:
    def __init__(self):
        self.bucket = storage.bucket()

    def __upload_file(self, blob_name, file):
        blob = self.bucket.blob(blob_name)
        file.seek(0)
        try:
            blob.upload_from_file(file)
            return blob
        except GoogleCloudError:
            return None

    def __upload_bulk_files(self, files):
        return transfer_manager.upload_many(files, worker_type=THREAD)

    def __get_blob(self, blob_name):
        return self.bucket.get_blob(blob_name)

    # def upload_document(self, intervention_id, file_name, file):
    #     path = f'{intervention_id}/{file_name}'
    #     blob = self.__upload_file(path, file)
    #     if blob is None:
    #         return
    #     metadata = InterventionDocument(intervention_id=intervention_id, file_name=file_name, storage_id=path)
    #     metadata.save()

    def upload_document(self, intervention_id, file_name, file):
        path = f"{intervention_id}/{file_name}"
        blob = self.__upload_file(path, file)
        if blob is None:
            return
        metadata = InterventionDocument(
            intervention_id=intervention_id, name=file_name, storage_id=path
        )
        try:
            InterventionDocument.objects.get(storage_id=path)
        except InterventionDocument.DoesNotExist:
            metadata.save()
        except InterventionDocument.MultipleObjectsReturned:
            pass

    def upload_documents(self, intervention_id, files):
        metadata = list()
        for index, (file, name) in enumerate(files):
            path = f"{intervention_id}/{name}"
            blob = self.bucket.blob(path)
            metadata.append(
                InterventionDocument(
                    intervention_id=intervention_id, name=name, storage_id=path
                )
            )
            files[index] = (file, blob)
        results = self.__upload_bulk_files(files)
        for index, result in enumerate(results):
            if result is not None:
                continue
            try:
                InterventionDocument.objects.get(storage_id=metadata[index].storage_id)
            except InterventionDocument.DoesNotExist:
                metadata[index].save()
            except InterventionDocument.MultipleObjectsReturned:
                pass
            blob = files[index][1]
            blob.make_public()
        return results

    def list_documents(self, intervention_id):
        blobs_path = InterventionDocument.objects.filter(
            intervention_id=intervention_id
        )
        result = list()
        for blob_meta in blobs_path:
            blob = self.__get_blob(blob_meta.storage_id)
            result.append({"name": blob_meta.name, "url": blob.public_url})
        return result
