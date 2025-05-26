# monitoring/models.py

from django.db import models

class ServerMetric(models.Model):
    """
    Main model representing a single metric collection from a server.
    It links to asset information and various performance metrics.
    """
    timestamp = models.DateTimeField(help_text="Timestamp of the metric collection (UTC).")
    hostname = models.CharField(max_length=255, help_text="Hostname of the server.")

    def __str__(self):
        return f"{self.hostname} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        verbose_name = "Server Metric"
        verbose_name_plural = "Server Metrics"
        ordering = ['-timestamp'] # Order by most recent first


class AssetInfo(models.Model):
    """
    Static asset information about the server.
    One-to-one relationship with ServerMetric.
    """
    server_metric = models.OneToOneField(
        ServerMetric,
        on_delete=models.CASCADE,
        related_name='asset_info',
        help_text="The server metric entry this asset information belongs to."
    )
    hostname = models.CharField(max_length=255, help_text="Hostname from asset info (redundant but kept for structure).")

    def __str__(self):
        return f"Asset Info for {self.server_metric.hostname}"

    class Meta:
        verbose_name = "Asset Information"
        verbose_name_plural = "Asset Information"


class OSInfo(models.Model):
    """Operating System details."""
    asset_info = models.OneToOneField(
        AssetInfo,
        on_delete=models.CASCADE,
        related_name='os',
        help_text="The asset information entry this OS info belongs to."
    )
    pretty_name = models.CharField(max_length=255, blank=True, help_text="Human-readable OS name.")
    kernel_version = models.CharField(max_length=255, blank=True, help_text="OS kernel version.")

    def __str__(self):
        return f"{self.pretty_name} ({self.kernel_version})"

    class Meta:
        verbose_name = "OS Information"
        verbose_name_plural = "OS Information"


class SystemInfo(models.Model):
    """System hardware details."""
    asset_info = models.OneToOneField(
        AssetInfo,
        on_delete=models.CASCADE,
        related_name='system',
        help_text="The asset information entry this system info belongs to."
    )
    manufacturer = models.CharField(max_length=255, blank=True, help_text="System manufacturer.")
    product_name = models.CharField(max_length=255, blank=True, help_text="System product name/model.")
    serial_number = models.CharField(max_length=255, blank=True, help_text="System serial number.")
    bios_version = models.CharField(max_length=255, blank=True, help_text="BIOS/UEFI version.")
    chassis_type = models.CharField(max_length=255, blank=True, help_text="Chassis type (e.g., 'Laptop', 'Desktop').")
    uptime_initial = models.CharField(max_length=255, blank=True, help_text="Initial system uptime at script start.")

    def __str__(self):
        return f"{self.manufacturer} {self.product_name}"

    class Meta:
        verbose_name = "System Information"
        verbose_name_plural = "System Information"


class CPUInfo(models.Model):
    """CPU details."""
    asset_info = models.OneToOneField(
        AssetInfo,
        on_delete=models.CASCADE,
        related_name='cpu',
        help_text="The asset information entry this CPU info belongs to."
    )
    model_name = models.CharField(max_length=255, blank=True, help_text="CPU model name.")
    vendor_id = models.CharField(max_length=255, blank=True, help_text="CPU vendor ID.")
    total_logical_cpus = models.IntegerField(default=0, help_text="Total number of logical CPUs/threads.")
    physical_cores_per_socket = models.IntegerField(default=0, help_text="Physical cores per CPU socket.")
    architecture = models.CharField(max_length=50, blank=True, help_text="CPU architecture (e.g., x86_64).")

    def __str__(self):
        return f"{self.model_name} ({self.total_logical_cpus} threads)"

    class Meta:
        verbose_name = "CPU Information"
        verbose_name_plural = "CPU Information"


class MemoryInfo(models.Model):
    """Memory (RAM) details."""
    asset_info = models.OneToOneField(
        AssetInfo,
        on_delete=models.CASCADE,
        related_name='memory',
        help_text="The asset information entry this memory info belongs to."
    )
    total_mb = models.IntegerField(default=0, help_text="Total installed RAM in MB.")
    speed = models.CharField(max_length=100, blank=True, help_text="Memory speed (e.g., '2400 MHz').")
    modules_count = models.IntegerField(default=0, help_text="Number of installed RAM modules.")

    def __str__(self):
        return f"{self.total_mb}MB"

    class Meta:
        verbose_name = "Memory Information"
        verbose_name_plural = "Memory Information"


