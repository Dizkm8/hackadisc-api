from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Worker, Intervention
from .serializers import  WorkersSerializer, WorkerDetailSerializer, DocumentSerializer, FileSerializer
from .services.FirebaseService import FirebaseService
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination

class WorkerListView(APIView):
    def get(self, request, *args, **kwargs):
        workers = Worker.objects.all()
        paginator = LimitOffsetPagination()
        paginated_workers = paginator.paginate_queryset(workers, request, view=self)
        serializer = WorkersSerializer(paginated_workers, many=True)
        return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def get_worker_by_rut(request, rut):
    try:
        worker = Worker.objects.get(rut=rut)
    except Worker.DoesNotExist:
        return Response({"error": "Worker not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = WorkerDetailSerializer(worker)
    return Response(serializer.data)

class InterventionDocumentsView(APIView):
    parser_classes = [MultiPartParser]

    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
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
        for document in request.FILES.getlist('documents') :
            documents.append((document.file, document.name))
        results = self.storage.upload_documents(id, documents)
        # TODO: handle upload failures
        return Response(results, status=status.HTTP_200_OK)
