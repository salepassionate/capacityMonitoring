# monitoring/serializers.py

from rest_framework import serializers
from .models import (
    ServerMetric, AssetInfo, OSInfo, SystemInfo, CPUInfo, MemoryInfo,
    DiskInfo, NetworkInterfaceInfo, VirtualizationInfo, WindowsUpdate, # Added WindowsUpdate
    MetricData, DiskUsageMetric, MemoryUsageMetric, CPULoadMetric,
    NetworkUsageMetric, TopProcessesMetric, ProcessDetail, TopDiskConsumerMetric
)

# --- Asset Information Serializers ---

class OSInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OSInfo
        exclude = ['id', 'asset_info'] # Exclude primary key and foreign key for nested serialization

class SystemInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemInfo
        exclude = ['id', 'asset_info']
        # Add the new fields here
        fields = (
            'manufacturer', 'product_name', 'serial_number', 'bios_version',
            'chassis_type', 'uptime_initial', 'last_update_check_time',
            'pending_updates_count'
        )

class CPUInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPUInfo
        exclude = ['id', 'asset_info']

class MemoryInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryInfo
        exclude = ['id', 'asset_info']

class DiskInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiskInfo
        exclude = ['id', 'asset_info'] # Exclude primary key and foreign key
        # 'fields' = '__all__' would also work if you want to include the FK for creation,
        # but we handle it via the parent serializer's create method.

class NetworkInterfaceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkInterfaceInfo
        exclude = ['id', 'asset_info']

class VirtualizationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualizationInfo
        exclude = ['id', 'asset_info']

class WindowsUpdateSerializer(serializers.ModelSerializer): # NEW Serializer for Windows Updates
    class Meta:
        model = WindowsUpdate
        exclude = ['id', 'asset_info'] # Exclude primary key and foreign key

class AssetInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for AssetInfo, including nested serializers for its related one-to-one fields
    and many-to-one fields (disks, network_interfaces, windows_updates).
    """
    os = OSInfoSerializer()
    system = SystemInfoSerializer()
    cpu = CPUInfoSerializer()
    memory = MemoryInfoSerializer()
    virtualization = VirtualizationInfoSerializer()
    disks = DiskInfoSerializer(many=True, required=False) # 'many=True' for a list of objects
    network_interfaces = NetworkInterfaceInfoSerializer(many=True, required=False)
    windows_updates = WindowsUpdateSerializer(many=True, required=False) # NEW: Optional for Linux systems

    class Meta:
        model = AssetInfo
        exclude = ['id', 'server_metric'] # Exclude primary key and foreign key

    def create(self, validated_data):
        # Handle nested creation for one-to-one relationships
        os_data = validated_data.pop('os')
        system_data = validated_data.pop('system')
        cpu_data = validated_data.pop('cpu')
        memory_data = validated_data.pop('memory')
        virtualization_data = validated_data.pop('virtualization')

        # Handle nested creation for many-to-one relationships (lists)
        # Use .pop(key, []) to handle cases where the list might be empty or missing in the incoming JSON
        disks_data = validated_data.pop('disks', [])
        network_interfaces_data = validated_data.pop('network_interfaces', [])
        windows_updates_data = validated_data.pop('windows_updates', []) # NEW: Pop with default empty list

        asset_info = AssetInfo.objects.create(**validated_data)

        OSInfo.objects.create(asset_info=asset_info, **os_data)
        SystemInfo.objects.create(asset_info=asset_info, **system_data)
        CPUInfo.objects.create(asset_info=asset_info, **cpu_data)
        MemoryInfo.objects.create(asset_info=asset_info, **memory_data)
        VirtualizationInfo.objects.create(asset_info=asset_info, **virtualization_data)

        for disk_data in disks_data:
            DiskInfo.objects.create(asset_info=asset_info, **disk_data)
        for net_if_data in network_interfaces_data:
            NetworkInterfaceInfo.objects.create(asset_info=asset_info, **net_if_data)
        for update_data in windows_updates_data: # NEW: Create WindowsUpdate instances
            WindowsUpdate.objects.create(asset_info=asset_info, **update_data)

        return asset_info

# --- Metric Data Serializers ---

class DiskUsageMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiskUsageMetric
        exclude = ['id', 'metrics_data']

class MemoryUsageMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryUsageMetric
        exclude = ['id', 'metrics_data']

class CPULoadMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPULoadMetric
        exclude = ['id', 'metrics_data']

class NetworkUsageMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkUsageMetric
        exclude = ['id', 'metrics_data']

class ProcessDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessDetail
        exclude = ['id', 'top_processes_metric']

class TopProcessesMetricSerializer(serializers.ModelSerializer):
    """
    Serializer for TopProcessesMetric, handling the 'by_cpu' and 'by_memory' lists
    by creating ProcessDetail instances with a 'process_type' field.
    """
    # These fields are not directly on the model but are used for incoming data
    by_cpu = ProcessDetailSerializer(many=True, required=False, write_only=True)
    by_memory = ProcessDetailSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = TopProcessesMetric
        exclude = ['id', 'metrics_data']

    def create(self, validated_data):
        # Pop the lists of processes, as they are not direct model fields
        by_cpu_data = validated_data.pop('by_cpu', [])
        by_memory_data = validated_data.pop('by_memory', [])

        top_processes_metric = TopProcessesMetric.objects.create(**validated_data)

        # Create ProcessDetail instances for CPU-bound processes
        for process_data in by_cpu_data:
            ProcessDetail.objects.create(
                top_processes_metric=top_processes_metric,
                process_type='cpu',
                **process_data
            )
        # Create ProcessDetail instances for Memory-bound processes
        for process_data in by_memory_data:
            ProcessDetail.objects.create(
                top_processes_metric=top_processes_metric,
                process_type='memory',
                **process_data
            )
        return top_processes_metric

class TopDiskConsumerMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopDiskConsumerMetric
        exclude = ['id', 'metrics_data']


class MetricDataSerializer(serializers.ModelSerializer):
    """
    Serializer for MetricData, including nested serializers for its related one-to-one fields
    and many-to-one fields (disk_usage, top_disk_consumers).
    """
    memory_usage = MemoryUsageMetricSerializer()
    cpu_load = CPULoadMetricSerializer()
    network_usage = NetworkUsageMetricSerializer()
    top_processes = TopProcessesMetricSerializer()
    disk_usage = DiskUsageMetricSerializer(many=True, required=False)
    top_disk_consumers = TopDiskConsumerMetricSerializer(many=True, required=False)

    class Meta:
        model = MetricData
        exclude = ['id', 'server_metric']

    def create(self, validated_data):
        # Handle nested creation for one-to-one relationships
        memory_usage_data = validated_data.pop('memory_usage')
        cpu_load_data = validated_data.pop('cpu_load')
        network_usage_data = validated_data.pop('network_usage')
        top_processes_data = validated_data.pop('top_processes')

        # Handle nested creation for many-to-one relationships (lists)
        disk_usage_data = validated_data.pop('disk_usage', [])
        top_disk_consumers_data = validated_data.pop('top_disk_consumers', [])

        metrics_data = MetricData.objects.create(**validated_data)

        MemoryUsageMetric.objects.create(metrics_data=metrics_data, **memory_usage_data)
        CPULoadMetric.objects.create(metrics_data=metrics_data, **cpu_load_data)
        NetworkUsageMetric.objects.create(metrics_data=metrics_data, **network_usage_data)
        TopProcessesMetric.objects.create(metrics_data=metrics_data, **top_processes_data)

        for du_data in disk_usage_data:
            DiskUsageMetric.objects.create(metrics_data=metrics_data, **du_data)
        for tdc_data in top_disk_consumers_data:
            TopDiskConsumerMetric.objects.create(metrics_data=metrics_data, **tdc_data)

        return metrics_data


class ServerMetricSerializer(serializers.ModelSerializer):
    """
    Main serializer for ServerMetric, handling the entire nested structure.
    """
    asset_info = AssetInfoSerializer()
    metrics = MetricDataSerializer(source='metrics_data') # Map 'metrics' JSON key to 'metrics_data' model field

    class Meta:
        model = ServerMetric
        fields = '__all__' # Include all fields from ServerMetric and its nested relations

    def create(self, validated_data):
        # Pop nested data to handle separately
        asset_info_data = validated_data.pop('asset_info')
        metrics_data = validated_data.pop('metrics_data') # Note: this was 'metrics' in JSON, mapped to 'metrics_data'

        # Create the main ServerMetric instance
        server_metric = ServerMetric.objects.create(**validated_data)

        # Create nested AssetInfo and MetricData instances
        # Pass the created server_metric instance to the nested serializer's create method
        asset_info_serializer = AssetInfoSerializer(data=asset_info_data)
        asset_info_serializer.is_valid(raise_exception=True)
        asset_info_serializer.create(asset_info_serializer.validated_data, server_metric=server_metric)

        metrics_data_serializer = MetricDataSerializer(data=metrics_data)
        metrics_data_serializer.is_valid(raise_exception=True)
        metrics_data_serializer.create(metrics_data_serializer.validated_data, server_metric=server_metric)

        return server_metric
