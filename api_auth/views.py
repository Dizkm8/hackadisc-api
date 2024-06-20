# from rest_framework import generics
# from .models import Worker
# from

# class WorkerListView(generics.ListAPIView):
#     queryset = Worker.objects.all()
#     serializer_class = WorkerSerializer

#     def get_queryset(self):
#         state_param = self.request.query_params.get('state')
#         if state_param:
#             self.queryset = self.queryset.filter(state=state_param)

#         rating_param = self.request.query_params.get('rating')
#         if rating_param:
#             self.queryset = self.queryset.filter(rating__gte=rating_param)

#         post_param = self.request.query_params.get('post')
#         if post_param:
#             self.queryset = self.queryset.filter(post=post_param)

#         area_param = self.request.query_params.get('area')
#         if area_param:
#             self.queryset = self.queryset.filter(area=area_param)

#         return self.queryset
