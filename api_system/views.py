from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Worker
from .serializers import WorkersSerializer

class WorkerListView(APIView):

    def get(self, request, *args, **kwargs):
            workers = Worker.objects.all()
            serializer = WorkersSerializer(workers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
