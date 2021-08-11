from rest_framework import serializers
from ..models import Subject, Course , Module, Content

class SubjectSerializer(serializers.ModelSerializer):
	class Meta:
		model = Subject 
		fields = ['id', 'name', 'code' ,'slug']

class ModuleSerializer(serializers.ModelSerializer):
	class Meta:
		model = Module
		fields = ['order', 'title', 'summary']

class CourseSerializer(serializers.ModelSerializer):
	modules = ModuleSerializer(many=True, read_only=True)

	class Meta:
		model = Course
		fields = [
			'id', 'title', 'subject', 'slug', 
			'description', 'instructor', 'date_created', 
			'payment_status', 'modules']

class ItemRelatedField(serializers.RelatedField):
	def to_representation(self, value):
		return value

class ContentSerializer(serializers.ModelSerializer):
	item = ItemRelatedField(read_only=True)

	class Meta:
		model = Content
		fields = ['order', 'item']

class ModuleWithContentsSerializer(serializers.ModelSerializer):
	contents = ContentSerializer(many=True)

	class Meta:
		model = Module
		fields = ['order', 'title', 'summary', 'contents']

class CourseWithContentsSerializer(serializers.ModelSerializer):
	modules = ModuleWithContentsSerializer(many=True)

	class Meta:
		model = Course 
		fields = [
			'id', 'title', 'subject', 'slug', 
			'description', 'instructor', 'date_created', 
			'payment_status', 'modules'
		]