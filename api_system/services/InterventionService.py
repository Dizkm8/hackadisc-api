from api_system.models import InterventionParticipant, Intervention
from api_system.services.FirebaseService import FirebaseService
from api_system.services.WorkerService import WorkerService


class InterventionService:
    def __init__(self):
        self.worker_service = WorkerService()
        self.storage_service = FirebaseService()

    # TODO: move business logic from views

    def complete_intervention(self, intervention_id, files):
        upload_results = self.storage_service.upload_documents(intervention_id, files)

        for result in upload_results:
            if result is not None:
                return (-1,"Upload failed.")

        participants = InterventionParticipant.objects.filter(intervention__id=intervention_id).only("worker").all()

        for participation in participants:
            self.worker_service.complete_intervention(participation)

        return (0,None)

    def get_intervention_files(self, intervention_id):
        try:
            Intervention.objects.get(id=id)
        except Intervention.DoesNotExist:
            return (-1, "The intervention doesn't exists")

        return (0, self.storage_service.list_documents(intervention_id))
