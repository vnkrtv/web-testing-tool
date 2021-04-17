import pathlib
from bson import ObjectId

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.auth.models import User

from rest_framework import serializers

from main.models import Subject, Test, Question, TestResult, RunningTestsAnswers


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
    description = serializers.CharField(default='')
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
        instance.description = validated_data.get('description', '')
        instance.tasks_num = validated_data.get('tasks_num', instance.tasks_num)
        instance.duration = validated_data.get('duration', instance.duration)
        instance.save()
        return instance

    class Meta:
        model = Test
        read_only_fields = (
            'id',
            'subject_id',
            'author_id'
        )


class QuestionSerializer(serializers.Serializer):
    _id = serializers.CharField(max_length=100)
    test_id = serializers.IntegerField()
    formulation = serializers.CharField(max_length=1_000)
    multiselect = serializers.BooleanField()
    tasks_num = serializers.IntegerField()
    type = serializers.CharField(max_length=50)
    options = serializers.JSONField()

    def create(self, validated_data):
        test = Test.objects.get(id=validated_data.get('test_id'))
        return Question.objects.create(
            formulation=validated_data.get('formulation'),
            multiselect=validated_data.get('multiselect'),
            tasks_num=validated_data.get('tasks_num'),
            type=validated_data.get('type'),
            options=Question.parse_options(validated_data.get('options')),
            test=test)

    @classmethod
    def create_from_request(cls, request):
        test = Test.objects.get(id=request.data.get('test_id'))
        questions_id = ObjectId()
        if request.data.get('with_images'):
            questions_type = Question.Type.WITH_IMAGES
            options = []
            for i, file_name in enumerate(request.FILES):
                path = pathlib.Path(f'{test.subject.name}/{test.name}/{questions_id}/{i}.{file_name.split(".")[-1]}')
                default_storage.save(path, ContentFile(request.FILES[file_name].read()))
                options.append({
                    'option': str(path),
                    'is_true': request.data.get(file_name) == 'true'
                })
        else:
            questions_type = Question.Type.REGULAR
            options = request.data.get('options')
        return Question.objects.create(
            _id=questions_id,
            formulation=request.data.get('formulation'),
            multiselect=request.data.get('multiselect'),
            tasks_num=request.data.get('tasks_num'),
            type=questions_type,
            options=Question.parse_options(options),
            test=test)

    def update(self, instance, validated_data):
        instance.formulation = validated_data.get('formulation', instance.formulation)
        instance.options = Question.parse_options(validated_data.get('options', instance.options))
        instance.save()
        return instance

    class Meta:
        model = Question
        read_only_fields = (
            '_id',
            'test_id'
        )


class TestResultSerializer(serializers.Serializer):
    _id = serializers.SerializerMethodField()
    is_running = serializers.BooleanField()
    comment = serializers.CharField(max_length=1_000)
    date = serializers.DateTimeField(format="%H:%M:%S  %d-%m-%y")
    test_id = serializers.IntegerField()
    launched_lecturer_id = serializers.IntegerField()
    subject_id = serializers.IntegerField()
    results = serializers.JSONField()

    def get__id(self, obj):
        return str(obj._id)

    def create(self, validated_data):
        launched_lecturer = User.objects.get(id=validated_data.get('launched_lecturer_id'))
        subject = Subject.objects.get(id=validated_data.get('subject_id'))
        test = Test.objects.get(id=validated_data.get('test_id'))
        return TestResult.objects.create(
            is_running=validated_data.get('is_running'),
            comment=validated_data.get('comment'),
            date=validated_data.get('date'),
            results=validated_data.get('results'),
            launched_lecturer=launched_lecturer,
            subject=subject,
            test=test)

    def update(self, instance, validated_data):
        instance.formulation = validated_data.get('is_running')
        instance.save()
        return instance

    class Meta:
        model = TestResult
        read_only_fields = (
            'test_id',
            'launched_lecturer_id',
            'subject_id'
        )
