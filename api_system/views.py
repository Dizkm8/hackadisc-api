from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Worker, Intervention
from .serializers import WorkerFilterSerializer, DocumentSerializer, FileSerializer
from .services.FirebaseService import FirebaseService

class WorkerListView(APIView):

    def post(self, request):
        serializer = WorkerFilterSerializer(data=request.data)
        
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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