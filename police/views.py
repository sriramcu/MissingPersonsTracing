from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, AdditionalPoliceDetailsForm, SightingsForm, VictimDetailsForm, ImageForm, OtherImageForm
from django.contrib import messages
import time
from django.apps import apps 
from django.contrib import admin 
from django.contrib.admin.sites import AlreadyRegistered 
from django.db import connection
import re
from django.contrib.auth.models import User
from police.models import Police,PoliceStation, Victim, Sightings
from django.core.files.storage import FileSystemStorage
import os
import face_recognition
import sys
from ipware import get_client_ip
import pymongo
from pymongo import MongoClient
import gridfs
import shutil
from PIL import Image
from django.utils.datastructures import MultiValueDictKeyError
import io

'''
Django project to assist victims and detectives to trace missing people and the suspects. Includes facial recognition, MongoDB.
'''

cluster = MongoClient("mongodb+srv://sriramcu:rvce_cse@cluster0.imfyu.mongodb.net/dbdpartb")

db = cluster["dbdpartb"]
fs = gridfs.GridFS(db)
fsfiles = db["fs.files"]
test = db["test"]


def register(request):
    if 'context' in request.session:
        del request.session['context']
    if request.method == 'POST':
        print(request.POST)
        form = UserRegisterForm(request.POST)
        extended_form = AdditionalPoliceDetailsForm(request.POST)
        if form.is_valid() and extended_form.is_valid():
            form.save()
        
            print(extended_form.cleaned_data)
      
            cd = extended_form.cleaned_data

            number_re = re.compile(r'PoliceStation object \((\d+)\)')
            mo = number_re.search(str(cd['police_station_id']))
            num = mo.group(1)
            fk = int(num)
            last_user = User.objects.last()
            selected_station = PoliceStation.objects.get(pk=fk)
            Police.objects.create(police_station_id=selected_station,login=last_user,name=cd['name'],dob=str(cd['dob']),mobile=cd['mobile'],rank=cd['rank'],sex=cd['sex'])
            
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
        extended_form = AdditionalPoliceDetailsForm()
    return render(request, 'register.html', {'form': form,'form2': extended_form})
    
    
    

def register_case(request):
    if 'context' in request.session:
        del request.session['context']
    if request.method == 'POST' and 'Select' in request.POST and 'Register' not in request.POST:
        print("1")
        print(request.POST)
        
        num_sightings = int(request.POST.get('num_sightings')) #max 5
        print(num_sightings)
        if not (num_sightings>0):
            messages.error(request,"Number of sightings must be at least one")
            
            form1 = VictimDetailsForm()
            form2 = SightingsForm()
            return render(request, 'register_case.html', {'form1':form1 ,'form2':form2,'my_num':num_sightings,'num_range':range(0)})
            
        request.session['num'] = num_sightings
        form1 = VictimDetailsForm()
        form2 = SightingsForm()
        return render(request, 'register_case.html', {'form1':form1 ,'form2':form2,'my_num':num_sightings,'num_range':range(num_sightings)})
        
        
        
    elif request.method == 'POST' and 'Register' in request.POST:
        print("2")
        print(request.POST)
        num_sightings = request.session['num']
        form1 = VictimDetailsForm(request.POST)
        form2 = SightingsForm(request.POST)
        
        #if form1.is_valid() and form2.is_valid():
        print("Will add")
        
        cd = dict(request.POST)       
        
        Victim.objects.create(name=cd['name'][0],sex=cd['sex'][0],dob=cd['dob'][0],mobile=cd['mobile'][0],street=cd['street'][0],area=cd['area'][0],city=cd['city'][0],state=cd['state'][0],eye_colour=cd['eye_colour'][0],hair_colour=cd['hair_colour'][0],skin_tone=cd['skin_tone'][0],comments=cd['comments'][0],status=cd['status'][0],messages=cd['messages'][0])
        last_victim = Victim.objects.last()
        for i in range(num_sightings): #use i+1 for common fields and i for unique
            Sightings.objects.create(victim_id = last_victim,street=cd['street'][i+1],area=cd['area'][i+1],city=cd['city'][i+1],state=cd['state'][i+1],date_time_sighting=cd['date_time_sighting'][0])
        print("Added")
            
        return render(request, 'register_case.html', {'form1':form1 ,'form2':form2,'my_num':num_sightings,'num_range':range(num_sightings)})
        

        
    
        
        
    print("3")      
    form1 = VictimDetailsForm()
    form2 = SightingsForm()
    return render(request, 'register_case.html', {'form1':form1 ,'form2':form2,'num_range':range(0)})


