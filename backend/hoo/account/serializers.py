from rest_framework import serializers
from .models import Resident, Visit, Message

class ResidentSerializer(serializers.ModelSerializer):

	class Meta:
		model = Resident
		fields = ('username', 'name', 'microsoft_id', 'video_id', 'photo_id')


class VisitSerializer(serializers.ModelSerializer):
	visitor = ResidentSerializer(many=False, read_only=True)
	date = serializers.DateTimeField(format="%m %d, %Y %H:%M")

	class Meta:
		model = Visit
		fields = ('id', 'status', 'date', 'visitor')


class MessageSerializer(serializers.ModelSerializer):
	date = serializers.DateTimeField(format="%m %d, %Y %H:%M")
	target = ResidentSerializer(many=False, read_only=True)

	class Meta:
		model = Message
		fields = ('id', 'status', 'date', 'message', 'target')