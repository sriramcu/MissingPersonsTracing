from django.contrib import admin
from .models import Police,Victim,Suspect,Sightings,PoliceStation

@admin.register(Police)
class PoliceAdmin(admin.ModelAdmin):
    pass
    
@admin.register(PoliceStation)
class PoliceStationAdmin(admin.ModelAdmin):
    pass
    
@admin.register(Victim)
class VictimAdmin(admin.ModelAdmin):
    pass
    
@admin.register(Suspect)
class SuspectAdmin(admin.ModelAdmin):
    pass
    
@admin.register(Sightings)
class SightingsAdmin(admin.ModelAdmin):
    pass

