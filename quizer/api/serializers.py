from rest_framework import serializers

from main.models import Subject


class SubjectSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    description = serializers.CharField()

    def create(self, validated_data):
        return Subject.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance
