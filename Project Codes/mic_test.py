import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import rfft, irfft


# set duration and start recording
fs = 44100
duration = 2  # seconds
myrecording = sd.rec(duration * fs, samplerate=fs, channels=2, blocking=True)

# collect output
y1 = abs(myrecording[:,0])
y2 = myrecording[:,1]

# calculate avg
y1_avg = np.average(y1)
print("avg = " +str(y1_avg))

# compute fft, apply band pass filter, then ifft
y1_fft = rfft(y1)
ylen = len(y1_fft)
y1_fft = [0]*int(0.1*ylen) + list(y1_fft[int(0.1*ylen):int(0.9*ylen)]) + [0]*int(0.1*ylen)
y1_hp = abs(irfft(y1_fft))

y1_hp_avg = np.average(y1_hp)

# detect frequency
counter = 0
for i in range (len(y1_hp)):
	if (y1_hp[i] > (50 * y1_hp_avg)):
		counter = counter + 1
	if (counter > 2):
		print("detected")
		break



# plt.plot(y1, linestyle = 'dotted', label='original')
plt.plot(y1_hp, linestyle = 'dotted', label='highpass')
# plt.plot(y2, linestyle = 'dotted')
plt.legend()
plt.show()
