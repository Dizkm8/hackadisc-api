import firebase_admin

class FirebaseService:
    def __init__(self):
        self.firebase = firebase_admin.initialize_app(options={
            'storageBucket': 'hackadisc.appspot.com'
        })
        self.bucket = firebase_admin.storage.bucket()

    def upload_file(self, blob_name, file):
        blob = self.bucket.blob(blob_name)
        file.seek(0)
        blob.upload_from_file(file)