from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from api_system.models import Company

# Create your models here.
class ROLE(models.IntegerChoices):
    ADMIN_PIGNUS = 1
    ADMIN_COMPANY = 2
    ADMIN_AREA = 3
    ADMIN_MULTICOMPANY=4

class UserManager(BaseUserManager):
    def create_user(self, rut, user_name, company_id, area_id, password=None):
        if not rut:
            raise ValueError('The RUT field must be set')
        role = ROLE.ADMIN_AREA if area_id >= 0 else ROLE.ADMIN_COMPANY
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            company = None

        user = self.model(rut=rut, user_name=user_name, company=company, area_id=area_id, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, user_name, password=None):
        if not rut:
            raise ValueError('The RUT field must be set')

        user = self.model(rut=rut, user_name=user_name, company_id=24, area_id=-1, role=ROLE.ADMIN_PIGNUS)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):

    rut = models.CharField(max_length=20, unique=True)
    user_name = models.CharField(max_length=100)
    area_id = models.IntegerField(default=-1)
    company = models.ForeignKey("api_system.Company", on_delete=models.CASCADE, null=True)
    role = models.IntegerField(choices=ROLE, default=ROLE.ADMIN_AREA)

    objects = UserManager()

    USERNAME_FIELD = "rut"
    REQUIRED_FIELDS = ["user_name"]

