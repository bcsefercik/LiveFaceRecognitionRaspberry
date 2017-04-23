import requests
import time

while True:
    r = requests.get('http://hoosthere-env.sa8qqj3a66.eu-central-1.elasticbeanstalk.com/generate/')
    print(r)
    time.sleep(0.5)
