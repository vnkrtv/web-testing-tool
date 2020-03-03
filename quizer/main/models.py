from django.db import models

class Test(models.Model):
    question = models.TextField('Вопрос', max_length=200)
    #option_1 = models.CharField('Первый вариант ответа')