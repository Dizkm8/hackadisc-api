from rest_framework import serializers
from .models import (
    Company,
    Worker,
    Evaluation,
    Intervention,
    InterventionParticipant,
    Contract,
)

# Intervention
class InterventionHistorySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name')
    
    class Meta:
        model = Intervention
        fields = ['id', 'name', 'date', 'competence', 'description', 'category', 'company_name']

class InterventionParticipantSerializer(serializers.ModelSerializer):
    intervention = InterventionHistorySerializer()

    class Meta:
        model = InterventionParticipant
        fields = ['intervention', 'is_completed']

class InterventionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='get_category_display', read_only=True)
    competence_name = serializers.CharField(source='get_competence_display', read_only=True)

    class Meta:
        model = Intervention
        fields = [
            'id', 'name', 'description', 'date', 'category_name', 'competence_name'
        ]

# Company
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"  # You can customize the fields if needed

# Worker
class WorkerSerializer(serializers.ModelSerializer):  # Aquí está la corrección
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
        interventions = obj.intervention_participants.all()
        return InterventionParticipantSerializer(interventions, many=True).data

class WorkerWithCheckSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    state_name = serializers.CharField(source='get_state_display', read_only=True)
    is_checked = serializers.SerializerMethodField()
    latest_evaluation_letter_grade = serializers.SerializerMethodField()


    class Meta:
        model = Worker
        fields = [
            'id', 'rut', 'user_name', 'email', 'area_name', 
            'post_name', 'company_name', 'state_name', 'is_checked',
            'latest_evaluation_letter_grade'
        ]
        
    def get_latest_evaluation_letter_grade(self, obj):
        return obj.calculate_latest_evaluation_letter_grade()
    
    def get_company_name(self, obj):
        return obj.company.company_name
    
    def get_is_checked(self, obj):
        competence_id = self.context.get('competence_id')
        competence_field_map = {
            1: 'adaptability_to_change',
            2: 'safe_conduct',
            3: 'dynamism_energy',
            4: 'personal_effectiveness',
            5: 'initiative',
            6: 'working_under_pressure'
        }
        competence_field = competence_field_map[competence_id]
        if obj.state == Worker.State.EVALUATED:
            latest_evaluation = obj.evaluation_set.order_by('-date').first()
            if latest_evaluation and getattr(latest_evaluation, competence_field) < 0.5:
                return 1
        return 0

#Evaluation
class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = "__all__"  # You can customize the fields if needed


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"  # You can customize the fields if needed

class DocumentSerializer(serializers.Serializer):
    name=serializers.CharField()
    url=serializers.CharField()

class FileSerializer(serializers.Serializer):
    file=serializers.FileField()

class CreateInterventionSerializer(serializers.ModelSerializer):
    ruts = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model = Intervention
        fields = ['name', 'category', 'competence', 'date', 'description', 'ruts']
        
