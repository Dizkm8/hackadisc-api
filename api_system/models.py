from django.db import models


class Company(models.Model):
    company_name = models.CharField(max_length=100)
    is_multi_main = models.BooleanField(default=False)
    main_company = models.ForeignKey("self", on_delete=models.CASCADE, null=True)


class Worker(models.Model):
    class State(models.IntegerChoices):
        NOT_EVALUATED = 0
        EVALUATED = 1
        IN_INTERVENTION = 2
        INTERVENED = 3

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
            total_score = (
                float(latest_evaluation.adaptability_to_change)
                + float(latest_evaluation.safe_conduct)
                + float(latest_evaluation.dynamism_energy)
                + float(latest_evaluation.personal_effectiveness)
                + float(latest_evaluation.initiative)
                + float(latest_evaluation.working_under_pressure)
            )
            average_score = total_score / 6.0  # Assuming 6 evaluation fields

            # Calculate the letter grade based on the average score
            if average_score >= 0.75:
                return "A"
            elif average_score >= 0.5:
                return "B"
            elif average_score >= 0.25:
                return "C"
            else:
                return "D"
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


class Intervention(models.Model):
    class Category(models.IntegerChoices):
        COURSE = 1
        TRAINING = 2
        SPEECH = 3

    class Competence(models.IntegerChoices):
        ADAPTABILITY = 1
        CONDUCT = 2
        DYNAMISM = 3
        EFFECTIVENESS = 4
        INITIATIVE = 5
        PRESSURE = 6

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    date = models.DateTimeField()
    category = models.IntegerField(choices=Category)
    competence = models.IntegerField(choices=Competence)


class InterventionParticipant(models.Model):
    worker = models.ForeignKey("Worker", on_delete=models.CASCADE)
    intervention = models.ForeignKey("Intervention", on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

class InterventionDocument(models.Model):
    intervention = models.ForeignKey("Intervention", on_delete=models.CASCADE)
    storage_id = models.TextField()
    name = models.TextField()

class Contract(models.Model):
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
