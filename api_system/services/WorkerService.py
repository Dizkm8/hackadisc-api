from api_system.models import InterventionParticipant, Worker


class WorkerService:
    def __init__(self):
        pass

    # TODO: move business logic from views
    def complete_intervention(self, participation):
        participation.is_completed = True
        participation.save()

        worker = participation.worker
        is_done = True
        for participation in InterventionParticipant.objects.filter(worker__id=worker.id).all():
            if not participation.is_completed:
                is_done = False
        if is_done:
            worker.state = Worker.State.INTERVENED
            worker.save()