def base(request):
    for fi in os.listdir('/home/sriram/work/MissingPersons/media/uploads'):
        os.remove(os.path.join('/home/sriram/work/MissingPersons/media/uploads',fi))
        
    for f in os.listdir('/home/sriram/work/MissingPersons/uploads/'):
        try:
            os.remove(os.path.join('/home/sriram/work/MissingPersons/uploads/',f))
            
        except OSError as e:
            print(e)
            continue
            
        else:
            print("{} deleted".format(f))
            
    for f in os.listdir('/home/sriram/work/MissingPersons/police/static/'):
        try:
            os.remove(os.path.join('/home/sriram/work/MissingPersons/police/static/',f))
            
        except OSError as e:
            print(e)
            continue
            
            
        else:
            print("{} deleted".format(f))
    
    if 'context' in request.session:
        del request.session['context']
    return render(request, 'base.html')

@login_required
def profile(request):
    if 'context' in request.session:
        del request.session['context']
    return render(request, 'profile.html')
    
    
@login_required
def tables(request):
    final_res = []
    selected_table = None
    columns = []
    tables = ['police_officers','suspects','victims','sightings','police_stations']
    context = {'tables':tables,'selected_table': selected_table,'returned_table':final_res,'columns':columns}
    user_id = request.user.id
    query2 = "select id from police_officers where login_id={};".format(user_id);
    cursor2= connection.cursor()
    res = cursor2.execute(query2)
    pol_id_list = [int(i[0]) for i in cursor2.fetchall()]
    pol_id = pol_id_list[0] if pol_id_list else None
    print("Pol id is " + str(pol_id))
    print("User id is "+str(user_id))
    cursor2.close()
    
    
    if request.method == "POST" and "Select" in request.POST:
        selected_table = request.POST.get("table")
        cursor = connection.cursor()
        if selected_table != 'victims' or request.user.is_superuser:
            query = "select * from {};".format(selected_table)
            
        else:
            
            query = "select * from victims where police_officer_id_id = '{}';".format(pol_id)
            
            
        res = cursor.execute(query)
        final_res = [] 
        for row in res:
            r1 = tuple(row)
            r1 = tuple(str(x) for x in row)
            final_res.append(r1)
       
        columns = [col[0] for col in cursor.description]
        context = {'tables':tables,'selected_table': selected_table,'returned_table':final_res,'columns':columns}
        request.session['context'] = context
        
    
    
    elif request.method == "POST" and "Update" in request.POST and 'context' in request.session:
      
        #selected_operation = request.POST.get("operation")
        
    
        context = request.session['context']
        columns = context['columns']
        selected_table = context['selected_table']
        if selected_table == 'police_officers' or selected_table == 'police_stations' or selected_table == 'suspects':
            messages.error(request,"Cannot modify {} table".format(selected_table))
            return render(request, 'tables.html', context)
    
        values = []
        for column in columns:
            values.append(request.POST[column])
        

        returned_table = context['returned_table']
        
            
        IDS = [a[0] for a in returned_table]
     
            
        if selected_table == 'victims':
            
            police_id = Victim.objects.get(pk=request.POST['id']).police_officer_id_id
            print("police_id is "+str(police_id))
            if police_id != pol_id and not request.user.is_superuser:
                messages.error(request, "Unauthorised operation")
                return render(request, 'tables.html', context)
                
            subquery = ""
            for column,value in zip(columns,values):
                if value == '' or column == 'id':
                    continue
                    
                if column == 'police_officer_id_id':
                    messages.error(request, "Unauthorised operation")
                    return render(request, 'tables.html', context)
                    
                    
                    
                if column!='messages':
                    subquery = subquery + "{}='{}',".format(column,value)
                else:
                    subquery = subquery + "messages=messages||'\n'||'{}',".format(value) #append messages
            subquery = subquery[:-1] #remove trailing comma
            query = "update victims set {} where id={};".format(subquery,request.POST['id'])
                
        elif selected_table == 'sightings':
            victim_id = int(Sightings.objects.get(pk=request.POST['id']).victim_id_id)
            print("victim_id is "+str(victim_id))
            police_id = int(Victim.objects.get(pk=victim_id).police_officer_id_id)
            print("police_id is "+str(police_id))
            if victim_id != pol_id and not request.user.is_superuser:
                messages.error(request, "Unauthorised operation")
                return render(request, 'tables.html', context)
                
            query = "insert into sightings values {};".format(selected_table,str(tuple(values)))
                
        else:
            messages.error(request,"Unknown error")
            print(selected_table)
            return render(request, 'tables.html', context)
                    
            

                    
                
        try:
            print(query)
            cursor2 = connection.cursor()
            res = cursor2.execute(query)
        
        except Exception as e:
            print(e)
            messages.error(request,"Error in executing SQL Query: "+str(e))
            return render(request, 'tables.html', context)
        else:
            print("Query successful")
    
        
            
  
        
    if 'context' in request.session:
        context = request.session['context']
        
    
    return render(request, 'tables.html', context)
        


