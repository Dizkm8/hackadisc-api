from babel.dates import format_datetime

from api_system.models import InterventionParticipant, Intervention
from api_system.services.EmailBuilderService import EmailBuilderService
from api_system.services.FirebaseService import FirebaseService
from api_system.services.GmailService import GmailService
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

        intervention = Intervention.objects.get(id=intervention_id)
        intervention.is_completed = True
        intervention.save()

        return (0,None)

    def get_intervention_files(self, intervention_id):
        try:
            Intervention.objects.get(id=id)
        except Intervention.DoesNotExist:
            return (-1, "The intervention doesn't exists")

        return (0, self.storage_service.list_documents(intervention_id))

    @staticmethod
    def send_notification(intervention, workers):
        gmail = GmailService()
        builder = EmailBuilderService()
        original_info = {
            "intervention": intervention.name,
            "description": intervention.description,
            "competence": intervention.get_competence_display(),
            "category": intervention.get_category_display(),
            "date": format_datetime(intervention.date, "EEEE d 'de' MMMM 'de' yyyy", locale='es_CL'),
        }

        bulk_info = list()
        for worker in workers:
            info = original_info.copy()
            info["worker"] = worker.user_name
            info["email"] = worker.email
            bulk_info.append(info)

        bulk_messages = builder.compose_all_emails(bulk_info)

        for message in bulk_messages:
            gmail.send_email(message)
        gmail.disconnect()

        return