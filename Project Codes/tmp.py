import board
import adafruit_am2320
import busio
from signal import signal, SIGINT



i2c = board.I2C()
sensor = adafruit_am2320.AM2320(i2c)

while True:
	print("Temperature: ", sensor.temperature)
	print("Humidity: ", sensor.relative_humidity)
	time.sleep(2)