def status(request):
    
    victims = Victim.objects.all().values('id','name','mobile')
    context = {'victims':victims}
    if request.method == 'POST' and 'Submit' in request.POST:
        key = request.POST['key']
        if str(key) != '0000':
            messages.error(request,"Entered key is wrong. Please try again.")
            return render(request,'status.html',context)
            
        
            
        victim_id = request.POST['victim_details']
        victim_id = int(victim_id) if victim_id else None
        
        if request.POST['message'] != '':
            v = Victim.objects.get(pk = victim_id)
            ip_address, is_routable = get_client_ip(request)
            v.messages += '\n' + ip_address + '  ' + request.POST['message']
            v.save()
            
        status = Victim.objects.get(pk=victim_id).status
        context = {'victims':victims,'status':status}
        return render(request,'status.html',context)
        
        
        
    
    return render(request,'status.html',context)
        
    



@login_required
def show_all(request):
    for f in os.listdir('/home/sriram/work/MissingPersons/police/static/'):
        try:
            os.remove(os.path.join('/home/sriram/work/MissingPersons/police/static/',f))
            
        except OSError as e:
            print(e)
            continue
            
        else:
            print("{} deleted".format(f))
            
    images = fsfiles.find()
    my_images = []
    names = []
    for i,image in enumerate(images):
        #print(type(image))
        data = fs.get(image["_id"]).read()
        
        ba = bytearray(data)
        # ~ pic = Image.open(io.BytesIO(ba).seek(0))
        # ~ pic.save("/home/sriram/work/MissingPersons/police/static/tmp{}.jpg".format(i))
        
        f1 = open("/home/sriram/work/MissingPersons/police/static/tmp{}.jpg".format(i),'wb')
        f1.write(ba)
        f1.close()
        my_images.append("tmp{}.jpg".format(i))
        names.append(image['filename'])
        
    print(names)
    all_my_images = zip(my_images,names)
    return render(request, "show_all.html",{"my_images":all_my_images})
    
    
@login_required
def facial_recognition(request):
    my_form = OtherImageForm()
    
    for fi in os.listdir('/home/sriram/work/MissingPersons/media/uploads'):
        os.remove(os.path.join('/home/sriram/work/MissingPersons/media/uploads',fi))
    for f in os.listdir('/home/sriram/work/MissingPersons/uploads/'):
        try:
            os.remove(os.path.join('/home/sriram/work/MissingPersons/uploads/',f))
            
        except OSError as e:
            print(e)
            continue
            
        else:
            print("{} deleted".format(f))
            
    for f in os.listdir('/home/sriram/work/MissingPersons/police/static/'):
        try:
            os.remove(os.path.join('/home/sriram/work/MissingPersons/police/static/',f))
            
        except OSError as e:
            print(e)
            continue
            
            
        else:
            print("{} deleted".format(f))
    try:
        if request.method == 'POST':
            print(request.POST)
            print("Type")
            
            person_type = request.POST['img_type'].lower()
                
            # ~ myfile = request.FILES['myfile']
            # ~ fss = FileSystemStorage(location='uploads')
            # ~ filename = fss.save(myfile.name, myfile)
            # ~ uploaded_file_url = fss.url(filename)
            # ~ proper_filename = os.path.abspath(os.path.join('uploads',filename))
            # ~ mugshots_dir = '/home/sriram/work/MissingPersons/police/static/mugshots'
            # ~ dir_imgs = os.listdir(mugshots_dir)
            
            my_form = OtherImageForm(request.POST,request.FILES)
            print("Just befre ccheck")
            if not my_form.is_valid():
                print("Hello")
            
            print(my_form.cleaned_data)

            my_form.save()
            proper_filename = os.path.join('/home/sriram/work/MissingPersons/media/uploads',os.listdir('/home/sriram/work/MissingPersons/media/uploads')[0])
            
            print(proper_filename)
            
            min_results = []
            known_encodings = []
            unknown_image = face_recognition.load_image_file(proper_filename)
            try:
                unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
                
            except IndexError:
                messages.error(request,"No face encodings found for uploaded image")
                return render(request, 'facial_recognition.html',{'my_form':my_form})
            images = fsfiles.find({"filename":{"$regex":person_type}})
            images_list = [x for x in images]
            for img in images_list:            
                
                
                known_encoding = img['ke']
                known_encodings.append(known_encoding)
                

            face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)    
            for i, face_distance in enumerate(face_distances):
                min_results.append(face_distance) 
                
            if len(min_results) == 0:
                messages.error(request,"No images found in selected person type(suspect/victim)")
                return render(request, 'facial_recognition.html',{'my_form':my_form})
            print(min(min_results))
            result_image = images_list[min_results.index(min(min_results))]['filename']
            img_obj = fsfiles.find_one({"filename":result_image})
            #for img_obj in img_objs:
            #print(type(img_obj))
            data = fs.get(img_obj["_id"]).read()
            ba = bytearray(data)
            pic = Image.open(io.BytesIO(ba))
            pic.save("/home/sriram/work/MissingPersons/police/static/{}".format(result_image))
            print(result_image)
            confidence = 100-100*min(min_results)
            for fi in os.listdir('/home/sriram/work/MissingPersons/media/uploads'):
                os.remove(os.path.join('/home/sriram/work/MissingPersons/media/uploads',fi))
            return render(request, 'facial_recognition.html', {'img_name':result_image,'confidence':confidence,'uploaded_file_url':'MongoDB','my_form':my_form})
    
    except MultiValueDictKeyError:
        messages.error(request,"Image file not chosen properly")
        
  
  
    return render(request, 'facial_recognition.html',{'my_form':my_form})
    
    
