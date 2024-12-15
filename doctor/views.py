import email
from email import message
from multiprocessing import context
from turtle import title
from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from hospital_admin.views import prescription_list
from .forms import DoctorUserCreationForm, DoctorForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import cache_control
from hospital.models import User, Patient
from hospital_admin.models import Admin_Information,Clinical_Laboratory_Technician
from .models import Doctor_Information, Appointment, Education, Experience, Prescription_medicine, Report,Specimen,Test, Prescription_test, Prescription, Doctor_review
from hospital_admin.models import Admin_Information,Clinical_Laboratory_Technician, Test_Information
from .models import Doctor_Information, Appointment, Education, Experience, Prescription_medicine, Report,Specimen,Test, Prescription_test, Prescription
from django.db.models import Q, Count
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
import random
import string
from datetime import datetime, timedelta
import datetime
import re
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.html import strip_tags
from io import BytesIO
from urllib import response
from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import Report
from django.views.decorators.csrf import csrf_exempt


from PIL import Image
from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render, redirect
from django.contrib import messages

# Create your views here.

def generate_random_string():
    N = 8
    string_var = ""
    string_var = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=N))
    return string_var

@csrf_exempt
@login_required(login_url="doctor-login")
def doctor_change_password(request,pk):
    doctor = Doctor_Information.objects.get(user_id=pk)
    context={'doctor':doctor}
    if request.method == "POST":
        
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        if new_password == confirm_password:
            
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request,"Password Changed Successfully")
            return redirect("doctor-dashboard")
            
        else:
            messages.error(request,"New Password and Confirm Password is not same")
            return redirect("change-password",pk)
    return render(request, 'doctor-change-password.html',context)

@csrf_exempt
@login_required(login_url="doctor-login")
def schedule_timings(request):
    doctor = Doctor_Information.objects.get(user=request.user)
    context = {'doctor': doctor}
    
    return render(request, 'schedule-timings.html', context)

@csrf_exempt
@login_required(login_url="doctor-login")
def patient_id(request):
    return render(request, 'patient-id.html')

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutDoctor(request):
    user = User.objects.get(id=request.user.id)
    if user.is_doctor:
        user.login_status == "offline"
        user.save()
        logout(request)
    
    messages.success(request, 'User Logged out')
    return render(request,'doctor-login.html')

