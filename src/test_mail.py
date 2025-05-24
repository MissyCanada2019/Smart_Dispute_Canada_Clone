import os
import requests
def send_simple_message():
  	return requests.post(
  		"https://api.mailgun.net/v3/sandbox4d5b2116b4b3442ca4e0c59b97c8cb56.mailgun.org/messages",
  		auth=("api", os.getenv('API_KEY', 'API_KEY')),
  		data={"from": "Mailgun Sandbox <postmaster@sandbox4d5b2116b4b3442ca4e0c59b97c8cb56.mailgun.org>",
			"to": "Teresa Melissa <smartdisputecanada@gmail.com>",
  			"subject": "Hello Teresa Melissa",
  			"text": "Congratulations Teresa Melissa, you just sent an email with Mailgun! You are truly awesome!"})
