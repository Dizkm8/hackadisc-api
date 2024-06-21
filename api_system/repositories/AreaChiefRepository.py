from django.db.models import Avg
from django.db import connection
from api_system.models import Evaluation, Intervention
from collections import Counter

class AreaChiefRepository:
    def __init__(self):
        pass

    def get_average_score_by_competence(self, company_id, area_id):
        query = Evaluation.objects.filter(worker__company__id = company_id,worker__area_id=area_id)
        # add disctint?
        competences_average = query.aggregate(
            Avg("adaptability_to_change"),
            Avg("safe_conduct"),
            Avg("dynamism_energy"),
            Avg("personal_effectiveness"),
            Avg("initiative"),
            Avg("working_under_pressure"),
        )
        return competences_average

    def get_competence_count_by_grade(self, company_id, area_id):
        query = Evaluation.objects.filter(worker__company__id=company_id, worker__area_id=area_id)
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

    def get_worker_count_by_state(self, company_id, area_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                select w.state, count(w.state) 
                    from api_system_worker as w 
                    where w.area_id=%s and w.company_id=%s 
                    group by w.state;
                """, [area_id, company_id])
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return data

    def get_active_intervention_count_by_category(self, company_id):
        with connection.cursor() as cursor:
            cursor.execute("""
            select i.category, count(*) 
                from api_system_intervention as i 
                where not i.is_completed and i.company_id=%s 
                group by i.category
            """, [company_id])
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return data
    def get_active_participants_by_competence_category(self, company_id, area_id):
        participant_count = dict()

        with connection.cursor() as cursor:
            for competence in Intervention.Competence.values:
                cursor.execute("""
                select count(w.*), i.category 
                    from api_system_intervention as i 
                        join api_system_interventionparticipant p on p.intervention_id = i.id 
                        join api_system_worker as w on p.worker_id = w.id 
                    where not i.is_completed and i.competence = %s and w.area_id = %s and w.company_id=%s 
                    group by i.category;
                """, [competence, area_id, company_id])
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                participant_count[competence] = data

        return participant_count

    def get_intervention_summary(self, company_id, area_id):
        with connection.cursor() as cursor:
            cursor.execute("""
            select i.name, count(w.*), i.date 
                from api_system_intervention as i 
                    join api_system_interventionparticipant p on p.intervention_id = i.id 
                    join api_system_worker as w on p.worker_id = w.id 
                where not i.is_completed and w.area_id=%s and w.company_id=%s 
                group by i.id, i.date 
                order by i.date asc;
            """, [area_id, company_id])
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return data