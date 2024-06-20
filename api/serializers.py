from rest_framework import serializers
from .models import Company, Worker, Evaluation, Intervention, InterventionParticipant, Contract

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'  # You can customize the fields if needed

class WorkerSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    def get_rating(self, obj):
        # Assuming the calculate_rating method in your model returns the actual rating
        return obj.calculate_rating()

    class Meta:
        model = Worker
        fields = ('id', 'user_name', 'area_id', 'area_name', 'post_id', 'post_name', 'company', 'company_name', 'state', 'rating')

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'  # You can customize the fields if needed

class InterventionCategoryChoiceField(serializers.ChoiceField):
    # Custom field to display human-readable category names
    def to_representation(self, value):
        return self.choices[value][1]

class InterventionCompetenceChoiceField(serializers.ChoiceField):
    # Custom field to display human-readable competence names
    def to_representation(self, value):
        return self.choices[value][1]

class InterventionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='get_category_display', read_only=True)
    competence_name = serializers.CharField(source='get_competence_display', read_only=True)

    class Meta:
        model = Intervention
        fields = ('id', 'company', 'name', 'description', 'date', 'category', 'category_name', 'competence', 'competence_name')

class InterventionParticipantSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source='worker.user_name', read_only=True)
    intervention_name = serializers.CharField(source='intervention.name', read_only=True)

    class Meta:
        model = InterventionParticipant
        fields = ('id', 'worker', 'worker_name', 'intervention', 'intervention_name', 'is_completed')

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'  # You can customize the fields if needed
