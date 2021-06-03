import json
import pathlib
from typing import List, Dict, Any

from bson import ObjectId

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.auth.models import User

from rest_framework import serializers

from main.models import Profile, Subject, Test, Question, TestResult, RunningTestsAnswers, UserResult


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    course = serializers.IntegerField()

    def get_username(self, profile):
        try:
            return profile.user.username
        except User.DoesNotExist:
            return ''

    class Meta:
        model = Profile
        fields = ('id', 'username', 'course', 'created_at', 'name', 'web_url', 'group', 'admission_year', 'number')


class SubjectSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=50)
    description = serializers.CharField(required=False)
    tests_count = serializers.SerializerMethodField()

    def get_tests_count(self, subject):
        return subject.tests.count()

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
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(default='')
    tasks_num = serializers.IntegerField()
    duration = serializers.IntegerField()
    questions_num = serializers.SerializerMethodField()

    subject = SubjectSerializer(read_only=True)
    author = UserSerializer(read_only=True)

    subject_id = serializers.IntegerField(write_only=True)
    author_id = serializers.IntegerField(write_only=True)

    def get_questions_num(self, test) -> int:
        return test.questions.count()

    def create(self, validated_data):
        subject = Subject.objects.get(id=validated_data.get('subject_id'))
        author = User.objects.get(id=validated_data.get('author_id'))
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

    def to_representation(self, test):
        representation = super().to_representation(test)
        test_results = TestResult.objects.filter(is_running=True, test__id=test.id).first()
        if test_results:
            representation['launched_lecturer'] = {
                'id': test_results.launched_lecturer.id,
                'username': test_results.launched_lecturer.username
            }
        return representation

    class Meta:
        model = Test
        read_only_fields = (
            'id'
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
            multiselect=json.loads(request.data.get('multiselect')),
            tasks_num=request.data.get('tasks_num'),
            type=questions_type,
            options=Question.parse_options(options),
            test=test)

    def update(self, instance, validated_data):
        instance.formulation = validated_data.get('formulation', instance.formulation)
        options = validated_data.get('options')
        if options:
            for option in options:
                option['is_true'] = ('true' == option['is_true']) or (option['is_true'] == True)
            instance.options = Question.parse_options(options)
        instance.save()
        return instance

    class Meta:
        model = Question
        read_only_fields = (
            '_id',
            'test_id'
        )


class UserResultSerializer(serializers.Serializer):
    _id = serializers.SerializerMethodField()
    user = UserSerializer()
    testing_result_id = serializers.CharField()
    time = serializers.IntegerField()
    tasks_num = serializers.IntegerField()
    right_answers_count = serializers.IntegerField()
    date = serializers.DateTimeField(format="%H:%M:%S  %d-%m-%y")
    questions = serializers.JSONField()

    def get__id(self, obj):
        return str(obj._id)

    def create(self, validated_data):
        user = User.objects.get(id=validated_data.get('user_id'))
        testing_result = TestResult.objects.get(_id=validated_data.get('testing_result_id'))
        return UserResult.objects.create(
            user=user,
            testing_result=testing_result,
            time=validated_data.get('time'),
            tasks_num=validated_data.get('tasks_num'),
            right_answers_count=validated_data.get('right_answers_count'),
            date=validated_data.get('date'),
            questions=validated_data.get('questions'))

    def update(self, instance, validated_data):
        return instance

    class Meta:
        model = UserResult
        read_only_fields = (
            '_id',
            'testing_result_id'
        )


class TestResultSerializer(serializers.Serializer):
    _id = serializers.SerializerMethodField()
    is_running = serializers.BooleanField()
    comment = serializers.CharField()
    date = serializers.DateTimeField(format="%H:%M:%S  %d-%m-%y")

    test = serializers.SerializerMethodField()
    launched_lecturer = UserSerializer()
    subject = SubjectSerializer()
    results = serializers.SerializerMethodField()

    test_id = serializers.IntegerField(write_only=True)
    launched_lecturer_id = serializers.IntegerField(write_only=True)
    subject_id = serializers.IntegerField(write_only=True)

    def get__id(self, obj):
        return str(obj._id)

    def get_test(self, obj):
        if obj.test_id:
            test = Test.objects.get(id=obj.test_id)
            return {
                'id': test.id,
                'name': test.name,
                'description': test.description,
                'duration': test.duration,
                'tasks_num': test.tasks_num
            }
        return {
            'id': 0,
            'name': 'deleted',
            'description': ''
        }

    def to_representation(self, test_results):
        representation = super().to_representation(test_results)
        representation['results'].sort(key=lambda res: res['date'])
        return representation

    def get_results(self, test_results) -> List[Dict[str, Any]]:
        serializer = UserResultSerializer(UserResult.objects.filter(testing_result=test_results), many=True)
        return serializer.data

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
            '_id',
            'launched_lecturer',
            'subject',
            'results'
        )
