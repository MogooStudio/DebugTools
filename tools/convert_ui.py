import os
import sys

project_path = os.path.join(sys.path[0], "..")
for ui in os.listdir(project_path):
    if ui.endswith(".ui"):
        ui_path = os.path.join(project_path, ui)
        py = ui.replace(".ui", ".py")
        py_path = os.path.join(project_path, py)
        print("ui={0} name={1}".format(ui, py))
        cmd = "/usr/local/Cellar/python@3.9/3.9.2_1/bin/python3.9 -m PyQt5.uic.pyuic {0} -o {1}".format(ui_path, py_path)
        os.system(cmd)
print("ui全部转换完毕")
