from django.core.management.base import BaseCommand

from app.models import ProjectCache


class Command(BaseCommand):
    help = 'Caches best users'

    def handle(self, *args, **options):
        ProjectCache.update_best_users()
        self.stdout.write('Best users -- cached')
