# monitoring/filters.py

import django_filters
from .models import ServerMetric, AssetInfo, WindowsUpdate # Import relevant models

class ServerMetricFilter(django_filters.FilterSet):
    # exact match for hostname
    hostname = django_filters.CharFilter(field_name='hostname', lookup_expr='iexact')
    # greater than or equal to timestamp
    timestamp_gte = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    # less than or equal to timestamp
    timestamp_lte = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')

    class Meta:
        model = ServerMetric
        # You can also just list fields directly without custom filter instances
        fields = ['hostname', 'timestamp'] # These will provide exact matches by default
        # If you define specific filters above, list them here if you want to include them in the meta fields
        # fields = {
        #     'hostname': ['exact', 'iexact'], # Example for multiple lookups
        #     'timestamp': ['exact', 'gte', 'lte'],
        # }

class AssetInfoFilter(django_filters.FilterSet):
    # Filter by OS name
    os_pretty_name = django_filters.CharFilter(field_name='os__pretty_name', lookup_expr='icontains')
    # Filter by System manufacturer
    system_manufacturer = django_filters.CharFilter(field_name='system__manufacturer', lookup_expr='icontains')
    # Filter by total memory greater than
    memory_total_mb_gte = django_filters.NumberFilter(field_name='memory__total_mb', lookup_expr='gte')
    # Filter by if it's a VM
    is_vm = django_filters.BooleanFilter(field_name='virtualization__is_vm')

    class Meta:
        model = AssetInfo
        # You can specify exact fields for filtering or use custom filters defined above
        fields = [
            'os__pretty_name',
            'system__manufacturer',
            'memory__total_mb',
            'virtualization__is_vm'
        ]

class WindowsUpdateFilter(django_filters.FilterSet):
    # Filter by KB ID (case-insensitive contains)
    kb_id = django_filters.CharFilter(field_name='kb_id', lookup_expr='icontains')
    # Filter by title (case-insensitive contains)
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    # Filter by installed on date (greater than or equal to)
    installed_on_gte = django_filters.DateTimeFilter(field_name='installed_on', lookup_expr='gte')
    # Filter by installed on date (less than or equal to)
    installed_on_lte = django_filters.DateTimeFilter(field_name='installed_on', lookup_expr='lte')

    class Meta:
        model = WindowsUpdate
        fields = [
            'kb_id',
            'title',
            'installed_on',
            'status'
      