@login_required
def upload(request):
    for fi in os.listdir('/home/sriram/work/MissingPersons/media/uploads'):
        os.remove(os.path.join('/home/sriram/work/MissingPersons/media/uploads',fi))
    my_form = ImageForm()
    if request.method == 'POST':
        print(request.POST)
    if request.method == 'GET':
        return render(request, 'upload.html',{'my_form':my_form})
    try:
        if request.method == 'POST':
            my_form = ImageForm(request.POST,request.FILES)
            if not my_form.is_valid():
                print("Hello")
                print(my_form.errors)
                print(request.FILES)
            

            my_form.save()
            proper_filename = os.path.join('/home/sriram/work/MissingPersons/media/uploads',os.listdir('/home/sriram/work/MissingPersons/media/uploads')[0])
            
            print(proper_filename)
            if 'victim' not in proper_filename.lower() and 'criminal' not in proper_filename.lower():
                messages.error(request,"File name must contain the word victim or criminal")
                return render(request,'upload.html',{'my_form':my_form})
            f = open(proper_filename,'rb')
            
            
            try:
                known_image = face_recognition.load_image_file(f.name)
                known_encoding = face_recognition.face_encodings(known_image)[0]
                
            except IndexError:
                #messages.error(request,"No face encodings found for uploaded image")
                messages.error(request,"No face encodings found for uploaded image")
                return render(request,'upload.html')

            a = fs.put(f,filename=os.path.basename(f.name),ke=known_encoding.tolist())
            messages.success(request,"Image uploaded successfuly")
            f.close()
            for fi in os.listdir('/home/sriram/work/MissingPersons/media/uploads'):
                os.remove(os.path.join('/home/sriram/work/MissingPersons/media/uploads',fi))
            return render(request,'upload.html',{'uploaded_file_url':'Mongo DB','my_form':my_form})
            
    except MultiValueDictKeyError:
        messages.error(request,"Image file not chosen properly")
        
        
    return render(request,'upload.html',{'my_form':my_form})
            
    
    
        
'''
request.POST 
<QueryDict: {'csrfmiddlewaretoken': ['WWUKda7mF8aLSEmsH3CoSCiovIDnPF21wogJRHWqv6uE4ZQcRwBiLybjd0n0AJD3'], 'name': ['Sriram N C'], 'sex': ['M'], 'dob': ['1990-04-14'], 'mobile': ['9845784933'], 'street': ['318, 6th A Main,  2nd Block', '318, 6th A Main,  2nd Block'], 'area': ['PQR3', 'PQR3'], 'city': ['Bengaluru', 'Bengaluru'], 'state': ['KA', 'KA'], 'eye_colour': ['d'], 'hair_colour': ['e'], 'skin_tone': ['e'], 'possible_suspects': ['1'], 'police_station_id': ['1'], 'comments': ['cie1'], 'status': ['w'], 'messages': ['w'], 'date_time_sighting': ['2000-04-14'], 'Register': ['Register']}>



'''
