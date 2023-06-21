import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGroupBox, QProgressBar
from PyQt5.QtCore import QTimer
import psutil
import platform

def get_size(bytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while bytes >= 1024 and i < len(suffixes) - 1:
        bytes /= 1024
        i += 1
    return f"{bytes:.2f} {suffixes[i]}"

class SystemMonitor(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.system_group = QGroupBox("System Information")
        self.cpu_group = QGroupBox("CPU Information")
        self.memory_group = QGroupBox("Memory Information")

        self.layout.addWidget(self.system_group)
        self.layout.addWidget(self.cpu_group)
        self.layout.addWidget(self.memory_group)

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

        vbox3 = QVBoxLayout()
        vbox3.addWidget(self.memory_info)
        self.memory_group.setLayout(vbox3)
        self.setLayout(self.layout)
        self.update_info()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)

    def update_info(self):
        # System Info
        uname = platform.uname()
        svmem = psutil.virtual_memory()
        self.system_info.setText(f"System: {uname.system}\nNode Name: {uname.node}\nRelease: {uname.release}\nVersion: {uname.version}\nMachine: {uname.machine}\nProcessor: {uname.processor}")
        
        # CPU Info
        cpu_percent = int(psutil.cpu_percent(interval=1))
        cpu_info_text = f"Physical cores: {psutil.cpu_count(logical=False)}\nTotal cores: {psutil.cpu_count(logical=True)}"
        cpufreq = psutil.cpu_freq()
        cpu_info_text += f"\nMax Frequency: {cpufreq.max:.2f}Mhz\nMin Frequency: {cpufreq.min:.2f}Mhz\nCurrent Frequency: {cpufreq.current:.2f}Mhz"
        cpu_info_text += "\nCPU Usage Per Core:"
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            cpu_info_text += f"\nCore {i}: {percentage}%"
        cpu_info_text += f"\nTotal CPU Usage: {psutil.cpu_percent(interval=1)}%"
        self.cpu_info.setText(cpu_info_text)
        self.cpu_usage.setValue(cpu_percent)
        
        # Memory Info
        memory_info_text = f"Total: {get_size(svmem.total)}\nAvailable: {get_size(svmem.available)}\nUsed: {get_size(svmem.used)}\nPercentage: {svmem.percent}%"
        swap = psutil.swap_memory()
        memory_info_text += f"\n\nSWAP\nTotal: {get_size(swap.total)}\nFree: {get_size(swap.free)}\nUsed: {get_size(swap.used)}\nPercentage: {swap.percent}%"
        self.memory_info.setText(memory_info_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SystemMonitor()
    widget.show()
    sys.exit(app.exec_())
