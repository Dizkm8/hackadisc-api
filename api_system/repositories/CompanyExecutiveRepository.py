from collections import Counter

from django.db import connection
from django.db.models import Avg
from django.forms import model_to_dict

from api_system.models import Evaluation, Contract, Intervention


class CompanyExecutiveRepository():
    def __init__(self):
        pass

    def get_average_score_by_competence(self, company_id, is_multi_company):
        if is_multi_company:
            query = Evaluation.objects.filter(worker__company__main_company__id=company_id)
        else:
            query = Evaluation.objects.filter(worker__company__id = company_id)

        competences_average = query.aggregate(
            Avg("adaptability_to_change"),
            Avg("safe_conduct"),
            Avg("dynamism_energy"),
            Avg("personal_effectiveness"),
            Avg("initiative"),
            Avg("working_under_pressure"),
        )
        return competences_average

    def get_competence_count_by_grade(self, company_id, is_multi_company):
        if is_multi_company:
            query = Evaluation.objects.filter(worker__company__main_company__id=company_id)
        else:
            query = Evaluation.objects.filter(worker__company__id=company_id)

        competence_grade_count = dict()

        scores = query.values_list("adaptability_to_change", flat=True)
        grades = [Evaluation.calculate_letter_grade(score) for score in scores]
        competence_grade_count["adaptability_to_change"] = Counter(grades)

        scores = query.values_list("safe_conduct", flat=True)
        grades = [Evaluation.calculate_letter_grade(score) for score in scores]
        competence_grade_count["safe_conduct"] = Counter(grades)

        scores = query.values_list("dynamism_energy", flat=True)
        grades = [Evaluation.calculate_letter_grade(score) for score in scores]
        competence_grade_count["dynamism_energy"] = Counter(grades)

        scores = query.values_list("personal_effectiveness", flat=True)
        grades = [Evaluation.calculate_letter_grade(score) for score in scores]
        competence_grade_count["personal_effectiveness"] = Counter(grades)

        scores = query.values_list("initiative", flat=True)
        grades = [Evaluation.calculate_letter_grade(score) for score in scores]
        competence_grade_count["initiative"] = Counter(grades)

        scores = query.values_list("working_under_pressure", flat=True)
        grades = [Evaluation.calculate_letter_grade(score) for score in scores]
        competence_grade_count["working_under_pressure"] = Counter(grades)

        return competence_grade_count

    def get_worker_count_by_state(self, company_id, is_multi_company):
        if is_multi_company:
            query = f"""
                    select w.state, count(w.state) 
                        from api_system_worker as w 
                        join api_system_company as c on w.company_id = c.id
                        where c.main_company_id=%s
                        group by w.state;
                    """
        else:
            query = f"""
                    select w.state, count(w.state) 
                        from api_system_worker as w 
                        where w.company_id=%s 
                        group by w.state;
                    """
        with connection.cursor() as cursor:
            cursor.execute(query, [company_id])
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return data

    def get_worker_count_by_subunit_state(self, company_id, is_multi_company):
        if is_multi_company:
            query = f"""
                    select w.company_id, w.state, count(w.state) 
                        from api_system_worker as w 
                        join api_system_company as c on w.company_id = c.id
                        where c.main_company_id=%s
                        group by w.company_id, w.state;
                    """
        else:
            query = f"""
                    select w.area_id, w.state, count(w.state) 
                        from api_system_worker as w 
                        where w.company_id=%s 
                        group by w.area_id, w.state;
                    """
        with connection.cursor() as cursor:
            cursor.execute(query, [company_id])
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return data

    def get_worker_count_by_subunit_filter_state(self, company_id, subunit_ids, is_multi_company):
        if is_multi_company:
            query = f"""
                    select w.company_id, w.state, count(w.state) 
                        from api_system_worker as w 
                        join api_system_company as c on w.company_id = c.id
                        where w.company_id in %s and c.main_company_id=%s
                        group by w.company_id, w.state;
                    """
        else:
            query = f"""
                    select w.area_id,w.state, count(w.state) 
                        from api_system_worker as w 
                        where w.area_id in %s and w.company_id=%s 
                        group by w.area_id, w.state;
                    """
        with connection.cursor() as cursor:
            cursor.execute(query, [subunit_ids, company_id])
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return data

    def get_active_intervention_count_by_category(self, company_id, is_multi_company):
        if is_multi_company:
            query = f"""
                    select i.category, count(*) 
                        from api_system_intervention as i 
                        join api_system_company as c on i.company_id = c.id
                        where i.date > now() and c.main_company_id=%s
                        group by i.category
                    """
        else:
            query = """
                    select i.category, count(*) 
                        from api_system_intervention as i 
                        where i.date > now() and i.company_id=%s 
                        group by i.category
                    """

        with connection.cursor() as cursor:
            cursor.execute(query, [company_id])
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return data

    def get_active_participants_by_competence_category(self, company_id, is_multi_company):
        if is_multi_company:
            query = """
                    select count(w.*), i.category 
                        from api_system_intervention as i 
                            join api_system_interventionparticipant p on p.intervention_id = i.id 
                            join api_system_worker as w on p.worker_id = w.id 
                            join api_system_company as c on i.company_id = c.id
                        where i.date > now() and i.competence = %s and c.main_company_id=%s
                        group by i.category;
                    """
        else:
            query = """
                    select count(w.*), i.category 
                        from api_system_intervention as i 
                            join api_system_interventionparticipant p on p.intervention_id = i.id 
                            join api_system_worker as w on p.worker_id = w.id 
                        where i.date > now() and i.competence = %s and w.company_id=%s 
                        group by i.category;
                    """
        participant_count = dict()

        with connection.cursor() as cursor:
            for competence in Intervention.Competence.values:
                cursor.execute(query, [competence, company_id])
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                participant_count[competence] = data

        return participant_count

    def get_contract_info(self, company_id):
        return [model_to_dict(contract, fields=["start_date", "end_date"]) for contract in Contract.objects.filter(company__id = company_id).all()]