from api_system.repositories.AreaChiefRepository import AreaChiefRepository


class AreaChiefService:
    def __init__(self, company_id=None, area_id=None):
        self.company_id = company_id
        self.area_id = area_id
        self.repository = AreaChiefRepository()

    def get_statistics(self, company_id=None, area_id=None):
        if company_id is None:
            company_id = self.company_id
        if area_id is None:
            area_id = self.area_id

        result = dict()
        result["competence_score_average"] = self.repository.get_average_score_by_competence(company_id, area_id)
        result["grade_count"] = self.repository.get_competence_count_by_grade(company_id, area_id)
        result["state_count"] = self.repository.get_worker_count_by_state(company_id, area_id)
        result["active_intervention"] = self.repository.get_active_intervention_count_by_category (company_id)
        result["intervention_participants"] = self.repository.get_active_participants_by_competence_category(company_id, area_id)
        result["intervention_summary"] = self.repository.get_intervention_summary(company_id, area_id)

        return result