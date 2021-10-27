from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main import utils
from main.models import (
    Profile,
    Subject,
    Test,
    Question,
    TestResult,
    RunningTestsAnswers,
    UserResult,
)
from .serializers import (
    ProfileSerializer,
    SubjectSerializer,
    TestSerializer,
    QuestionSerializer,
    TestResultSerializer,
    UserResultSerializer,
)
from .permissions import IsLecturer, TestAPIPermission


logger = utils.get_logger(__name__)


class UserAPI(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, request):
        users = Profile.objects.all()

        group = request.query_params.get("group", None)
        if group:
            users = users.filter(user__groups__name=group)

        serializer = ProfileSerializer(users, many=True)
        return Response({"users": serializer.data})


class SubjectAPI(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, _):
        serializer = SubjectSerializer(Subject.objects.all(), many=True)
        return Response({"subjects": serializer.data})

    def post(self, request):
        if request.data.get("load"):
            message = utils.add_subject_with_tests(request)
            return Response({"success": message})
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_subject = serializer.save()
        logger.info(
            "subject %s was added by %s", new_subject.name, request.user.username
        )
        return Response(
            {"success": "Предмет '%s' успешно добавлен." % new_subject.name}
        )

    def put(self, request, subject_id):
        updated_subject = get_object_or_404(Subject.objects.all(), pk=subject_id)
        serializer = SubjectSerializer(
            instance=updated_subject, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            updated_subject = serializer.save()
        logger.info(
            "subject %s was updated by %s", updated_subject.name, request.user.username
        )
        return Response(
            {
                "success": "Предмет '%s' был успешно отредактирован."
                % updated_subject.name
            }
        )

    def delete(self, request, subject_id):
        subject = get_object_or_404(Subject.objects.all(), pk=subject_id)
        message = (
            "Учебный предмет '%s', а также все тесты и вопросы, "
            "относящиеся к нему, были успешно удалены." % subject.name
        )
        logger.info("subject %s was deleted by %s", subject.name, request.user.username)
        subject.delete()
        return Response({"success": message})


class TestAPI(APIView):
    permission_classes = [IsAuthenticated, TestAPIPermission]

    def get(self, request):
        state = request.query_params.get("state", None)
        if state == "running":
            tests = Test.objects.get_running()
        elif state == "not_running":
            tests = Test.objects.get_not_running()
        else:
            tests = Test.objects.all()

        subject_id = request.query_params.get("subject_id", None)
        if subject_id:
            tests = tests.filter(subject__id=subject_id)

        serializer = TestSerializer(tests, many=True)
        return Response({"tests": serializer.data})

    def post(self, request):
        serializer = TestSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_test = serializer.save()
        logger.info(
            "test %s for subject %s was added by %s",
            new_test.name,
            new_test.subject.name,
            request.user.username,
        )
        return Response(
            {
                "success": "Тест '%s' по предмету '%s' успешно добавлен."
                % (new_test.name, new_test.subject.name)
            }
        )

    def put(self, request, test_id):
        updated_test = get_object_or_404(Test.objects.all(), pk=test_id)
        serializer = TestSerializer(
            instance=updated_test, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            updated_test = serializer.save()
        logger.info(
            "test %s for subject %s was updated by %s",
            updated_test.name,
            updated_test.subject.name,
            request.user.username,
        )
        return Response(
            {
                "success": "Тест '%s' по предмету '%s' был успешно отредактирован."
                % (updated_test.name, updated_test.subject.name)
            }
        )

    def delete(self, request, test_id):
        test = get_object_or_404(Test.objects.all(), pk=test_id)
        message = (
            "Тест '%s' по предмету '%s', а также все "
            "вопросы к нему были успешно удалены." % (test.name, test.subject.name)
        )
        logger.info(
            "test %s for subject %s was deleted by %s",
            test.name,
            test.subject.name,
            request.user.username,
        )
        test.delete()
        return Response({"success": message})


class LaunchTestAPI(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def put(self, request, test_id):
        test = get_object_or_404(Test.objects.all(), pk=test_id)
        if test.questions.count() < test.tasks_num:
            return Response(
                {
                    "ok": False,
                    "message": "Тест %s не запущен, так как вопросов в базе меньше %d."
                    % (test.name, test.tasks_num),
                }
            )
        TestResult.objects.create(
            test=test,
            launched_lecturer=request.user,
            subject=test.subject,
            is_running=True,
            comment=request.data.get("comment", ""),
        )
        logger.info(
            "test %s for subject %s was launched by %s",
            test.name,
            test.subject.name,
            request.user.username,
        )
        message = "Тест '%s' запущен. Состояние его прохождения можно отследить во вкладке 'Запущенные тесты'."
        return Response({"ok": True, "message": message % test.name})


class QuestionAPI(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, request, test_id):
        serializer = QuestionSerializer(
            Question.objects.filter(test__id=test_id), many=True
        )
        return Response({"questions": serializer.data})

    def post(self, request, test_id):
        serializer = QuestionSerializer()
        try:
            if request.POST.get("load"):
                questions = utils.load_questions_list(request, test_id)
                for question in questions:
                    serializer.create(question)
                message = "Вопросы к тесту в количестве %d успешно добавлены." % len(
                    questions
                )
                logger.info(
                    "%s questions was loaded by %s",
                    len(questions),
                    request.user.username,
                )
                return Response({"success": message})
            question = serializer.create_from_request(request)
            message = "Вопрос '%s' к тесту '%s' успешно добавлен."
            logger.info(
                "question %s for test %s, subject %s was loaded by %s",
                question.formulation,
                question.test.name,
                question.test.subject.name,
                request.user.username,
            )
            return Response(
                {"success": message % (question.formulation, question.test.name)}
            )
        except utils.EmptyOptionsError:
            logger.error(
                "error on adding new question by %s - empty options",
                request.user.username,
            )
            return Response(
                {
                    "error": f"Вопрос не был добавлен, так как присутствуют пустые варианты ответов."
                }
            )
        except UnicodeDecodeError:
            logger.error(
                "error on adding new question by %s - invalid text file format",
                request.user.username,
            )
            return Response({"error": f"Файл некорректного формата."})
        except utils.InvalidFileFormatError as e:
            logger.error(
                "error on adding new question by %s - invalid text file format",
                request.user.username,
            )
            return Response({"error": f"Вопросы не были загружены: {e}"})

    def put(self, request, test_id, question_id):
        question = get_object_or_404(Question.objects.all(), id=question_id)
        serializer = QuestionSerializer(
            instance=question, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            updated_question = serializer.save()
        message = "Вопрос '%s' по тесту '%s' был успешно отредактирован."
        logger.info(
            "question %s for test %s, subject %s was updated by %s",
            updated_question.formulation,
            updated_question.test.name,
            updated_question.test.subject.name,
            request.user.username,
        )
        return Response(
            {
                "success": message
                % (updated_question.formulation, updated_question.test.name)
            }
        )

    def delete(self, request, test_id, question_id):
        question = get_object_or_404(Question.objects.all(), id=question_id)
        message = "Вопрос '%s' по тесту '%s' был успешно удален." % (
            question.formulation,
            question.test.name,
        )
        logger.info(
            "question %s for test %s, subject %s was deleted by %s",
            question.formulation,
            question.test.name,
            question.test.subject.name,
            request.user.username,
        )
        question.delete()
        return Response({"success": message})


class TestsResultAPI(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, request):
        results = TestResult.objects.all()

        test_results_id = request.query_params.get("id", None)
        if test_results_id:
            serializer = TestResultSerializer(results.get(id=test_results_id))
            return Response(serializer.data)

        subject_id = request.query_params.get("subject_id", None)
        if subject_id:
            results = results.filter(subject__id=subject_id)

        test_id = request.query_params.get("test_id", None)
        if test_id:
            results = results.filter(test__id=test_id)

        serializer = TestResultSerializer(results, many=True)
        results_count_only = request.query_params.get("results_count_only", None)
        if results_count_only:
            for res in serializer.data:
                res["results_count"] = len(res["results"])
                del res["results"]
        return Response({"results": serializer.data})


class UserResultAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        results = UserResult.objects.all()

        user_id = request.query_params.get("user_id", None)
        if user_id:
            results = results.filter(user__id=user_id)

        group = request.query_params.get("group", None)
        if group:
            results = results.filter(user__profile__group=group)

        subject_id = request.query_params.get("subject_id", None)
        if subject_id:
            results = results.filter(testing_result__subject__id=subject_id)

        test_id = request.query_params.get("test_id", None)
        if test_id:
            results = results.filter(testing_result__test__id=test_id)

        non_zero = request.query_params.get("non_zero", None)
        if non_zero:
            results = results.filter(right_answers_count__gt=0)

        course = request.query_params.get("course", None)
        if course:
            results = [res for res in results if str(res.user.profile.course) == course]

        serializer = UserResultSerializer(results, many=True)
        return Response({"results": serializer.data})


class RunningTestAPI(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, request):
        serializer = TestResultSerializer(
            TestResult.objects.filter(is_running=True), many=True
        )
        return Response({"tests": serializer.data})


class QuestionAnalysisAPI(APIView):
    permission_classes = [IsAuthenticated, IsLecturer]

    def get(self, request):
        results = UserResult.objects.filter(right_answers_count__gt=0)

        zero_results = request.query_params.get("zero_results", None)
        if zero_results:
            results = UserResult.objects.all()

        subject_id = request.query_params.get("subject_id", None)
        if subject_id:
            results = results.filter(testing_result__subject__id=subject_id)

        test_id = request.query_params.get("test_id", None)
        if test_id:
            results = results.filter(testing_result__test__id=test_id)

        stats = {}
        for result in results.values("questions"):
            for question in result["questions"]:
                q_id = question["question_id"]
                if "is_true" in question:
                    is_true = question["is_true"]
                else:
                    is_true = question["selected_options"] == question["right_options"]
                if q_id not in stats:
                    stats[q_id] = {"true": 0, "false": 0}
                if is_true:
                    stats[q_id]["true"] += 1
                else:
                    stats[q_id]["false"] += 1

        return Response({"stats": stats})
