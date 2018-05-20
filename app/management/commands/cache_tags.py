from django.core.management.base import BaseCommand

from app.models import ProjectCache


class Command(BaseCommand):
    help = 'Caches popular tags'

    def handle(self, *args, **options):
        ProjectCache.update_popular_tags()
        self.stdout.write('Popular tags -- cached')
