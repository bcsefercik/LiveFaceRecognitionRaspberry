import requests

class Network:
	def __init__(self, endpoint = 'http://hoo-dev.eu-central-1.elasticbeanstalk.com/hoo/'):
		self.endpoint = endpoint

	def create_visit(self, username, video_id, status=0):
		return requests.post(self.endpoint + 'create_visit/', json={'username': username, 'video_id': video_id, 'status': status})

	def get_message(self, username):
		req = requests.get(self.endpoint + 'create_message/', params={'username': username})
		if req.status_code == 200:
			json = req.json()

			if 'result' in json:
				return None
			else:
				return json['message']
		else:
			return None
		print(req)
		