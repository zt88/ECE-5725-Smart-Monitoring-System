import threading
import argparse
import os,sys
import pickle

import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import rfft, irfft
import time
import datetime
import requests
import config


# set duration and start recording
fs = 44100
duration = 1  # seconds


def record(event_dict, args):
	# keeps recording audio and then perform FFT
	while True:
		if event_dict['stop'].is_set():
			break

		rec_start_time = time.time()
		rec_stop_time = rec_start_time + 0.9
		myrecording = sd.rec(duration * fs, samplerate=fs, channels=2, blocking=False)

		while time.time() < rec_stop_time:
			time.sleep(0)
		sd.wait()

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
				# send text
				message = '\U0001F50A loud sound detected'
				curr_time = datetime.datetime.now().strftime("%H:%M:%S %m/%d/%Y")
				resp = requests.post('https://textbelt.com/text', {
					'phone': config.PHONE,
					'message': message + " at " + curr_time,
					'key': config.KEY,
				})
				event_dict['capture'].set()
				capture = True
				with open('capture.tmp', 'wb') as f:
					pickle.dump(capture, f)
				break


		if args.figure:
			plt.clf()
			# plt.plot(y1, linestyle = 'dotted', label='original')
			plt.plot(y1_hp, linestyle = 'dotted', label='highpass')
			# plt.plot(y2, linestyle = 'dotted')
			plt.show()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
						prog = 'Baby Monitor',
						description = '')
	parser.add_argument('--vis', dest='visualize',
						action='store_true')
	parser.add_argument('--fig', dest='figure',
						action='store_true')
	parser.add_argument('--verbose', dest='verbose',
						action='store_true')
	args = parser.parse_args()

	while True:
		record({'stop': threading.Event(), 'capture':threading.Event()}, args)
