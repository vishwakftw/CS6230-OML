import os
import subprocess
import numpy as np

functions = ['B1', 'B2', 'B3', 'BL', 'RB']
optims = ['GD', 'CM', 'Adam', 'Adagrad', 'RMSprop']

for i in functions:
    for j in optims:
        subprocess.call(["python3", "main.py", "--optim", j, "--fn", i]) 

best_files = open('best_values.txt', 'w')
for directory_1 in functions:
    for directory_2 in optims:
        data = []
        file_list = os.listdir(directory_1+'/'+directory_2)
        file_list = list(filter(lambda x: x.find('log') != -1, file_list))
        for filename in file_list:
            filepath = directory_1 +'/'+ directory_2 +'/'+ filename
            data.append(np.genfromtxt(filepath)[-1,1])
        print(directory_1, directory_2, file_list[np.argsort(data)[0]])
        best_files.write('{0}\t{1}\t{2}\n'.format(directory_1, directory_2, file_list[np.argsort(data)[0]][4:-7]))
best_files.close()
