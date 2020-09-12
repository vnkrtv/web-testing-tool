from rest_framework import serializers

from main.models import Subject, Test


class SubjectSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=50)
    description = serializers.CharField()

    def create(self, validated_data):
        return Subject.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


class TestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    subject_id = serializers.IntegerField()
    author_id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField()
    tasks_num = serializers.IntegerField()
    duration = serializers.IntegerField()

    def create(self, validated_data):
        return Test.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.tasks_num = validated_data.get('tasks_num', instance.tasks_num)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.save()
        return instance
