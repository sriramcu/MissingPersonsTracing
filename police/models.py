from django.db import models
from django.contrib.auth.models import AbstractUser
from django import forms
from django.core.exceptions import ValidationError 
import datetime
from django.conf import settings

# Create your models here.

#from phonenumber_field.modelfields import PhoneNumberField

def validate_mobile(value):
    if len(value)!=10:
        raise ValidationError("Mobile number must be of length 10")
    elif not value.isnumeric():
        raise ValidationError("Mobile number must have digits only")
        
def validate_age(value): 
    age = (datetime.date.today() - value) // datetime.timedelta(days=365.2425)
    if age>65 or age<25:
        raise ValidationError("Age of police officer must be between 25 and 65 ")
    

class PoliceStation(models.Model):
    #psid = models.CharField(max_length = 20, primary_key = True)
    name = models.CharField(max_length = 20,default='',unique=True)
    street = models.CharField(max_length=40)
    area = models.CharField(max_length=40)
    city = models.CharField(max_length=40)
    state = models.CharField(max_length=40)
    class Meta:
        db_table = 'police_stations'
        verbose_name_plural = db_table
        
        
class Police(models.Model):
    #id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40, default = '')
    mobile = models.CharField(max_length=10,validators=[validate_mobile])
    rank = models.CharField(max_length=50)
    sex = models.CharField(max_length = 1)
    dob = models.DateField(validators = [validate_age],default = datetime.date(1980,1,1))
    police_station_id = models.ForeignKey('PoliceStation',on_delete = models.CASCADE)
    login =  models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default = 1,
        
    )
    
    class Meta:
        db_table = 'police_officers'
        verbose_name_plural = db_table
    
    
class Victim(models.Model):
    name = models.CharField(max_length=40)
    sex = models.CharField(max_length = 1)
    dob = models.DateField()
    email = models.EmailField(default='')
    mobile = models.CharField(max_length=10,validators=[validate_mobile],unique=True)
    street = models.CharField(max_length=40)
    area = models.CharField(max_length=40)
    city = models.CharField(max_length=40)
    state = models.CharField(max_length=40)
    eye_colour = models.CharField(max_length=40)
    hair_colour = models.CharField(max_length=40)
    skin_tone = models.CharField(max_length=40)
    suspect_id = models.ForeignKey('Suspect',on_delete = models.CASCADE,default = '',null=True,blank=True)
    police_officer_id = models.ForeignKey('Police',on_delete = models.CASCADE,default = '',null=True,blank=True)
    police_station_id = models.ForeignKey('PoliceStation',on_delete = models.CASCADE,default = '',null=True,blank=True)
    comments = models.CharField(max_length=200,blank = True)
    status = models.CharField(max_length=500,blank = True,null=True,default='')
    messages  = models.CharField(max_length=500,blank = True,null=True,default='')
    class Meta:
        db_table = 'victims'
        verbose_name_plural = db_table
    
class Sightings(models.Model):
    street = models.CharField(max_length=40)
    area = models.CharField(max_length=40)
    city = models.CharField(max_length=40)
    state = models.CharField(max_length=40)
    date_time_sighting = models.DateTimeField(verbose_name = "Choose date and time of sighting",null = True, blank = True)
    victim_id = models.ForeignKey('Victim',on_delete = models.CASCADE)
    
        
    class Meta:
        
        db_table = 'sightings' 
        verbose_name_plural = db_table

        
class Suspect(models.Model):
    name = models.CharField(max_length=40)
    sex = models.CharField(max_length = 1)
    dob = models.DateField(validators = [validate_age])
    mobile = models.CharField(max_length=10,validators=[validate_mobile])
    street = models.CharField(max_length=40)
    area = models.CharField(max_length=40)
    city = models.CharField(max_length=40)
    state = models.CharField(max_length=40)
    police_officer_id = models.ForeignKey('Police',verbose_name='Interrogated By',on_delete = models.CASCADE,default = '',null=True,blank=True)
    
    class Meta:
        db_table = 'suspects'
        verbose_name_plural = db_table
    

class input_image(models.Model):
	image = models.FileField(upload_to='uploads')
	
	
class other_input_image(models.Model):
	image = models.FileField(upload_to='uploads')
	img_type = models.CharField(max_length=20, choices=(('suspect','Suspect'),('victim','Victim')), default='suspect')