class DiskInfo(models.Model):
    """Details for an individual disk."""
    asset_info = models.ForeignKey(
        AssetInfo,
        on_delete=models.CASCADE,
        related_name='disks',
        help_text="The asset information entry this disk belongs to."
    )
    name = models.CharField(max_length=50, help_text="Disk device name (e.g., 'sda').")
    size = models.CharField(max_length=50, help_text="Disk size (e.g., '256G').")
    model = models.CharField(max_length=255, blank=True, help_text="Disk model.")
    serial = models.CharField(max_length=255, blank=True, help_text="Disk serial number.")

    def __str__(self):
        return f"{self.name} ({self.size})"

    class Meta:
        verbose_name = "Disk Information"
        verbose_name_plural = "Disk Information"
        unique_together = ('asset_info', 'name') # A disk name should be unique per asset info


class NetworkInterfaceInfo(models.Model):
    """Details for an individual network interface."""
    asset_info = models.ForeignKey(
        AssetInfo,
        on_delete=models.CASCADE,
        related_name='network_interfaces',
        help_text="The asset information entry this network interface belongs to."
    )
    name = models.CharField(max_length=50, help_text="Interface name (e.g., 'eth0', 'ens192').")
    mac_address = models.CharField(max_length=17, blank=True, help_text="MAC address.")
    ipv4_address = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True, help_text="IPv4 address.")
    ipv6_address = models.GenericIPAddressField(protocol='IPv6', null=True, blank=True, help_text="IPv6 address.")

    def __str__(self):
        return f"{self.name} ({self.ipv4_address})"

    class Meta:
        verbose_name = "Network Interface Information"
        verbose_name_plural = "Network Interface Information"
        unique_together = ('asset_info', 'name') # An interface name should be unique per asset info


class VirtualizationInfo(models.Model):
    """Virtualization details."""
    asset_info = models.OneToOneField(
        AssetInfo,
        on_delete=models.CASCADE,
        related_name='virtualization',
        help_text="The asset information entry this virtualization info belongs to."
    )
    is_vm = models.BooleanField(default=False, help_text="True if the system is a virtual machine.")
    hypervisor = models.CharField(max_length=100, blank=True, help_text="Name of the hypervisor if it's a VM.")

    def __str__(self):
        return f"VM: {self.is_vm}, Hypervisor: {self.hypervisor}"

    class Meta:
        verbose_name = "Virtualization Information"
        verbose_name_plural = "Virtualization Information"


class MetricData(models.Model):
    """
    Container for various performance metrics.
    One-to-one relationship with ServerMetric.
    """
    server_metric = models.OneToOneField(
        ServerMetric,
        on_delete=models.CASCADE,
        related_name='metrics_data',
        help_text="The server metric entry this performance data belongs to."
    )

    def __str__(self):
        return f"Metrics for {self.server_metric.hostname}"

    class Meta:
        verbose_name = "Metric Data"
        verbose_name_plural = "Metric Data"


class DiskUsageMetric(models.Model):
    """Disk usage for a specific filesystem."""
    metrics_data = models.ForeignKey(
        MetricData,
        on_delete=models.CASCADE,
        related_name='disk_usage',
        help_text="The metric data entry this disk usage belongs to."
    )
    filesystem = models.CharField(max_length=255, help_text="Filesystem path (e.g., '/dev/sda2').")
    percentage_used = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage of disk used.")
    total_size = models.CharField(max_length=50, help_text="Total size of the filesystem (e.g., '512M').")
    used_size = models.CharField(max_length=50, help_text="Used size of the filesystem.")
    available_size = models.CharField(max_length=50, help_text="Available size of the filesystem.")

    def __str__(self):
        return f"{self.filesystem} - {self.percentage_used}%"

    class Meta:
        verbose_name = "Disk Usage Metric"
        verbose_name_plural = "Disk Usage Metrics"
        unique_together = ('metrics_data', 'filesystem')


class MemoryUsageMetric(models.Model):
    """Memory usage metrics."""
    metrics_data = models.OneToOneField(
        MetricData,
        on_delete=models.CASCADE,
        related_name='memory_usage',
        help_text="The metric data entry this memory usage belongs to."
    )
    total_mb = models.IntegerField(help_text="Total memory in MB.")
    used_mb = models.IntegerField(help_text="Used memory in MB.")
    free_mb = models.IntegerField(help_text="Free memory in MB.")
    available_mb = models.IntegerField(help_text="Available memory in MB.")
    percentage_used = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage of memory used.")

    def __str__(self):
        return f"{self.used_mb}MB used ({self.percentage_used}%)"

    class Meta:
        verbose_name = "Memory Usage Metric"
        verbose_name_plural = "Memory Usage Metrics"


