from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from decimal import Decimal
from datetime import datetime


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)  # Make email unique
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
 
    objects = CustomUserManager() # Set default custom manager
    
    USERNAME_FIELD = "email"  # Use email to log in
    REQUIRED_FIELDS = ["first_name", "last_name"]  # Required fields besides email

    def __str__(self):
        return self.email


# submission holds user, receipt, and creation date.
class Submission(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    receipt = models.ForeignKey(
        'Receipt', 
        on_delete=models.CASCADE, 
        related_name="submissions",
        null=True,
        blank=True
        )
    
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.user.email} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


def create_default_receipt_name():
    return f"untitled-receipt-{datetime.now().strftime('%Y%m%d%H%M%S')}"

# receipt object
class Receipt(models.Model):
    receipt_name = models.CharField(max_length=50, default=create_default_receipt_name)
    store_name = models.CharField(max_length=200)
    
    store_phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?\d{10,15}$', message="Enter a valid phone number.")]
    )
    store_address = models.CharField(max_length=200)
    store_site = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    line_items = models.CharField(max_length=20000, blank=True)
    total_payment = models.DecimalField(max_digits=10, decimal_places=2)
    pay_method = models.CharField(max_length=200)

    def __str__(self):
        return f"Receipt from {self.store_name} - Total: ${self.total_payment}"

