# pylint: skip-file
from django.test import TestCase
from django.contrib.auth.models import User
from .views import *


class ModelsTestCase(TestCase):
    def setUp(self):
        User.objects.create(
            id=1,
            username='Test user',
        )
        Subject.objects.create(
            lecturer=User.objects.get(id=1),
            name='Test subject',
            description='Description of test subject'
        )
        Test.objects.create(
            subject=Subject.objects.get(id=1),
            author=User.objects.get(id=1),
            name='First test',
            description='Description of test for test subject',
            tasks_num=10,
            duration=60
        )

    def test_foreign_keys(self):
        user = User.objects.get(id=1)
        subject = Subject.objects.get(id=1)
        test = Test.objects.get(id=1)
        self.assertEqual(test.author, user)
        self.assertEqual(subject.lecturer, user)
        self.assertEqual(test.subject, subject)


class Test