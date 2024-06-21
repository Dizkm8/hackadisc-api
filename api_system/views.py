from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Worker, Intervention
from .serializers import WorkerSerializer, WorkerDetailSerializer, DocumentSerializer, FileSerializer, WorkerWithCheckSerializer
from .services.FirebaseService import FirebaseService
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination

class WorkerListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            (user, token) = JWTAuthentication().authenticate(request)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        workers = Worker.objects.filter(company_id=user.company_id)
        paginator = LimitOffsetPagination()
        paginated_workers = paginator.paginate_queryset(workers, request, view=self)
        serializer = WorkerSerializer(paginated_workers, many=True)
        return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def get_worker_by_rut(request, rut):
    # Autenticar y obtener el usuario y token
    try:
        (user, token) = JWTAuthentication().authenticate(request)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        worker = Worker.objects.get(rut=rut, company_id=user.company_id)
    except Worker.DoesNotExist:
        return Response({"error": "Worker not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = WorkerDetailSerializer(worker)
    return Response(serializer.data)

@api_view(['GET'])
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
        return Response({"error": "Invalid competence ID"}, status=status.HTTP_400_BAD_REQUEST)

    # Mapa de competencias a los campos correspondientes en el modelo Evaluation
    competence_field_map = {
        1: 'adaptability_to_change',
        2: 'safe_conduct',
        3: 'dynamism_energy',
        4: 'personal_effectiveness',
        5: 'initiative',
        6: 'working_under_pressure'
    }

    # Verificar que el competence_id es válido
    if competence_id not in competence_field_map:
        return Response({"error": "Invalid competence ID"}, status=status.HTTP_400_BAD_REQUEST)

    competence_field = competence_field_map[competence_id]

    # Obtener todos los trabajadores de la empresa del usuario autenticado
    workers = Worker.objects.filter(company_id=company_id)

    # Serializar los trabajadores
    context = {'request': request, 'competence_id': competence_id}
    serializer = WorkerWithCheckSerializer(workers, many=True, context=context)

    return Response(serializer.data, status=status.HTTP_200_OK)
class InterventionDocumentsView(APIView):
    parser_classes = [MultiPartParser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = FirebaseService()

    def get(self, request, id):
        # TODO: handle permissions
        try:
            Intervention.objects.get(id=id)
        except Intervention.DoesNotExist:
            return Response("The intervention doesn't exists", status=status.HTTP_400_BAD_REQUEST)

        documents = self.storage.list_documents(id)
        serializer = DocumentSerializer(data=documents, many=True)
        serializer.is_valid(raise_exception=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, id):
        documents = list()
        for document in request.FILES.getlist('documents'):
            documents.append((document.file, document.name))
        results = self.storage.upload_documents(id, documents)
        # TODO: handle upload failures
        return Response(results, status=status.HTTP_200_OK)
