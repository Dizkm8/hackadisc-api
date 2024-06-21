from collections import Counter

from django.db import connection
from django.db.models import Avg
from api_system.models import Evaluation, Intervention
from api_system.services.DateService import DateService


class AdminRepository():
    def __init__(self):
        pass

    def get_average_score_by_competence(self):
        query = Evaluation.objects.all()

        competences_average = query.aggregate(
            Avg("adaptability_to_change"),
            Avg("safe_conduct"),
            Avg("dynamism_energy"),
            Avg("personal_effectiveness"),
            Avg("initiative"),
            Avg("working_under_pressure"),
        )
        return competences_average

    def get_competence_count_by_grade(self):
        query = Evaluation.objects.all()

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

    def get_worker_count_by_state(self):
        query = f"""
                select w.state, count(w.state) 
                    from api_system_worker as w
                    group by w.state;
                """
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return data

    def get_active_intervention_count_by_category(self):
        query = """
            select i.category, count(*) 
                from api_system_intervention as i 
                where not i.is_completed
                group by i.category
            """

        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return data

    def get_active_participants_by_competence_category(self):
        query = """
            select count(w.*), i.category 
                from api_system_intervention as i 
                    join api_system_interventionparticipant p on p.intervention_id = i.id 
                    join api_system_worker as w on p.worker_id = w.id 
                where not i.is_completed and i.competence = %s
                group by i.category;
            """
        participant_count = dict()

        with connection.cursor() as cursor:
            for competence in Intervention.Competence.values:
                cursor.execute(query, [competence])
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                participant_count[competence] = data

        return participant_count

    def get_company_summary(self):
        query="""
        select c.company_name,
        (select count(*) from api_system_worker as w where w.company_id = c.id) as worker_count,
        (select count(*) from api_system_worker as w where w.company_id = c.id and w.state != 0) as evaluation_count,
        (select count(*) from api_system_intervention as i where i.company_id = c.id and not i.is_completed) as intervention_count,
        main_c.company_name as main_company,
        contract.start_date,
        contract.end_date
        from api_system_company c join api_system_contract as contract on c.id = contract.id
        left join api_system_company main_c on c.main_company_id = main_c.id;
        """

        data = list()

        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            columns.append("remaining_time")
            for row in cursor.fetchall():
                remaining_time = DateService.format_time_delta(row[-1], row[-2]) # end_date, start_date
                data_row = [*row, remaining_time]
                data.append(dict(zip(columns, data_row)))

        return data