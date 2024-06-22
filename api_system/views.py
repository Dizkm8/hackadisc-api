from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Worker, Intervention, InterventionParticipant, Message
from .serializers import (
    InterventionDetailSerializer,
    InterventionSerializer,
    WorkerSerializer,
    WorkerDetailSerializer,
    WorkerWithCheckSerializer,
    CreateInterventionSerializer,
)
from .services.AdminService import AdminService
from .services.AreaChiefService import AreaChiefService
from .services.CompanyExecutiveService import CompanyExecutiveService
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination
from api_auth.models import User
from .services.InterventionService import InterventionService
from openai import OpenAI

openai_client = OpenAI(
    api_key="sk-proj-JAyTvASXnrZJrC82CU9cT3BlbkFJhMfEp5925C9SkdrOGNGt"
)


class WorkerListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            (user, token) = JWTAuthentication().authenticate(request)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        workers = Worker.objects.filter(
            company_id=user.company_id, area_id=user.area_id
        )
        paginator = LimitOffsetPagination()
        paginated_workers = paginator.paginate_queryset(workers, request, view=self)
        serializer = WorkerSerializer(paginated_workers, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def get_worker_by_rut(request, rut):
    # Autenticar y obtener el usuario y token
    try:
        (user, token) = JWTAuthentication().authenticate(request)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        worker = Worker.objects.get(
            rut=rut, company_id=user.company_id, area_id=user.area_id
        )
    except Worker.DoesNotExist:
        return Response({"error": "Worker not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = WorkerDetailSerializer(worker)
    return Response(serializer.data)


@api_view(["GET"])
def get_workers_by_competence(request, competence_id):
    # Autenticar y obtener el usuario y token
    try:
        (user, token) = JWTAuthentication().authenticate(request)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    # Obtener el company_id del usuario autenticado
    company_id = user.company_id

    # Validar el competence_id
    try:
        competence_id = int(competence_id)
    except ValueError:
        return Response(
            {"error": "Invalid competence ID"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Mapa de competencias a los campos correspondientes en el modelo Evaluation
    competence_field_map = {
        1: "adaptability_to_change",
        2: "safe_conduct",
        3: "dynamism_energy",
        4: "personal_effectiveness",
        5: "initiative",
        6: "working_under_pressure",
    }

    # Verificar que el competence_id es válido
    if competence_id not in competence_field_map:
        return Response(
            {"error": "Invalid competence ID"}, status=status.HTTP_400_BAD_REQUEST
        )

    competence_field = competence_field_map[competence_id]

    # Obtener todos los trabajadores de la empresa del usuario autenticado
    workers = Worker.objects.filter(company_id=company_id, area_id=user.area_id)

    # Serializar los trabajadores
    context = {"request": request, "competence_id": competence_id}
    serializer = WorkerWithCheckSerializer(workers, many=True, context=context)

    return Response(serializer.data, status=status.HTTP_200_OK)


class CompleteInterventionView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.intervention_service = InterventionService()

    def post(self, request, intervention_id):
        try:
            (user, token) = JWTAuthentication().authenticate(request)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        documents = list()
        for document in request.FILES.getlist("documents"):
            documents.append((document.file, document.name))
        results = self.intervention_service.complete_intervention(
            intervention_id, documents
        )
        return Response(results, status=status.HTTP_200_OK)


# intervention
@api_view(["POST"])
def create_intervention(request):
    try:
        (user, token) = JWTAuthentication().authenticate(request)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = CreateInterventionSerializer(data=request.data)
    if serializer.is_valid():
        company_id = user.company_id

        # Crear la intervención
        intervention = Intervention.objects.create(
            company_id=company_id,
            name=serializer.validated_data["name"],
            category=serializer.validated_data["category"],
            competence=serializer.validated_data["competence"],
            date=serializer.validated_data["date"],
            description=serializer.validated_data["description"],
        )

        # Asignar participantes
        ruts = serializer.validated_data["ruts"]
        workers = list()
        for rut in ruts:
            print(rut, company_id)
            worker = Worker.objects.get(
                rut=rut, company_id=company_id, area_id=user.area_id
            )
            InterventionParticipant.objects.create(
                worker=worker, intervention=intervention, is_completed=True
            )
            worker.state = Worker.State.IN_INTERVENTION
            worker.save()
            workers.append(worker)
        InterventionService.send_notification(intervention, workers)
        return Response(
            {"message": "Intervention created successfully"},
            status=status.HTTP_201_CREATED,
        )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InterventionListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            (user, token) = JWTAuthentication().authenticate(request)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        # Obtener todas las intervenciones de la empresa del usuario autenticado
        interventions = Intervention.objects.filter(company_id=user.company_id)

        paginator = LimitOffsetPagination()
        paginated_interventions = paginator.paginate_queryset(
            interventions, request, view=self
        )
        serializer = InterventionSerializer(paginated_interventions, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def get_intervention_detail(request, intervention_id):
    try:
        intervention = Intervention.objects.get(id=intervention_id)
    except Intervention.DoesNotExist:
        return Response(
            {"error": "Intervention not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = InterventionDetailSerializer(intervention)
    return Response(serializer.data, status=status.HTTP_200_OK)


class AreaDashboardView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.area_service = AreaChiefService()

    def get(self, request):
        try:
            (user, token) = JWTAuthentication().authenticate(request)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            return Response(
                self.area_service.get_statistics(user.company_id, user.area_id),
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class CompanyDashboardView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_service = CompanyExecutiveService()

    def get(self, request):
        try:
            (user, token) = JWTAuthentication().authenticate(request)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            return Response(
                self.company_service.get_statistics(user.role, user.company_id),
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class AdminDashboardView(ViewSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin_service = AdminService()

    def get(self, request):
        try:
            (user, token) = JWTAuthentication().authenticate(request)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            return Response(
                self.admin_service.get_statistics(), status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    def get_company_summary(self, request):
        try:
            (user, token) = JWTAuthentication().authenticate(request)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            summary = self.admin_service.get_company_summary()
            paginator = LimitOffsetPagination()
            paginated_summary = paginator.paginate_queryset(summary, request, view=self)
            return paginator.get_paginated_response(paginated_summary)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["DELETE"])
def remove_worker_from_intervention(request, intervention_id, worker_rut):
    try:
        worker = Worker.objects.get(rut=worker_rut)
    except Worker.DoesNotExist:
        return Response({"error": "Worker not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        intervention = Intervention.objects.get(id=intervention_id)
    except Intervention.DoesNotExist:
        return Response(
            {"error": "Intervention not found"}, status=status.HTTP_404_NOT_FOUND
        )

    try:
        intervention_participant = InterventionParticipant.objects.get(
            worker=worker, intervention=intervention
        )
        intervention_participant.delete()
        return Response(
            {"success": "Worker removed from intervention"},
            status=status.HTTP_204_NO_CONTENT,
        )
    except InterventionParticipant.DoesNotExist:
        return Response(
            {"error": "Worker is not a participant in this intervention"},
            status=status.HTTP_404_NOT_FOUND,
        )


class OpenAIGenerateView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt")

        try:
            (user, token) = JWTAuthentication().authenticate(request)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = user.id

        conversation_history = []
        if user_id:
            try:
                user_messages = Message.objects.filter(user_id=user_id, role="user").order_by('created_at')[:10]  # Get recent 5 user messages
                assistant_messages = Message.objects.filter(user_id=user_id, role="assistant").order_by('created_at')[:10]  # Get recent 5 assistant messages
                conversation_history.extend(user_messages)
                conversation_history.extend(assistant_messages)
            except User.DoesNotExist:
                return Response({"error": "Invalid user ID provided"}, status=400)

        openai_messages = []
        for message in conversation_history:
            openai_messages.append({"role": message.role, "content": message.content})
        openai_messages.append({"role": "user", "content": prompt}) 
        print(openai_messages)
        chat_completion = openai_client.chat.completions.create(
            messages=openai_messages,
            model="gpt-3.5-turbo",
        )

        generated_text = chat_completion.choices[0].message.content

        if user_id:
            Message.objects.create(content=prompt, role="user", user_id=user_id)
            Message.objects.create(content=generated_text, role="assistant", user_id=user_id)

        return Response({"response": generated_text})