class CPULoadMetric(models.Model):
    """CPU load average metrics."""
    metrics_data = models.OneToOneField(
        MetricData,
        on_delete=models.CASCADE,
        related_name='cpu_load',
        help_text="The metric data entry this CPU load belongs to."
    )
    load_1min = models.DecimalField(max_digits=5, decimal_places=2, help_text="CPU load average over 1 minute.")
    load_5min = models.DecimalField(max_digits=5, decimal_places=2, help_text="CPU load average over 5 minutes.")
    load_15min = models.DecimalField(max_digits=5, decimal_places=2, help_text="CPU load average over 15 minutes.")

    def __str__(self):
        return f"Load: {self.load_1min}, {self.load_5min}, {self.load_15min}"

    class Meta:
        verbose_name = "CPU Load Metric"
        verbose_name_plural = "CPU Load Metrics"


class NetworkUsageMetric(models.Model):
    """Network bandwidth usage metrics."""
    metrics_data = models.OneToOneField(
        MetricData,
        on_delete=models.CASCADE,
        related_name='network_usage',
        help_text="The metric data entry this network usage belongs to."
    )
    received_bps = models.DecimalField(max_digits=15, decimal_places=2, help_text="Received bytes per second.")
    transmitted_bps = models.DecimalField(max_digits=15, decimal_places=2, help_text="Transmitted bytes per second.")

    def __str__(self):
        return f"RX: {self.received_bps} Bps, TX: {self.transmitted_bps} Bps"

    class Meta:
        verbose_name = "Network Usage Metric"
        verbose_name_plural = "Network Usage Metrics"


class TopProcessesMetric(models.Model):
    """Container for top processes by CPU and Memory."""
    metrics_data = models.OneToOneField(
        MetricData,
        on_delete=models.CASCADE,
        related_name='top_processes',
        help_text="The metric data entry this top processes info belongs to."
    )

    def __str__(self):
        return f"Top Processes for {self.metrics_data.server_metric.hostname}"

    class Meta:
        verbose_name = "Top Processes Metric"
        verbose_name_plural = "Top Processes Metrics"


class ProcessDetail(models.Model):
    """Details for an individual top process."""
    PROCESS_TYPE_CHOICES = [
        ('cpu', 'By CPU'),
        ('memory', 'By Memory'),
    ]
    top_processes_metric = models.ForeignKey(
        TopProcessesMetric,
        on_delete=models.CASCADE,
        related_name='processes', # Generic name, will filter by 'type'
        help_text="The top processes metric entry this process detail belongs to."
    )
    process_type = models.CharField(max_length=10, choices=PROCESS_TYPE_CHOICES, help_text="Type of top process (CPU or Memory).")
    pid = models.IntegerField(help_text="Process ID.")
    user = models.CharField(max_length=255, help_text="User running the process.")
    cpu_percent = models.DecimalField(max_digits=5, decimal_places=2, help_text="CPU usage percentage.")
    mem_percent = models.DecimalField(max_digits=5, decimal_places=2, help_text="Memory usage percentage.")
    command = models.TextField(help_text="Full command of the process.")

    def __str__(self):
        return f"PID {self.pid} ({self.process_type}) - {self.command[:50]}..."

    class Meta:
        verbose_name = "Process Detail"
        verbose_name_plural = "Process Details"
        # Can't use unique_together easily due to dynamic nature,
        # but combination of (top_processes_metric, process_type, pid) would be logical if needed.


class TopDiskConsumerMetric(models.Model):
    """Details for an individual top disk space consuming directory."""
    metrics_data = models.ForeignKey(
        MetricData,
        on_delete=models.CASCADE,
        related_name='top_disk_consumers',
        help_text="The metric data entry this top disk consumer belongs to."
    )
    size = models.CharField(max_length=50, help_text="Size of the directory/file (e.g., '103G').")
    path = models.CharField(max_length=1024, help_text="Path of the directory/file.")

    def __str__(self):
        return f"{self.path} - {self.size}"

    class Meta:
        verbose_name = "Top Disk Consumer Metric"
        verbose_name_plural = "Top Disk Consumer Metrics"
        unique_together = ('metrics_data', 'path')
