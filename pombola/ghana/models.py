from django.db import models

from pombola.core.models import Person, Position
from pombola.hansard.models import Sitting, Entry


class UploadModel(models.Model):
    name = models.CharField(max_length=64, blank=True)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/%H/%M/%S')

    @property
    def filename(self):
        return self.file.name.rsplit('/', 1)[-1]


class MP(models.Model):
    """Currently, this is just storage for data we scraped for mps in Ghana,
    mapped to a Person model in the core mzalendo codebase.
    """
    person = models.ForeignKey(Person)
    party_position = models.ForeignKey(Position, related_name='party_positions')
    parliament_position = models.ForeignKey(Position, related_name='parliament_positions')

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True, default='')

    occupation = models.CharField(max_length=180, blank=True, default='')
    marital_status = models.CharField(max_length=50, blank=True, default='')
    hometown = models.CharField(max_length=150, blank=True, default='')
    education = models.CharField(max_length=255, blank=True, default='')
    religion = models.CharField(max_length=100, blank=True, default='')
    last_employment = models.CharField(max_length=150, blank=True, default='')
    votes_obtained = models.CharField(max_length=150, blank=True, default='')

    def __unicode__(self):
        if self.middle_name:
            return "%s %s %s" % (self.first_name, self.middle_name, self.last_name)
        else:
            return "%s %s" % (self.first_name, self.last_name)


class GhanaMP(Person):
    class Meta:
        proxy= True
        verbose_name = "MP"


class HansardEntry(models.Model):
    sitting = models.ForeignKey(Sitting)
    entry = models.ForeignKey(Entry)
    time = models.TimeField()
    section = models.CharField(max_length=255, blank=True, default='')
    column = models.IntegerField(default=0)
