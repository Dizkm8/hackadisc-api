from api_system.repositories.AdminRepository import AdminRepository


class AdminService:
    def __init__(self):
        self.repository = AdminRepository()

    def get_statistics(self):

        result = dict()
        result["competence_score_average"] = self.repository.get_average_score_by_competence()
        result["grade_count"] = self.repository.get_competence_count_by_grade()
        result["state_count"] = self.repository.get_worker_count_by_state()
        result["active_intervention"] = self.repository.get_active_intervention_count_by_category ()
        result["intervention_participants"] = self.repository.get_active_participants_by_competence_category()

        return result

    def get_company_summary(self):
        return self.repository.get_company_summary()
