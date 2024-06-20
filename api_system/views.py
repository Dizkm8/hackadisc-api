from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Worker
from .serializers import WorkerFilterSerializer

class WorkerListView(APIView):

    def post(self, request):
        serializer = WorkerFilterSerializer(data=request.data)
        
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
