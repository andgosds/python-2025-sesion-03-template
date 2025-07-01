from django.db import models

# Create your models here.
import secrets
from django.db import models

def _hex_id():
    return secrets.token_hex(12)  # 24 caracteres hexadecimales

class Book(models.Model):
    id     = models.CharField(primary_key=True, max_length=24, default=_hex_id, editable=False)
    title  = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    pages  = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "books"
        ordering = ["title"]