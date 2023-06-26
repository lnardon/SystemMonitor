import sys
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QProgressBar,
)
from PyQt5.QtCore import QTimer
import psutil
import platform
import pynvml as nvml


def get_size(bytes):
    suffixes = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while bytes >= 1024 and i < len(suffixes) - 1:
        bytes /= 1024
        i += 1
    return f"{bytes:.2f} {suffixes[i]}"


class SystemMonitor(QWidget):
    def __init__(self):
        super().__init__()
        # self.setWindowIcon(QIcon("./icon.png"))

        # Layout
        self.layout = QVBoxLayout()
        self.system_group = QGroupBox("System Information")
        self.cpu_group = QGroupBox("CPU Information")
        self.memory_group = QGroupBox("Memory Information")
        self.gpu_group = QGroupBox("GPU Information")
        self.layout.addWidget(self.system_group)
        self.layout.addWidget(self.cpu_group)
        self.layout.addWidget(self.memory_group)
        self.layout.addWidget(self.gpu_group)

        # System Info and CPU Info
        self.system_info = QLabel()
        self.cpu_info = QLabel()
        self.cpu_usage = QProgressBar()
        self.cpu_usage.setMaximum(100)
        self.memory_info = QLabel()
        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.system_info)
        self.system_group.setLayout(vbox1)
        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.cpu_info)
        vbox2.addWidget(self.cpu_usage)
        self.cpu_group.setLayout(vbox2)

        # Memory Info
        vbox3 = QVBoxLayout()
        vbox3.addWidget(self.memory_info)
        self.ram_usage = QProgressBar()
        self.ram_usage.setMaximum(100)
        vbox3.addWidget(self.ram_usage)
        self.memory_group.setLayout(vbox3)
        self.setLayout(self.layout)

        # GPU Info
        nvml.nvmlInit()
        self.gpu_device = nvml.nvmlDeviceGetHandleByIndex(0)
        self.gpu_util_progress = QProgressBar()
        self.gpu_util_progress.setMaximum(100)
        self.gpu_mem_progress = QProgressBar()
        self.gpu_mem_progress.setMaximum(100)
        self.gpu_temp_info = QLabel()

        vbox4 = QVBoxLayout()
        vbox4.addWidget(self.gpu_temp_info)
        vbox4.addWidget(QLabel("Usage:"))
        vbox4.addWidget(self.gpu_util_progress)
        vbox4.addWidget(QLabel("Memory usage:"))
        vbox4.addWidget(self.gpu_mem_progress)
        self.gpu_group.setLayout(vbox4)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        self.timer.start(3000)

    def update_info(self):
        # System Info
        uname = platform.uname()
        svmem = psutil.virtual_memory()
        self.system_info.setText(
            f"System: {uname.system}\nNode Name: {uname.node}\nRelease: {uname.release}\nVersion: {uname.version}\nProcessor: {uname.processor}"
        )

        # CPU Info
        cpu_percent = int(psutil.cpu_percent(interval=1))
        cpu_info_text = f"Physical cores: {psutil.cpu_count(logical=False)} | Total cores: {psutil.cpu_count(logical=True)}"
        cpufreq = psutil.cpu_freq()
        cpu_info_text += f"\nFrequency Range: {cpufreq.min:.2f}Mhz - {cpufreq.max:.2f}Mhz \nCurrent Frequency: {cpufreq.current:.2f}Mhz"
        cpu_info_text += "\n\nCPU Usage Per Core:"
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            cpu_info_text += f"\nCore {i}: {percentage}%"
        cpu_info_text += f"\n\nTotal CPU Usage: {cpu_percent}%"
        self.cpu_info.setText(cpu_info_text)
        self.cpu_usage.setValue(cpu_percent)

        # Memory Info
        memory_info_text = f"Total: {get_size(svmem.total)} | Available: {get_size(svmem.available)} | Used: {get_size(svmem.used)}"
        self.ram_usage.setValue(int(svmem.percent))
        self.memory_info.setText(memory_info_text)

        # GPU Info
        gpu_util = nvml.nvmlDeviceGetUtilizationRates(self.gpu_device)
        gpu_temp = nvml.nvmlDeviceGetTemperature(
            self.gpu_device, nvml.NVML_TEMPERATURE_GPU
        )
        self.gpu_temp_info.setText(f"GPU Temperature: {gpu_temp} C \n")
        self.gpu_util_progress.setValue(gpu_util.gpu)
        self.gpu_mem_progress.setValue(gpu_util.memory)

    def __del__(self):
        nvml.nvmlShutdown()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SystemMonitor()
    widget.show()
    sys.exit(app.exec_())
