from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from police.models import Police, Victim, Sightings,input_image, other_input_image
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput, DateTimePickerInput, MonthPickerInput, YearPickerInput   

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    #comment = forms.CharField(label='enter comment')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AdditionalPoliceDetailsForm(forms.ModelForm):
    class Meta:
        model = Police
        exclude = ('login',)
    
# ~ class DateInput(forms.DateInput):
    # ~ input_type = 'date'
    
# ~ class DateTimeInput(forms.DateTimeInput):
    # ~ input_type = 'datetime'
    
class VictimDetailsForm(forms.ModelForm):
    class Meta:
        model = Victim
        exclude = ('police_station_id','suspect_id','status','messages',)
        widgets = {
            'dob': DatePickerInput(format='%d/%m/%Y')
        }
        
class SightingsForm(forms.ModelForm):
    class Meta:
        model = Sightings
        exclude = ('victim_id',)
        widgets = {'date_time_sighting': DateTimePickerInput(format='%d/%m/%Y %H:%M:%S')}
        
        
class ImageForm(forms.ModelForm):
	class Meta:
		model = input_image
		fields = '__all__'
		
class OtherImageForm(forms.ModelForm):
	class Meta:
		model = other_input_image
		fields = '__all__'
		


#SightingsFormSet =  inlineformset_factory(Victim,Sightings,SightingsForm,extra=1)
