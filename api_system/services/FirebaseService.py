import firebase_admin
from firebase_admin import storage
from google.cloud.exceptions import GoogleCloudError
from google.cloud.storage import transfer_manager
from google.cloud.storage.transfer_manager import THREAD

from api_system.models import InterventionDocument

firebase_admin.initialize_app(options={
    'storageBucket': 'hackadisc.appspot.com'
})
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

    def upload_document(self, intervention_id, file_name, file):
        path = f'{intervention_id}/{file_name}'
        blob = self.__upload_file(path, file)
        if blob is None:
            # TODO: Handle error messages
            return
        metadata = InterventionDocument(intervention_id=intervention_id, file_name=file_name, storage_id=path)
        metadata.save()

    def upload_document(self, intervention_id, file_name, file):
        path = f'{intervention_id}/{file_name}'
        blob = self.__upload_file(path, file)
        if blob is None:
            # TODO: Handle error messages
            return
        metadata = InterventionDocument(intervention_id=intervention_id, name=file_name, storage_id=path)
        try:
            InterventionDocument.objects.get(storage_id=path)
        except InterventionDocument.DoesNotExist:
            metadata.save()
        except InterventionDocument.MultipleObjectsReturned:
            pass

    def upload_documents(self, intervention_id, files):
        metadata = list()
        for index, (file, name) in enumerate(files):
            path = f'{intervention_id}/{name}'
            blob = self.bucket.blob(path)
            metadata.append(InterventionDocument(intervention_id=intervention_id, name=name, storage_id=path))
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
        blobs_path = InterventionDocument.objects.filter(intervention_id=intervention_id)
        result = list()
        for blob_meta in blobs_path:
            blob = self.__get_blob(blob_meta.storage_id)
            result.append({'name':blob_meta.name,'url':blob.public_url})
        return result