@csrf_exempt
def doctor_register(request):
    page = 'doctor-register'
    form = DoctorUserCreationForm()

    if request.method == 'POST':
        form = DoctorUserCreationForm(request.POST)
        if form.is_valid():
            # form.save()
            # commit=False --> don't save to database yet (we have a chance to modify object)
            user = form.save(commit=False)
            user.is_doctor = True
            # user.username = user.username.lower()  # lowercase username
            user.save()

            messages.success(request, 'Doctor account was created!')

            # After user is created, we can log them in
            #login(request, user)
            return redirect('doctor-login')

        else:
            messages.error(request, 'An error has occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'doctor-register.html', context)

@csrf_exempt
def doctor_login(request):
    # page = 'patient_login'
    if request.method == 'GET':
        return render(request, 'doctor-login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')
                
        user = authenticate(username=username, password=password)
        
        if user is not None:
            
            login(request, user)
            if request.user.is_doctor:
                # user.login_status = "online"
                # user.save()
                messages.success(request, 'Welcome Doctor!')
                return redirect('doctor-dashboard')
            else:
                messages.error(request, 'Invalid credentials. Not a Doctor')
                return redirect('doctor-logout')   
        else:
            messages.error(request, 'Invalid username or password')
            
    return render(request, 'doctor-login.html')

@csrf_exempt
@login_required(login_url="doctor-login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def doctor_dashboard(request):
        if request.user.is_authenticated:    
            if request.user.is_doctor:
                # doctor = Doctor_Information.objects.get(user_id=pk)
                doctor = Doctor_Information.objects.get(user=request.user)
                # appointments = Appointment.objects.filter(doctor=doctor).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed'))
                current_date = datetime.date.today()
                current_date_str = str(current_date)  
                today_appointments = Appointment.objects.filter(date=current_date_str).filter(doctor=doctor).filter(appointment_status='confirmed')
                
                next_date = current_date + datetime.timedelta(days=1) # next days date 
                next_date_str = str(next_date)  
                next_days_appointment = Appointment.objects.filter(date=next_date_str).filter(doctor=doctor).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
                
                today_patient_count = Appointment.objects.filter(date=current_date_str).filter(doctor=doctor).annotate(count=Count('patient'))
                total_appointments_count = Appointment.objects.filter(doctor=doctor).annotate(count=Count('id'))
            else:
                return redirect('doctor-logout')
            
            context = {'doctor': doctor, 'today_appointments': today_appointments, 'today_patient_count': today_patient_count, 'total_appointments_count': total_appointments_count, 'next_days_appointment': next_days_appointment, 'current_date': current_date_str, 'next_date': next_date_str}
            return render(request, 'doctor-dashboard.html', context)
        else:
            return redirect('doctor-login')
 
@csrf_exempt
@login_required(login_url="doctor-login")
def appointments(request):
    doctor = Doctor_Information.objects.get(user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).filter(appointment_status='pending').order_by('date')
    context = {'doctor': doctor, 'appointments': appointments}
    return render(request, 'appointments.html', context) 
 
@csrf_exempt        
@login_required(login_url="doctor-login")
def accept_appointment(request, pk):
    appointment = Appointment.objects.get(id=pk)
    appointment.appointment_status = 'confirmed'
    appointment.save()
    
    # Mailtrap
    
    patient_email = appointment.patient.email
    patient_name = appointment.patient.name
    patient_username = appointment.patient.username
    patient_serial_number = appointment.patient.serial_number
    doctor_name = appointment.doctor.name

    appointment_serial_number = appointment.serial_number
    appointment_date = appointment.date
    appointment_time = appointment.time
    appointment_status = appointment.appointment_status
    
    subject = "Appointment Acceptance Email"
    
    values = {
            "email":patient_email,
            "name":patient_name,
            "username":patient_username,
            "serial_number":patient_serial_number,
            "doctor_name":doctor_name,
            "appointment_serial_num":appointment_serial_number,
            "appointment_date":appointment_date,
            "appointment_time":appointment_time,
            "appointment_status":appointment_status,
    }
    
    html_message = render_to_string('appointment_accept_mail.html', {'values': values})
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(subject, plain_message, 'hospital_admin@gmail.com',  [patient_email], html_message=html_message, fail_silently=False)
    except BadHeaderError:
        return HttpResponse('Invalid header found')
    
    messages.success(request, 'Appointment Accepted')
    
    return redirect('doctor-dashboard')

@csrf_exempt
@login_required(login_url="doctor-login")
def reject_appointment(request, pk):
    appointment = Appointment.objects.get(id=pk)
    appointment.appointment_status = 'cancelled'
    appointment.save()
    
    # Mailtrap
    
    patient_email = appointment.patient.email
    patient_name = appointment.patient.name
    doctor_name = appointment.doctor.name

    subject = "Appointment Rejection Email"
    
    values = {
            "email":patient_email,
            "name":patient_name,
            "doctor_name":doctor_name,
    }
    
    html_message = render_to_string('appointment_reject_mail.html', {'values': values})
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(subject, plain_message, 'hospital_admin@gmail.com',  [patient_email], html_message=html_message, fail_silently=False)
    except BadHeaderError:
        return HttpResponse('Invalid header found')
    
    messages.error(request, 'Appointment Rejected')
    
    return redirect('doctor-dashboard')


#         end_year = doctor.end_year
#         end_year = re.sub("'", "", end_year)
#         end_year = end_year.replace("[", "")
#         end_year = end_year.replace("]", "")
#         end_year = end_year.replace(",", "")
#         end_year_array = end_year.split()       
#         experience = zip(work_place_array, designation_array, start_year_array, end_year_array)

@csrf_exempt
@login_required(login_url="doctor-login")
def doctor_profile(request, pk):
    # request.user --> get logged in user
    if request.user.is_patient:
        patient = request.user.patient
    else:
        patient = None
    
    doctor = Doctor_Information.objects.get(doctor_id=pk)
    # doctor = Doctor_Information.objects.filter(doctor_id=pk).order_by('-doctor_id')
    
    educations = Education.objects.filter(doctor=doctor).order_by('-year_of_completion')
    experiences = Experience.objects.filter(doctor=doctor).order_by('-from_year','-to_year')
    doctor_review = Doctor_review.objects.filter(doctor=doctor)
            
    context = {'doctor': doctor, 'patient': patient, 'educations': educations, 'experiences': experiences, 'doctor_review': doctor_review}
    return render(request, 'doctor-profile.html', context)

@csrf_exempt
@login_required(login_url="doctor-login")
def delete_education(request, pk):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        
        educations = Education.objects.get(education_id=pk)
        educations.delete()
        
        messages.success(request, 'Education Deleted')
        return redirect('doctor-profile-settings')

@csrf_exempt  
@login_required(login_url="doctor-login")
def delete_experience(request, pk):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        
        experiences = Experience.objects.get(experience_id=pk)
        experiences.delete()
        
        messages.success(request, 'Experience Deleted')
        return redirect('doctor-profile-settings')
      
def is_valid_image(file: UploadedFile) -> bool:
    """Check if the uploaded file is a valid image."""
    try:
        img = Image.open(file)
        img.verify()  # Ensure the image is valid
        print(f"🖼️ Image uploaded successfully: {file.name}")
        return True
    except (IOError, Exception) as e:
        print(f"❌ Invalid image file: {file.name} | Error: {str(e)}")
        return False
    
@csrf_exempt      
@login_required(login_url="doctor-login")
def doctor_profile_settings(request):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        old_featured_image = doctor.featured_image

        if request.method == 'GET':
            educations = Education.objects.filter(doctor=doctor)
            experiences = Experience.objects.filter(doctor=doctor)
            
            context = {'doctor': doctor, 'educations': educations, 'experiences': experiences}
            return render(request, 'doctor-profile-settings.html', context)

        elif request.method == 'POST':
            featured_image = old_featured_image

            if 'featured_image' in request.FILES:
                uploaded_file = request.FILES['featured_image']
                if is_valid_image(uploaded_file):
                    featured_image = uploaded_file
                else:
                    messages.error(request, "Uploaded file is not a valid image. Please try again.")
                    print(f"🚫 User uploaded an invalid file: {uploaded_file.name}")
                    return redirect('doctor-profile-settings')

            # Update doctor's main information
            doctor.name = request.POST.get('name')
            doctor.phone_number = request.POST.get('number')
            doctor.gender = request.POST.get('gender')
            doctor.dob = request.POST.get('dob')
            doctor.description = request.POST.get('description')
            doctor.consultation_fee = request.POST.get('consultation_fee')
            doctor.report_fee = request.POST.get('report_fee')
            doctor.nid = request.POST.get('nid')
            doctor.visiting_hour = request.POST.get('visit_hour')
            doctor.featured_image = featured_image
            doctor.save()
            
            print(f"✅ Doctor profile updated successfully for user: {request.user.username}")

            # Update Education
            degree = request.POST.getlist('degree')
            institute = request.POST.getlist('institute')
            year_complete = request.POST.getlist('year_complete')

            Education.objects.filter(doctor=doctor).delete()
            for i in range(len(degree)):
                education = Education(
                    doctor=doctor,
                    degree=degree[i],
                    institute=institute[i],
                    year_of_completion=year_complete[i]
                )
                education.save()
            print(f"📚 Education details updated for doctor: {request.user.username}")

            # Update Experience
            hospital_name = request.POST.getlist('hospital_name')
            start_year = request.POST.getlist('from')
            end_year = request.POST.getlist('to')
            designation = request.POST.getlist('designation')

            Experience.objects.filter(doctor=doctor).delete()
            for i in range(len(hospital_name)):
                experience = Experience(
                    doctor=doctor,
                    work_place_name=hospital_name[i],
                    from_year=start_year[i],
                    to_year=end_year[i],
                    designation=designation[i]
                )
                experience.save()
            print(f"🏥 Experience details updated for doctor: {request.user.username}")

            messages.success(request, 'Profile Updated 🎉')
            return redirect('doctor-dashboard')
    else:
        print(f"⚠️ Unauthorized access attempt by user: {request.user.username}")
        return redirect('doctor-logout')
               
@csrf_exempt    
@login_required(login_url="doctor-login")      
def booking_success(request):
    return render(request, 'booking-success.html')

@csrf_exempt
@login_required(login_url="doctor-login")
def booking(request, pk):
    patient = request.user.patient
    doctor = Doctor_Information.objects.get(doctor_id=pk)

    if request.method == 'POST':
        appointment = Appointment(patient=patient, doctor=doctor)
        date = request.POST['appoint_date']
        time = request.POST['appoint_time']
        appointment_type = request.POST['appointment_type']
        message = request.POST['message']

    
        transformed_date = datetime.datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
        transformed_date = str(transformed_date)
         
        appointment.date = transformed_date
        appointment.time = time
        appointment.appointment_status = 'pending'
        appointment.serial_number = generate_random_string()
        appointment.appointment_type = appointment_type
        appointment.message = message
        appointment.save()
        
        if message:
            # Mailtrap
            patient_email = appointment.patient.email
            patient_name = appointment.patient.name
            patient_username = appointment.patient.username
            patient_phone_number = appointment.patient.phone_number
            doctor_name = appointment.doctor.name
        
            subject = "Appointment Request"
            
            values = {
                    "email":patient_email,
                    "name":patient_name,
                    "username":patient_username,
                    "phone_number":patient_phone_number,
                    "doctor_name":doctor_name,
                    "message":message,
                }
            
            html_message = render_to_string('appointment-request-mail.html', {'values': values})
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(subject, plain_message, 'hospital_admin@gmail.com',  [patient_email], html_message=html_message, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found')
        
        
        messages.success(request, 'Appointment Booked')
        return redirect('patient-dashboard')

    context = {'patient': patient, 'doctor': doctor}
    return render(request, 'booking.html', context)

@csrf_exempt
@login_required(login_url="doctor-login")
def my_patients(request):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        appointments = Appointment.objects.filter(doctor=doctor).filter(appointment_status='confirmed')
        # patients = Patient.objects.all()
    else:
        redirect('doctor-logout')
    
    
    context = {'doctor': doctor, 'appointments': appointments}
    return render(request, 'my-patients.html', context)


# def patient_profile(request):
#     return render(request, 'patient_profile.html')

@csrf_exempt
@login_required(login_url="doctor-login")
def patient_profile(request, pk):
    if request.user.is_doctor:
        # doctor = Doctor_Information.objects.get(user_id=pk)
        doctor = Doctor_Information.objects.get(user=request.user)
        patient = Patient.objects.get(patient_id=pk)
        appointments = Appointment.objects.filter(doctor=doctor).filter(patient=patient)
        prescription = Prescription.objects.filter(doctor=doctor).filter(patient=patient)
        report = Report.objects.filter(doctor=doctor).filter(patient=patient) 
    else:
        redirect('doctor-logout')
    context = {'doctor': doctor, 'appointments': appointments, 'patient': patient, 'prescription': prescription, 'report': report}  
    return render(request, 'patient-profile.html', context)


@csrf_exempt
@login_required(login_url="doctor-login")
def create_prescription(request, pk):
    if request.user.is_doctor:
        try:
            doctor = Doctor_Information.objects.get(user=request.user)
            print("👨‍⚕️ Doctor retrieved:", doctor)
        except Doctor_Information.DoesNotExist:
            print("❌ Error: Doctor profile not found for user:", request.user)
            messages.error(request, "Doctor profile not found.")
            return redirect('logout')

        try:
            patient = Patient.objects.get(patient_id=pk)
            print("👤 Patient retrieved:", patient)
        except Patient.DoesNotExist:
            print("❌ Error: Patient with ID", pk, "does not exist.")
            messages.error(request, "Patient not found.")
            return redirect('doctor-dashboard')  # Adjust as needed

        create_date = datetime.date.today()
        print("📅 Prescription creation date:", create_date)

        if request.method == 'POST':
            print("📥 POST request received to create prescription.")

            # Retrieve POST data
            test_name = request.POST.getlist('test_name')
            test_description = request.POST.getlist('description')
            medicine_name = request.POST.getlist('medicine_name')
            medicine_quantity = request.POST.getlist('quantity')
            medecine_frequency = request.POST.getlist('frequency')
            medicine_duration = request.POST.getlist('duration')
            medicine_relation_with_meal = request.POST.getlist('relation_with_meal')
            medicine_instruction = request.POST.getlist('instruction')
            extra_information = request.POST.get('extra_information')
            test_info_id = request.POST.getlist('id')

            print("📝 POST Data Retrieved:")
            print("   - Test Names:", test_name)
            print("   - Test Descriptions:", test_description)
            print("   - Medicine Names:", medicine_name)
            print("   - Quantities:", medicine_quantity)
            print("   - Frequencies:", medecine_frequency)
            print("   - Durations:", medicine_duration)
            print("   - Relation with Meal:", medicine_relation_with_meal)
            print("   - Instructions:", medicine_instruction)
            print("   - Extra Information:", extra_information)
            print("   - Test Info IDs:", test_info_id)

            # Create Prescription
            prescription = Prescription(doctor=doctor, patient=patient)
            prescription.extra_information = extra_information
            prescription.create_date = create_date
            prescription.save()
            print("✅ Prescription created with ID:", prescription.prescription_id)

            # Add Medicines
            for i in range(len(medicine_name)):
                medicine = Prescription_medicine(
                    prescription=prescription,
                    medicine_name=medicine_name[i],
                    quantity=medicine_quantity[i],
                    frequency=medecine_frequency[i],
                    duration=medicine_duration[i],
                    relation_with_meal=medicine_relation_with_meal[i],
                    instruction=medicine_instruction[i]
                )
                medicine.save()
                print(f"💊 Medicine {i+1} added:", medicine)

            # Add Tests
            for i in range(len(test_name)):
                try:
                    test_info = Test_Information.objects.get(test_id=test_info_id[i])
                    print(f"🔍 Test Info {i+1} retrieved:", test_info)
                except Test_Information.DoesNotExist:
                    print(f"❌ Error: Test Information with ID {test_info_id[i]} does not exist.")
                    messages.error(request, f"Test Information with ID {test_info_id[i]} does not exist.")
                    continue  # Skip this test

                tests = Prescription_test(
                    prescription=prescription,
                    test_name=test_name[i],
                    test_description=test_description[i],
                    test_info_id=test_info_id[i],
                    test_info_price=test_info.test_price
                )
                tests.save()
                print(f"🧪 Test {i+1} added:", tests)

            messages.success(request, '✅ Prescription Created Successfully!')
            print("✅ Success message sent to user.")

            return redirect('patient-profile', pk=patient.patient_id)
        else:
            print("📄 GET request received. Rendering 'create-prescription.html'.")
            context = {'doctor': doctor, 'patient': patient}
            return render(request, 'create-prescription.html', context)
    else:
        print("🔒 Unauthorized access attempt by user:", request.user)
        return redirect('logout')
        
@csrf_exempt      
def render_to_pdf(template_src, context_dict={}):
    
    template=get_template(template_src)
    html=template.render(context_dict)
    result=BytesIO()
    pdf=pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    
    if not pdf.err:
        return HttpResponse(result.getvalue(),content_type="aplication/pdf")
    return None

@csrf_exempt
def report_pdf(request, pk):
 if request.user.is_patient:
    patient = Patient.objects.get(user=request.user)
    report = Report.objects.get(report_id=pk)
    specimen = Specimen.objects.filter(report=report)
    test = Test.objects.filter(report=report)
    # current_date = datetime.date.today()
    context={'patient':patient,'report':report,'test':test,'specimen':specimen}
    pdf=render_to_pdf('report_pdf.html', context)
    if pdf:
        response=HttpResponse(pdf, content_type='application/pdf')
        content="inline; filename=report.pdf"
        # response['Content-Disposition']= content
        return response
    print("Report Clikced")
    return HttpResponse("Not Found")


# def testing(request):
#     doctor = Doctor_Information.objects.get(user=request.user)
#     degree = doctor.degree
#     degree = re.sub("'", "", degree)
#     degree = degree.replace("[", "")
#     degree = degree.replace("]", "")
#     degree = degree.replace(",", "")
#     degree_array = degree.split()
    
#     education = zip(degree_array, institute_array)
    
#     context = {'doctor': doctor, 'degree': institute, 'institute_array': institute_array, 'education': education}
#     # test range, len, and loop to show variables before moving on to doctor profile
    
#     return render(request, 'testing.html', context)

@csrf_exempt
@login_required(login_url="login")
def patient_search(request, pk):
    if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(doctor_id=pk)
        id = int(request.GET['search_query'])
        patient = Patient.objects.get(patient_id=id)
        prescription = Prescription.objects.filter(doctor=doctor).filter(patient=patient)
        context = {'patient': patient, 'doctor': doctor, 'prescription': prescription}
        return render(request, 'patient-profile.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'doctor-login.html')

@csrf_exempt
@login_required(login_url="login")
def doctor_test_list(request):
    if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        tests = Test_Information.objects.all
        context = {'doctor': doctor, 'tests': tests}
        return render(request, 'doctor-test-list.html', context)
    
    elif request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        tests = Test_Information.objects.all
        context = {'patient': patient, 'tests': tests}
        return render(request, 'doctor-test-list.html', context)
        
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'doctor-login.html')


@csrf_exempt
@login_required(login_url="login")
def doctor_view_prescription(request, pk):
    if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        prescriptions = Prescription.objects.get(prescription_id=pk)
        medicines = Prescription_medicine.objects.filter(prescription=prescriptions)
        tests = Prescription_test.objects.filter(prescription=prescriptions)
        context = {'prescription': prescriptions, 'medicines': medicines, 'tests': tests, 'doctor': doctor}
        return render(request, 'doctor-view-prescription.html', context)

@csrf_exempt
@login_required(login_url="login")
def doctor_view_report(request, pk):
    if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        report = Report.objects.get(report_id=pk)
        specimen = Specimen.objects.filter(report=report)
        test = Test.objects.filter(report=report)
        context = {'report': report, 'test': test, 'specimen': specimen, 'doctor': doctor}
        return render(request, 'doctor-view-report.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'doctor-login.html')


@csrf_exempt
@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):    
    user.login_status = True
    user.save()

@csrf_exempt
@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):   
    user.login_status = False
    user.save()

@csrf_exempt
@login_required(login_url="login")
def doctor_review(request, pk):
    if request.user.is_doctor:
        # doctor = Doctor_Information.objects.get(user_id=pk)
        doctor = Doctor_Information.objects.get(user=request.user)
            
        doctor_review = Doctor_review.objects.filter(doctor=doctor)
        
        context = {'doctor': doctor, 'doctor_review': doctor_review}  
        return render(request, 'doctor-profile.html', context)

    if request.user.is_patient:
        doctor = Doctor_Information.objects.get(doctor_id=pk)
        patient = Patient.objects.get(user=request.user)

        if request.method == 'POST':
            title = request.POST.get('title')
            message = request.POST.get('message')
            
            doctor_review = Doctor_review(doctor=doctor, patient=patient, title=title, message=message)
            doctor_review.save()

        context = {'doctor': doctor, 'patient': patient, 'doctor_review': doctor_review}  
        return render(request, 'doctor-profile.html', context)
    else:
        logout(request)
 
 
   
 


