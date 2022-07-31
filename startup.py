import subprocess
commands = ['sudo pigpiod', 'cd Drone ; ./mavproxysetup.sh', 'cd Drone ; python droneConsumer.py']
n = 3 #the number of parallel processes you want
for j in range(max(int(len(commands)/n), 1)):
    procs = [subprocess.Popen(i, shell=True) for i in commands[j*n: min((j+1)*n, len(commands))] ]
    for p in procs:
        p.wait()
