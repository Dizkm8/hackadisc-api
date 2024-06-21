from api_auth.models import ROLE
from api_system.repositories.CompanyExecutiveRepository import CompanyExecutiveRepository


class CompanyExecutiveService:
    def __init__(self, company_id=None, subunit_id=None):
        self.company_id = company_id
        self.subunit_id = subunit_id
        self.repository = CompanyExecutiveRepository()

    def get_statistics(self, role, company_id=None, subunit_id=None):
        if company_id is None:
            company_id = self.company_id
        if subunit_id is None:
            subunit_id = self.subunit_id

        is_multi_company = role == ROLE.ADMIN_MULTICOMPANY

        result = dict()
        result["competence_score_average"] = self.repository.get_average_score_by_competence(company_id, is_multi_company)
        result["grade_count"] = self.repository.get_competence_count_by_grade(company_id, is_multi_company)
        result["state_count"] = self.repository.get_worker_count_by_state(company_id, is_multi_company)
        result["subunit_state_count"] = self.repository.get_worker_count_by_subunit_state(company_id, is_multi_company)
        result["active_intervention"] = self.repository.get_active_intervention_count_by_category (company_id, is_multi_company)
        result["intervention_participants"] = self.repository.get_active_participants_by_competence_category(company_id, is_multi_company)
        result["contracts"] = self.repository.get_contract_info(company_id)

        return result