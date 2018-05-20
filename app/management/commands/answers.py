# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from app.models import Question, Answer
from random import choice, randint
from faker import Factory
import os


class Command(BaseCommand):
    help = 'Fill answers'

    def add_arguments(self, parser):
        parser.add_argument('--min-number',
                            action='store',
                            dest='min_number',
                            default=1,
                            help='Min number of answers for a question'
                            )
        parser.add_argument('--max-number',
                            action='store',
                            dest='max_number',
                            default=5,
                            help='Max number of answers for a question'
                            )

    def handle(self, *args, **options):
        fake = Factory.create()

        min_number = int(options['min_number'])
        max_number = int(options['max_number'])

        users = User.objects.all()[1:]
        questions = Question.objects.all()

        for q in questions:
            for i in range(0, randint(min_number, max_number)):
                ans = Answer()
                ans.text = fake.paragraph(nb_sentences=randint(2, 10), variable_nb_sentences=True)
                ans.author = choice(users)
                ans.question = q
                ans.save()

