from django.db import models
from django.utils.translation import gettext_lazy as _

class Company(models.Model):
    company_name = models.CharField(max_length=100)
    is_multi_main = models.BooleanField(default=False)
    main_company = models.ForeignKey("self", on_delete=models.CASCADE, null=True)


class Worker(models.Model):
    class State(models.IntegerChoices):
        NOT_EVALUATED = 0, _("No evaluado")
        EVALUATED = 1, _("Evaluado")
        IN_INTERVENTION = 2, _("En intervención")
        INTERVENED = 3, _("Intervenido")

    rut = models.CharField(max_length=20, unique=True)
    user_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    area_id = models.IntegerField()
    area_name = models.CharField(max_length=100)
    post_id = models.IntegerField()
    post_name = models.CharField(max_length=100)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    state = models.IntegerField(choices=State, default=State.EVALUATED)

    def get_latest_evaluation(self):
        """Retrieves the most recent evaluation for the worker."""
        try:
            return self.evaluation_set.order_by(
                "-date"
            ).first()  # Order by descending date
        except Evaluation.DoesNotExist:
            return None  # Return None if no evaluations exist

    def calculate_latest_evaluation_letter_grade(self):
        """Calculates the letter grade based on the most recent evaluation."""
        latest_evaluation = self.get_latest_evaluation()
        if latest_evaluation:
            return latest_evaluation.calculate_average_letter_grade()
        else:
            return None  # Default value if no evaluations exist


class Evaluation(models.Model):
    worker = models.ForeignKey("Worker", on_delete=models.CASCADE)
    date = models.DateTimeField()
    adaptability_to_change = models.FloatField()
    safe_conduct = models.FloatField()
    dynamism_energy = models.FloatField()
    personal_effectiveness = models.FloatField()
    initiative = models.FloatField()
    working_under_pressure = models.FloatField()

    def calculate_average_grade(self):
        """Calculates the grade."""
        total_score = (
                float(self.adaptability_to_change)
                + float(self.safe_conduct)
                + float(self.dynamism_energy)
                + float(self.personal_effectiveness)
                + float(self.initiative)
                + float(self.working_under_pressure)
            )
        return total_score / 6.0  # Assuming 6 evaluation fields

    def calculate_average_letter_grade(self):
        """Calculates the letter grade."""
        average_score = self.calculate_average_grade()

        # Calculate the letter grade based on the average score
        return self.calculate_letter_grade(average_score)

    @staticmethod
    def calculate_letter_grade(score):
        # Calculate the letter grade based on the  score
        if score >= 0.75:
            return "A"
        elif score >= 0.5:
            return "B"
        elif score >= 0.25:
            return "C"
        else:
            return "D"


class Intervention(models.Model):
    class Category(models.IntegerChoices):
        COURSE = 1, _("Curso")
        TRAINING = 2, _("Capacitación")
        SPEECH = 3, _("Charla")

    class Competence(models.IntegerChoices):
        ADAPTABILITY = 1, _("Adaptabilidad")
        CONDUCT = 2, _("Trabajo bajo presión")
        DYNAMISM = 3, _("Iniciativa")
        EFFECTIVENESS = 4, _("Dinamismo y energía")
        INITIATIVE = 5, _("Conducta segura")
        PRESSURE = 6, _("Efectividad")

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    date = models.DateTimeField()
    category = models.IntegerField(choices=Category)
    competence = models.IntegerField(choices=Competence)
    is_completed = models.BooleanField(default=False)


class InterventionParticipant(models.Model):
    id = models.AutoField(primary_key=True)
    worker = models.ForeignKey("Worker", on_delete=models.CASCADE, related_name="intervention_participants")
    intervention = models.ForeignKey("Intervention", on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)


class InterventionDocument(models.Model):
    intervention = models.ForeignKey("Intervention", on_delete=models.CASCADE)
    storage_id = models.TextField(unique=True)
    name = models.TextField()

class Contract(models.Model):
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
