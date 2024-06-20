from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Worker
from .serializers import WorkersSerializer, WorkerDetailSerializer
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10  # Número de elementos por página
    page_size_query_param = 'page_size'
    max_page_size = 100
    
class WorkerListView(APIView):
    def get(self, request, *args, **kwargs):
        workers = Worker.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Puedes ajustar este valor o usar el paginador personalizado
        paginated_workers = paginator.paginate_queryset(workers, request)
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
