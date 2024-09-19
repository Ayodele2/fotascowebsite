from django.db import models

class UserRegistration(models.Model):
    full_name = models.CharField(max_length=100)
    dob = models.DateField()  # Date of Birth
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')])
    roles = models.CharField(max_length=50, choices=[('Admin', 'Admin'), ('Staffs', 'Staffs'), ('Guard', 'Guard')])

    # Identity details
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    next_of_kin = models.CharField(max_length=100)
    relationship = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name
