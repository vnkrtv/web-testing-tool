from django.contrib.auth.models import User

from rest_framework import serializers

from main.models import Subject, Test


class SubjectSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=50)
    description = serializers.CharField(required=False)

    def create(self, validated_data):
        return Subject.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance

    class Meta:
        model = Subject
        read_only_fields = (
            'id',
        )


class TestSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    subject = serializers.IntegerField()
    author = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, default='')
    tasks_num = serializers.IntegerField()
    duration = serializers.IntegerField()

    def create(self, validated_data):
        subject = Subject.objects.get(id=validated_data.get('subject'))
        author = User.objects.get(id=validated_data.get('author'))
        return Test.objects.create(
            name=validated_data.get('name'),
            description=validated_data.get('description'),
            tasks_num=validated_data.get('tasks_num'),
            duration=validated_data.get('duration'),
            subject=subject,
            author=author)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.tasks_num = validated_data.get('tasks_num', instance.tasks_num)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.save()
        return instance

    class Meta:
        model = Subject
        read_only_fields = (
            'id',
            'subject_id',
            'author_id'
        )
