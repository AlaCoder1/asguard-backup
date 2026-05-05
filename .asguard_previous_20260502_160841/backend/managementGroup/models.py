from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Group(models.Model):
    groupname = models.CharField(max_length=200, null=True, unique=True, verbose_name=_("group name"))
    description = models.CharField(max_length=200, null=True)
    gid = models.IntegerField(null=True, unique=True)
    fonctionalities = models.CharField(max_length=200, null=True)
    created_by_system = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'group'
    
    def __str__(self):
        return self.groupname
