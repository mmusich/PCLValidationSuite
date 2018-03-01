import numpy as np
import matplotlib.pyplot as plt

with open("RSS_ref.out") as f:
    data = f.read()

data = data.split('\n')

#print data

y = [row.split(' ')[0] for row in data]
x = range(1, len(y))
y.pop()
y = [float(i) / (1024*1024) for i in y]
print y
print len(x),len(y)

fig = plt.figure()

ax1 = fig.add_subplot(111)

ax1.set_title("RSS memory for wf 1001.0 step3")    
ax1.set_xlabel('time [s]')
ax1.set_ylabel('RSS [GB]')

ax1.plot(x,y, c='r', label='Reference')

leg = ax1.legend(loc="upper right", bbox_to_anchor=(0.4,0.8))

with open("RSS_mods.out") as f2:
    data2 = f2.read()

data2 = data2.split('\n')

#print data2

y2 = [row.split(' ')[0] for row in data2]
x2 = range(1, len(y2))
y2.pop()
y2 = [float(i) / (1024*1024) for i in y2]
print y2
print len(x2),len(y2)

ax2 = fig.add_subplot(111)
ax2.set_title("RSS memory for wf 1001.0 step3")    
ax2.set_xlabel('time [s]')
ax2.set_ylabel('RSS [GB]')

ax2.plot(x2,y2, c='b', label='This PR')

leg2 = ax2.legend(loc="upper right", bbox_to_anchor=(0.4,0.8))

plt.show()
fig.savefig('./memory.png')
