# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from app.models import Question, Tag

from random import choice, randint
import os


class Command(BaseCommand):
    help = 'Fill tags'

    def add_arguments(self, parser):
        parser.add_argument('--number',
                            action='store',
                            dest='number',
                            default=4,
                            help='Number of tags for a question'
                            )

    def handle(self, *args, **options):
        tags = [
            'java', 'php', 'android', 'jquery', 'python',
            'html', 'css', 'ios', 'mysql', 'sql',
        ]

        for tag in tags:
            if len(Tag.objects.filter(title=tag)) == 0:
                t = Tag()
                t.title = tag
                t.save()

        number = int(options['number'])
        tags = Tag.objects.all()

        for q in Question.objects.all():
            if len(q.tags.all()) < number:
                for i in range(0, number - len(q.tags.all())):
                    t = choice(tags)

                    if t not in q.tags.all():
                        q.tags.add(t)