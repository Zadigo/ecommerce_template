from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shop import models


class BaseAPIView(APIView):
    authentication_classes = []
    permission_classes = []

class ChartsView(BaseAPIView):
    def get(self, format=None, **kwargs):
        payments_by_month = models.CustomerOrder\
                            .statistics.payments_by_month()
        data = {
            "myChart": {
                'labels': payments_by_month[0],
                'data': payments_by_month[1]
            }
        }
        return Response(data=data[kwargs['name']])
