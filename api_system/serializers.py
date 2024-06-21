from rest_framework import serializers
from .models import (
    Company,
    Worker,
    Evaluation,
    Intervention,
    InterventionParticipant,
    Contract,
)

class InterventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervention
        fields = ['id', 'name', 'description', 'date', 'category', 'competence']

class InterventionParticipantSerializer(serializers.ModelSerializer):
    intervention = InterventionSerializer()

    class Meta:
        model = InterventionParticipant
        fields = ['intervention', 'is_completed']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"  # You can customize the fields if needed
        
class WorkersSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    latest_evaluation_letter_grade = serializers.SerializerMethodField()
    state_name = serializers.CharField(source='get_state_display', read_only=True)

    class Meta:
        model = Worker
        fields = ['id', 'user_name', 'rut', 'post_name', 'company_name', 'latest_evaluation_letter_grade', 'state_name', 'email', 'area_name', 'state']
    
    def get_company_name(self, obj):
        return obj.company.company_name

    def get_latest_evaluation_letter_grade(self, obj):
        return obj.calculate_latest_evaluation_letter_grade()
    

class WorkerDetailSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    state_name = serializers.CharField(source='get_state_display', read_only=True)
    adaptability_to_change = serializers.SerializerMethodField()
    safe_conduct = serializers.SerializerMethodField()
    dynamism_energy = serializers.SerializerMethodField()
    personal_effectiveness = serializers.SerializerMethodField()
    initiative = serializers.SerializerMethodField()
    working_under_pressure = serializers.SerializerMethodField()
    interventions_history = serializers.SerializerMethodField()


    class Meta:
        model = Worker
        fields = [
            'id', 'rut', 'user_name', 'email', 'area_name', 
            'post_name', 'company_name', 'state_name',
            'adaptability_to_change', 'safe_conduct', 'dynamism_energy',
            'personal_effectiveness', 'initiative', 'working_under_pressure',
            'interventions_history'
        ]
        
    def get_company_name(self, obj):
        return obj.company.company_name
    
    def get_latest_evaluation(self, obj):
        try:
            return obj.evaluation_set.latest('date')
        except Evaluation.DoesNotExist:
            return None

    def get_adaptability_to_change(self, obj):
        evaluation = self.get_latest_evaluation(obj)
        return evaluation.adaptability_to_change if evaluation else None

    def get_safe_conduct(self, obj):
        evaluation = self.get_latest_evaluation(obj)
        return evaluation.safe_conduct if evaluation else None

    def get_dynamism_energy(self, obj):
        evaluation = self.get_latest_evaluation(obj)
        return evaluation.dynamism_energy if evaluation else None

    def get_personal_effectiveness(self, obj):
        evaluation = self.get_latest_evaluation(obj)
        return evaluation.personal_effectiveness if evaluation else None

    def get_initiative(self, obj):
        evaluation = self.get_latest_evaluation(obj)
        return evaluation.initiative if evaluation else None

    def get_working_under_pressure(self, obj):
        evaluation = self.get_latest_evaluation(obj)
        return evaluation.working_under_pressure if evaluation else None
    
    def get_interventions_history(self, obj):
        interventions = obj.interventionparticipant_set.all()
        return InterventionParticipantSerializer(interventions, many=True).data



class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = "__all__"  # You can customize the fields if needed


class InterventionCategoryChoiceField(serializers.ChoiceField):
    # Custom field to display human-readable category names
    def to_representation(self, value):
        return self.choices[value][1]


class InterventionCompetenceChoiceField(serializers.ChoiceField):
    # Custom field to display human-readable competence names
    def to_representation(self, value):
        return self.choices[value][1]




class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"  # You can customize the fields if needed
