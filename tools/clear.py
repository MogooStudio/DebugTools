import os

DELETE_FILES = ['dist', 'build', 'hummerUpdate', 'DebugTools.spec']

delete_files = []
for filename in DELETE_FILES:
    filename = "../" + filename
    print(filename)
    delete_files.append(filename)

os.system('rm -rf ' + ' '.join(delete_files))
print("delete end")
