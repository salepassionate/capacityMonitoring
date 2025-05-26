# monitoring/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny # Consider stricter permissions for production

from .models import ServerMetric, AssetInfo, WindowsUpdate
from .serializers import ServerMetricSerializer, AssetInfoSerializer, WindowsUpdateSerializer

# Import your filters (assuming you followed the django-filter setup)
from .filters import ServerMetricFilter, AssetInfoFilter, WindowsUpdateFilter
# If you didn't set DEFAULT_FILTER_BACKENDS globally in settings.py,
# you'll need to import it here:
# from django_filters.rest_framework import DjangoFilterBackend


class ServerMetricViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Server Metrics to be viewed or created.
    This is the primary endpoint for receiving data from your monitoring scripts.
    """
    queryset = ServerMetric.objects.all().order_by('-timestamp') # Order by most recent first
    serializer_class = ServerMetricSerializer
    permission_classes = [AllowAny] # For simplicity during development. Adjust for production!
    filterset_class = ServerMetricFilter # Enable filtering for this ViewSet

    # You might want to override create to handle potential idempotency or custom logic
    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AssetInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Asset Information to be viewed.
    Data for AssetInfo is typically created via the ServerMetric endpoint.
    """
    queryset = AssetInfo.objects.all().prefetch_related(
        'os', 'system', 'cpu', 'memory', 'virtualization',
        'disks', 'network_interfaces', 'windows_updates' # Ensure all related fields are prefetched for efficiency
    ).order_by('server_metric__hostname') # Order for consistent viewing
    serializer_class = AssetInfoSerializer
    permission_classes = [AllowAny]
    filterset_class = AssetInfoFilter # Enable filtering for this ViewSet


class WindowsUpdateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Windows Update History to be viewed.
    Data for Windows Updates is typically created via the ServerMetric endpoint.
    """
    queryset = WindowsUpdate.objects.all().order_by('-installed_on', 'asset_info__server_metric__hostname')
    serializer_class = WindowsUpdateSerializer
    permission_classes = [AllowAny]
    filterset_class = WindowsUpdateFilter # Enable filtering for this ViewSet
