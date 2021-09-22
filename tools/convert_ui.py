import os
import sys
import subprocess

ENV = {
    "win32": "E:/Program Files/Python38/python3.exe",
    "darwin": "/usr/local/Cellar/python@3.9/3.9.2_1/bin/python3.9"
}

print("Start.")
project_path = os.path.join(sys.path[0], "..")
for ui in os.listdir(project_path):
    if ui.endswith(".ui"):
        ui_path = os.path.join(project_path, ui)
        py = ui.replace(".ui", ".py")
        py_path = os.path.join(project_path, py)
        print("ui={0} name={1}".format(ui, py))
        cmd = "{0} -m PyQt5.uic.pyuic {1} -o {2}".format(ENV[sys.platform], ui_path, py_path)
        process = subprocess.Popen(cmd)
        process.wait()
print("Done.")
