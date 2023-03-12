import config
import requests
import datetime

message = 'motion detected'
curr_time = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")

resp = requests.post('https://textbelt.com/text', {
  'phone': config.PHONE,
  'message': message + " at " + curr_time,
  'key': config.KEY,
})

print(resp.json())