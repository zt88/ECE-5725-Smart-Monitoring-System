import RPi.GPIO as GPIO
import config
import requests
import datetime

# GPIO setup
PIR_1 = 17
PIR_2 = 22
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIR_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# callbacks
def motion_1(channel):
	message = '\U0001F3C3\U0001F4A8 left motion detected'
	curr_time = datetime.datetime.now().strftime("%H:%M:%S %m/%d/%Y")
	resp = requests.post('https://textbelt.com/text', {
		'phone': config.PHONE,
		'message': message + " at " + curr_time,
		'key': config.KEY,
	})
	# debug uses
	print(message + " at " + curr_time)
	print(resp.json())

def motion_2(channel):
	message = '\U0001F3C3\U0001F4A8 right motion detected'
	curr_time = datetime.datetime.now().strftime("%H:%M:%S %m/%d/%Y")
	resp = requests.post('https://textbelt.com/text', {
		'phone': config.PHONE,
		'message': message + " at " + curr_time,
		'key': config.KEY,
	})
	# debug uses
	print(message + " at " + curr_time)
	print(resp.json())
	
GPIO.add_event_detect(PIR_1, GPIO.RISING, callback=motion_1)
GPIO.add_event_detect(PIR_2, GPIO.RISING, callback=motion_2)

while True:
	try:
		pass
	except KeyboardInterrupt:
		GPIO.cleanup()




