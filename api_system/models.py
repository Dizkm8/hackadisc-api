from django.db import models

class Company(models.Model):
    company_name = models.CharField(max_length=100)
    is_multi_main = models.BooleanField(default=False)
    main_company = models.ForeignKey('self', on_delete=models.CASCADE)

class Worker(models.Model):
    class State(models.IntegerChoices):
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

class Evaluation(models.Model):
    worker = models.ForeignKey("Worker", on_delete=models.CASCADE)
    date = models.DateField()
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
    date = models.DateField()
    category = models.IntegerField(choices=Category)
    competence = models.IntegerField(choices=Competence)

class InterventionParticipant(models.Model):
    worker = models.ForeignKey("Worker", on_delete=models.CASCADE)
    intervention = models.ForeignKey("Intervention", on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

class Contract(models.Model):
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
