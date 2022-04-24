import os
import sys
import subprocess

if os.path.isfile("local.py"):
    from local import *

MAC = sys.platform == "darwin"
program = ENV[sys.platform]
if not program or program == "" or not os.path.exists(program):
    raise Exception("error: ENV configuration error")

print("Start.")
project_path = os.path.join(sys.path[0], "..")
for ui in os.listdir(project_path):
    if ui.endswith(".ui"):
        ui_path = os.path.join(project_path, ui)
        py = ui.replace(".ui", ".py")
        py_path = os.path.join(project_path, py)
        print("ui={0} name={1}".format(ui, py))
        cmd = "{0} -m PyQt5.uic.pyuic {1} -o {2}".format(program, ui_path, py_path)
        process = subprocess.Popen(cmd, shell=MAC)
        process.wait()
print("Done.")
