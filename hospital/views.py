import email
from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, PatientForm, PasswordResetForm
from hospital.models import Hospital_Information, User, Patient 
from doctor.models import Test, testCart, testOrder
from hospital_admin.models import hospital_department, specialization, service, Test_Information
from django.views.decorators.cache import cache_control
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
import datetime
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.template.loader import get_template
from xhtml2pdf import pisa
from .utils import searchDoctors, searchHospitals, searchDepartmentDoctors, paginateHospitals
from .models import Patient, User
from doctor.models import Doctor_Information, Appointment,Report, Specimen, Test, Prescription, Prescription_medicine, Prescription_test
from sslcommerz.models import Payment
from django.db.models import Q, Count
import re
from io import BytesIO
from urllib import response
from django.core.mail import BadHeaderError, send_mail
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt


from PIL import Image
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib import messages

# Create your views here.
@csrf_exempt
def hospital_home(request):
    # .order_by('-created_at')[:6]
    doctors = Doctor_Information.objects.filter(register_status='Accepted')
    hospitals = Hospital_Information.objects.all()
    context = {'doctors': doctors, 'hospitals': hospitals} 
    return render(request, 'index-2.html', context)

@csrf_exempt
@login_required(login_url="login")
def change_password(request,pk):
    patient = Patient.objects.get(user_id=pk)
    context={"patient":patient}
    if request.method == "POST":
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        if new_password == confirm_password:
            
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request,"Password Changed Successfully")
            return redirect("patient-dashboard")
        else:
            messages.error(request,"New Password and Confirm Password is not same")
            return redirect("change-password",pk)
    return render(request, 'change-password.html',context)


def add_billing(request):
    return render(request, 'add-billing.html')

def appointments(request):
    return render(request, 'appointments.html')

def edit_billing(request):
    return render(request, 'edit-billing.html')

def edit_prescription(request):
    return render(request, 'edit-prescription.html')

# def forgot_password(request):
#     return render(request, 'forgot-password.html')

@csrf_exempt
def resetPassword(request):
    form = PasswordResetForm()

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user_email = user.email
       
            subject = "Password Reset Requested"
            # email_template_name = "password_reset_email.txt"
            values = {
				"email":user.email,
				'domain':'127.0.0.1:8000',
				'site_name': 'Website',
				"uid": urlsafe_base64_encode(force_bytes(user.pk)),
				"user": user,
				'token': default_token_generator.make_token(user),
				'protocol': 'http',
			}

            html_message = render_to_string('mail_template.html', {'values': values})
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(subject, plain_message, 'admin@example.com',  [user.email], html_message=html_message, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect ("password_reset_done")

    context = {'form': form}
    return render(request, 'reset_password.html', context)
    
    
def privacy_policy(request):
    return render(request, 'privacy-policy.html')

def about_us(request):
    return render(request, 'about-us.html')

@csrf_exempt
@login_required(login_url="login")
def chat(request, pk):
    patient = Patient.objects.get(user_id=pk)
    doctors = Doctor_Information.objects.all()

    context = {'patient': patient, 'doctors': doctors}
    return render(request, 'chat.html', context)

@csrf_exempt
@login_required(login_url="login")
def chat_doctor(request):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        patients = Patient.objects.all()
        
    context = {'patients': patients, 'doctor': doctor}
    return render(request, 'chat-doctor.html', context)

@csrf_exempt     
@login_required(login_url="login")
def pharmacy_shop(request):
    return render(request, 'pharmacy/shop.html')

@csrf_exempt
def login_user(request):
    page = 'patient_login'
    if request.method == 'GET':
        return render(request, 'patient-login.html')
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
            if request.user.is_patient:   
                messages.success(request, 'User Logged in Successfully')    
                return redirect('patient-dashboard')
            else:
                messages.error(request, 'Invalid credentials. Not a Patient')
                return redirect('logout')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'patient-login.html')

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutUser(request):
    logout(request)
    messages.success(request, 'User Logged out')
    return redirect('login')

@csrf_exempt
def patient_register(request):
    page = 'patient-register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # form.save()
            user = form.save(commit=False) # commit=False --> don't save to database yet (we have a chance to modify object)
            user.is_patient = True
            # user.username = user.username.lower()  # lowercase username
            user.save()
            messages.success(request, 'Patient account was created!')

            # After user is created, we can log them in --> login(request, user)
            return redirect('login')

        else:
            messages.error(request, 'An error has occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'patient-register.html', context)

@csrf_exempt
@login_required(login_url="login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def patient_dashboard(request):
    if request.user.is_patient:
        # patient = Patient.objects.get(user_id=pk)
        patient = Patient.objects.get(user=request.user)
        report = Report.objects.filter(patient=patient)
        prescription = Prescription.objects.filter(patient=patient).order_by('-prescription_id')
        appointments = Appointment.objects.filter(patient=patient).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed'))
        payments = Payment.objects.filter(patient=patient).filter(appointment__in=appointments).filter(payment_type='appointment').filter(status='VALID')
        context = {'patient': patient, 'appointments': appointments, 'payments': payments,'report':report,'prescription':prescription}
    else:
        return redirect('logout')
        
    return render(request, 'patient-dashboard.html', context)


# def profile_settings(request):
#     if request.user.is_patient:
#         # patient = Patient.objects.get(user_id=pk)
#         patient = Patient.objects.get(user=request.user)
#         form = PatientForm(instance=patient)  

#         if request.method == 'POST':
#             form = PatientForm(request.POST, request.FILES,instance=patient)  
#             if form.is_valid():
#                 form.save()
#                 return redirect('patient-dashboard')
#             else:
#                 form = PatientForm()
#     else:
#         redirect('logout')

#     context = {'patient': patient, 'form': form}
#     return render(request, 'profile-settings.html', context)


def is_valid_image(file: UploadedFile) -> bool:
    """Check if the uploaded file is a valid image."""
    try:
        # Try to open the image to verify it's valid
        img = Image.open(file)
        img.verify()  # Check if the image is corrupted
        print(f"🖼️ Image uploaded successfully: {file.name}")
        return True
    except (IOError, ValidationError) as e:
        print(f"❌ Invalid image file: {file.name} | Error: {str(e)}")
        return False

@csrf_exempt
@login_required(login_url="login")
def profile_settings(request):
    if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        old_featured_image = patient.featured_image

        if request.method == 'GET':
            context = {'patient': patient}
            return render(request, 'profile-settings.html', context)

        elif request.method == 'POST':
            featured_image = old_featured_image

            # Check if an image was uploaded
            if 'featured_image' in request.FILES:
                uploaded_file = request.FILES['featured_image']
                if is_valid_image(uploaded_file):
                    featured_image = uploaded_file
                else:
                    messages.error(request, "Uploaded file is not a valid image. Please try again.")
                    print(f"🚫 User uploaded an invalid file: {uploaded_file.name}")
                    return redirect('profile-settings')

            # Update patient details with POST data
            patient.name = request.POST.get('name')
            patient.dob = request.POST.get('dob')
            patient.age = request.POST.get('age')
            patient.blood_group = request.POST.get('blood_group')
            patient.phone_number = request.POST.get('phone_number')
            patient.address = request.POST.get('address')
            patient.weight = request.POST.get('weight')
            patient.nid = request.POST.get('nid')
            patient.history = request.POST.get('history')
            patient.featured_image = featured_image

            # Save updated patient data
            patient.save()
            messages.success(request, 'Profile Settings Changed! 🎉')
            print(f"✅ Profile updated successfully for user: {request.user.username}")
            return redirect('patient-dashboard')

    else:
        print(f"⚠️ Unauthorized access attempt by user: {request.user.username}")
        return redirect('logout')     
@csrf_exempt
@login_required(login_url="login")
def search(request):
    if request.user.is_authenticated and request.user.is_patient:
        # patient = Patient.objects.get(user_id=pk)
        patient = Patient.objects.get(user=request.user)
        doctors = Doctor_Information.objects.filter(register_status='Accepted')
        
        doctors, search_query = searchDoctors(request)
        context = {'patient': patient, 'doctors': doctors, 'search_query': search_query}
        return render(request, 'search.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')    
    

def checkout_payment(request):
    return render(request, 'checkout.html')

@csrf_exempt
@login_required(login_url="login")
def multiple_hospital(request):
    
    if request.user.is_authenticated: 
        
        if request.user.is_patient:
            # patient = Patient.objects.get(user_id=pk)
            patient = Patient.objects.get(user=request.user)
            doctors = Doctor_Information.objects.all()
            hospitals = Hospital_Information.objects.all()
            
            hospitals, search_query = searchHospitals(request)
            
            # PAGINATION ADDED TO MULTIPLE HOSPITALS
            custom_range, hospitals = paginateHospitals(request, hospitals, 3)
        
            context = {'patient': patient, 'doctors': doctors, 'hospitals': hospitals, 'search_query': search_query, 'custom_range': custom_range}
            return render(request, 'multiple-hospital.html', context)
        
        elif request.user.is_doctor:
            doctor = Doctor_Information.objects.get(user=request.user)
            hospitals = Hospital_Information.objects.all()
            
            hospitals, search_query = searchHospitals(request)
            
            context = {'doctor': doctor, 'hospitals': hospitals, 'search_query': search_query}
            return render(request, 'multiple-hospital.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html') 
    
@csrf_exempt    
@login_required(login_url="login")
def hospital_profile(request, pk):
    
    if request.user.is_authenticated: 
        
        if request.user.is_patient:
            patient = Patient.objects.get(user=request.user)
            doctors = Doctor_Information.objects.all()
            hospitals = Hospital_Information.objects.get(hospital_id=pk)
        
            departments = hospital_department.objects.filter(hospital=hospitals)
            specializations = specialization.objects.filter(hospital=hospitals)
            services = service.objects.filter(hospital=hospitals)
            
            # department_list = None
            # for d in departments:
            #     vald = d.hospital_department_name
            #     vald = re.sub("'", "", vald)
            #     vald = vald.replace("[", "")
            #     vald = vald.replace("]", "")
            #     vald = vald.replace(",", "")
            #     department_list = vald.split()
            
            context = {'patient': patient, 'doctors': doctors, 'hospitals': hospitals, 'departments': departments, 'specializations': specializations, 'services': services}
            return render(request, 'hospital-profile.html', context)
        
        elif request.user.is_doctor:
           
            doctor = Doctor_Information.objects.get(user=request.user)
            hospitals = Hospital_Information.objects.get(hospital_id=pk)
            
            departments = hospital_department.objects.filter(hospital=hospitals)
            specializations = specialization.objects.filter(hospital=hospitals)
            services = service.objects.filter(hospital=hospitals)
            
            context = {'doctor': doctor, 'hospitals': hospitals, 'departments': departments, 'specializations': specializations, 'services': services}
            return render(request, 'hospital-profile.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html') 
    
    
def data_table(request):
    return render(request, 'data-table.html')

@csrf_exempt
@login_required(login_url="login")
def hospital_department_list(request, pk):
    if request.user.is_authenticated: 
        
        if request.user.is_patient:
            # patient = Patient.objects.get(user_id=pk)
            patient = Patient.objects.get(user=request.user)
            doctors = Doctor_Information.objects.all()
            
            hospitals = Hospital_Information.objects.get(hospital_id=pk)
            departments = hospital_department.objects.filter(hospital=hospitals)
        
            context = {'patient': patient, 'doctors': doctors, 'hospitals': hospitals, 'departments': departments}
            return render(request, 'hospital-department.html', context)
        
        elif request.user.is_doctor:
            doctor = Doctor_Information.objects.get(user=request.user)
            hospitals = Hospital_Information.objects.get(hospital_id=pk)
            departments = hospital_department.objects.filter(hospital=hospitals)
            
            context = {'doctor': doctor, 'hospitals': hospitals, 'departments': departments}
            return render(request, 'hospital-department.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html')

@csrf_exempt
@login_required(login_url="login")
def hospital_doctor_list(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        # patient = Patient.objects.get(user_id=pk)
        patient = Patient.objects.get(user=request.user)
        departments = hospital_department.objects.get(hospital_department_id=pk)
        doctors = Doctor_Information.objects.filter(department_name=departments)
        
        doctors, search_query = searchDepartmentDoctors(request, pk)
        
        context = {'patient': patient, 'department': departments, 'doctors': doctors, 'search_query': search_query, 'pk_id': pk}
        return render(request, 'hospital-doctor-list.html', context)

    elif request.user.is_authenticated and request.user.is_doctor:
        # patient = Patient.objects.get(user_id=pk)
        
        doctor = Doctor_Information.objects.get(user=request.user)
        departments = hospital_department.objects.get(hospital_department_id=pk)
        
        doctors = Doctor_Information.objects.filter(department_name=departments)
        doctors, search_query = searchDepartmentDoctors(request, pk)
        
        context = {'doctor':doctor, 'department': departments, 'doctors': doctors, 'search_query': search_query, 'pk_id': pk}
        return render(request, 'hospital-doctor-list.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')   
    


@csrf_exempt
@login_required(login_url="login")
def hospital_doctor_register(request, pk):
    print("🚀 Function `hospital_doctor_register` called.")
    print(f"📡 Request Method: {request.method}")
    print(f"👤 User: {request.user}")

    if request.user.is_authenticated:
        print("🛡 User is authenticated.")
        
        if getattr(request.user, 'is_doctor', False):
            print("👨‍⚕️ User is identified as a doctor.")
            
            try:
                doctor = Doctor_Information.objects.get(user=request.user)
                print(f"🔍 Retrieved Doctor Information: {doctor}")
            except Doctor_Information.DoesNotExist:
                print("❌ Error: Doctor_Information does not exist for the authenticated user.")
                messages.error(request, 'Doctor information not found.')
                return redirect('doctor-dashboard')
            
            try:
                hospitals = Hospital_Information.objects.get(hospital_id=pk)
                print(f"🏥 Retrieved Hospital Information: {hospitals}")
            except Hospital_Information.DoesNotExist:
                print(f"❌ Error: Hospital with ID {pk} does not exist.")
                messages.error(request, 'Hospital not found.')
                return redirect('doctor-dashboard')
            
            departments = hospital_department.objects.filter(hospital=hospitals)
            specializations = specialization.objects.filter(hospital=hospitals)
            print(f"📂 Retrieved Departments: {departments}")
            print(f"🔬 Retrieved Specializations: {specializations}")
            
            if request.method == 'POST':
                print("📥 Processing POST request.")
                print(f"📑 POST Data: {request.POST}")
                print(f"📁 FILES Data: {request.FILES}")
                
                # Handle certificate_image
                if 'certificate_image' in request.FILES:
                    certificate_image = request.FILES['certificate_image']
                    print(f"🖼 Certificate Image Uploaded: {certificate_image.name}")
                else:
                    certificate_image = "doctors_certificate/default.png"
                    print("🖼 No Certificate Image uploaded. Using default image.")
                
                # Retrieve selected department and specialization
                department_id_selected = request.POST.get('department_radio')
                specialization_id_selected = request.POST.get('specialization_radio')
                print(f"📌 Selected Department ID: {department_id_selected}")
                print(f"📌 Selected Specialization ID: {specialization_id_selected}")
                
                # Validate and fetch department_chosen
                try:
                    department_chosen = hospital_department.objects.get(hospital_department_id=department_id_selected)
                    print(f"✅ Department Chosen: {department_chosen}")
                except hospital_department.DoesNotExist:
                    print(f"❌ Error: Selected department ID {department_id_selected} does not exist.")
                    messages.error(request, 'Selected department does not exist.')
                    return redirect('hospital_doctor_register', pk=pk)
                
                # Validate and fetch specialization_chosen
                try:
                    specialization_chosen = specialization.objects.get(specialization_id=specialization_id_selected)
                    print(f"✅ Specialization Chosen: {specialization_chosen}")
                except specialization.DoesNotExist:
                    print(f"❌ Error: Selected specialization ID {specialization_id_selected} does not exist.")
                    messages.error(request, 'Selected specialization does not exist.')
                    return redirect('hospital_doctor_register', pk=pk)
                
                # Update doctor information
                doctor.department_name = department_chosen
                doctor.specialization = specialization_chosen
                doctor.register_status = 'Pending'
                doctor.certificate_image = certificate_image
                print("📝 Updated Doctor Information with selected department and specialization.")
                
                # Save the updated doctor information
                doctor.save()
                print("💾 Doctor information saved successfully.")
                
                # Send success message and redirect
                messages.success(request, 'Hospital Registration Request Sent 🎉')
                print("✅ Success message sent to the user.")
                
                return redirect('doctor-dashboard')
            
            # Prepare context for rendering the template
            context = {
                'doctor': doctor, 
                'hospitals': hospitals, 
                'departments': departments, 
                'specializations': specializations
            }
            print(f"📄 Rendering 'hospital-doctor-register.html' with context: {context}")
            return render(request, 'hospital-doctor-register.html', context)
    else:
        # Handle unauthorized access
        logout(request)
        messages.info(request, 'Not Authorized 🚫')
        print("🔓 User not authenticated. Logged out and redirected to login page.")
        return render(request, 'doctor-login.html')
   
def testing(request):
    # hospitals = Hospital_Information.objects.get(hospital_id=1)
    test = "test"
    context = {'test': test}
    return render(request, 'testing.html', context)

@csrf_exempt
@login_required(login_url="login")
def view_report(request,pk):
    if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        report = Report.objects.filter(report_id=pk)
        specimen = Specimen.objects.filter(report__in=report)
        test = Test.objects.filter(report__in=report)

        # current_date = datetime.date.today()
        context = {'patient':patient,'report':report,'test':test,'specimen':specimen}
        return render(request, 'view-report.html',context)
    else:
        redirect('logout') 


def test_cart(request):
    return render(request, 'test-cart.html')

@csrf_exempt
@login_required(login_url="login")
def test_single(request,pk):
     if request.user.is_authenticated and request.user.is_patient:
         
        patient = Patient.objects.get(user=request.user)
        Perscription_test = Perscription_test.objects.get(test_id=pk)
        carts = testCart.objects.filter(user=request.user, purchased=False)
        
        context = {'patient': patient, 'carts': carts, 'Perscription_test': Perscription_test}
        return render(request, 'test-cart.html',context)
     else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html')  

@csrf_exempt
@login_required(login_url="login")
def test_add_to_cart(request, pk, pk2):
    if request.user.is_authenticated and request.user.is_patient:
         
        patient = Patient.objects.get(user=request.user)
        test_information = Test_Information.objects.get(test_id=pk2)
        prescription = Prescription.objects.filter(prescription_id=pk)

        item = get_object_or_404(Prescription_test, test_info_id=pk2,prescription_id=pk)
        order_item = testCart.objects.get_or_create(item=item, user=request.user, purchased=False)
        order_qs = testOrder.objects.filter(user=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            order.orderitems.add(order_item[0])
            # messages.info(request, "This test is added to your cart!")
            return redirect("prescription-view", pk=pk)
        else:
            order = testOrder(user=request.user)
            order.save()
            order.orderitems.add(order_item[0])
            return redirect("prescription-view", pk=pk)

        context = {'patient': patient,'prescription_test': prescription_tests,'prescription':prescription,'prescription_medicine':prescription_medicine,'test_information':test_information}
        return render(request, 'prescription-view.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html')  

@csrf_exempt
@login_required(login_url="login")
def test_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        # prescription = Prescription.objects.filter(prescription_id=pk)
        
        prescription = Prescription.objects.filter(prescription_id=pk)
        
        patient = Patient.objects.get(user=request.user)
        prescription_test = Prescription_test.objects.all()
        test_carts = testCart.objects.filter(user=request.user, purchased=False)
        test_orders = testOrder.objects.filter(user=request.user, ordered=False)
        
        if test_carts.exists() and test_orders.exists():
            test_order = test_orders[0]
            
            context = {'test_carts': test_carts,'test_order': test_order, 'patient': patient, 'prescription_test':prescription_test, 'prescription_id':pk}
            return render(request, 'test-cart.html', context)
        else:
            # messages.warning(request, "You don't have any test in your cart!")
            context = {'patient': patient,'prescription_test':prescription_test}
            return render(request, 'prescription-view.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html') 

@csrf_exempt
@login_required(login_url="login")
def test_remove_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        item = Prescription_test.objects.get(test_id=pk)

        patient = Patient.objects.get(user=request.user)
        prescription = Prescription.objects.filter(prescription_id=pk)
        prescription_medicine = Prescription_medicine.objects.filter(prescription__in=prescription)
        prescription_test = Prescription_test.objects.filter(prescription__in=prescription)
        test_carts = testCart.objects.filter(user=request.user, purchased=False)
        
        # item = get_object_or_404(test, pk=pk)
        test_order_qs = testOrder.objects.filter(user=request.user, ordered=False)
        if test_order_qs.exists():
            test_order = test_order_qs[0]
            if test_order.orderitems.filter(item=item).exists():
                test_order_item = testCart.objects.filter(item=item, user=request.user, purchased=False)[0]
                test_order.orderitems.remove(test_order_item)
                test_order_item.delete()
                # messages.warning(request, "This test was remove from your cart!")
                context = {'test_carts': test_carts,'test_order': test_order,'patient': patient,'prescription_id':pk}
                return render(request, 'test-cart.html', context)
            else:
                # messages.info(request, "This test was not in your cart")
                context = {'patient': patient,'test': item,'prescription':prescription,'prescription_medicine':prescription_medicine,'prescription_test':prescription_test}
                return render(request, 'prescription-view.html', context)
        else:
            # messages.info(request, "You don't have an active order")
            context = {'patient': patient,'test': item,'prescription':prescription,'prescription_medicine':prescription_medicine,'prescription_test':prescription_test}
            return redirect('prescription-view', pk=prescription.prescription_id)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html') 

@csrf_exempt
def prescription_view(request, pk):
    if request.user.is_patient:
        try:
            patient = Patient.objects.get(user=request.user)
            print("👤 Patient retrieved:", patient)
        except Patient.DoesNotExist:
            print("❌ Error: Patient profile not found for user:", request.user)
            messages.error(request, "Patient profile not found.")
            return redirect('logout')

        # Retrieve the specific Prescription object or return 404
        prescription = get_object_or_404(Prescription, prescription_id=pk, patient=patient)
        print("📝 Prescription retrieved:", prescription)

        # Fetch related Prescription_medicine and Prescription_test objects
        prescription_medicine = Prescription_medicine.objects.filter(prescription=prescription)
        prescription_test = Prescription_test.objects.filter(prescription=prescription)

        print("💊 Prescription Medicines Retrieved:", prescription_medicine)
        print("🧪 Prescription Tests Retrieved:", prescription_test)

        context = {
            'patient': patient,
            'prescription': prescription,
            'prescription_test': prescription_test,
            'prescription_medicine': prescription_medicine
        }

        print("📄 Rendering 'prescription-view.html' with context:", context)
        return render(request, 'prescription-view.html', context)
    else:
        print("🔒 Unauthorized access attempt by user:", request.user)
        messages.info(request, 'You are not authorized to view this page.')
        return redirect('logout')
    
    
@csrf_exempt
def render_to_pdf(template_src, context_dict={}):
    template=get_template(template_src)
    html=template.render(context_dict)
    result=BytesIO()
    pres_pdf=pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pres_pdf.err:
        return HttpResponse(result.getvalue(),content_type="aplication/pres_pdf")
    return None


# def prescription_pdf(request,pk):
#  if request.user.is_patient:
#     patient = Patient.objects.get(user=request.user)
#     prescription = Prescription.objects.get(prescription_id=pk)
#     perscription_medicine = Perscription_medicine.objects.filter(prescription=prescription)
#     perscription_test = Perscription_test.objects.filter(prescription=prescription)
#     current_date = datetime.date.today()
#     context={'patient':patient,'current_date' : current_date,'prescription':prescription,'perscription_test':perscription_test,'perscription_medicine':perscription_medicine}
#     pdf=render_to_pdf('prescription_pdf.html', context)
#     if pdf:
#         response=HttpResponse(pdf, content_type='application/pdf')
#         content="inline; filename=report.pdf"
#         # response['Content-Disposition']= content
#         return response
#     return HttpResponse("Not Found")

@csrf_exempt
def prescription_pdf(request,pk):
 if request.user.is_patient:
    patient = Patient.objects.get(user=request.user)
    prescription = Prescription.objects.get(prescription_id=pk)
    prescription_medicine = Prescription_medicine.objects.filter(prescription=prescription)
    prescription_test = Prescription_test.objects.filter(prescription=prescription)
    # current_date = datetime.date.today()
    context={'patient':patient,'prescription':prescription,'prescription_test':prescription_test,'prescription_medicine':prescription_medicine}
    pres_pdf=render_to_pdf('prescription_pdf.html', context)
    if pres_pdf:
        response=HttpResponse(pres_pdf, content_type='application/pres_pdf')
        content="inline; filename=prescription.pdf"
        response['Content-Disposition']= content
        return response
    return HttpResponse("Not Found")

@csrf_exempt
@login_required(login_url="login")
def delete_prescription(request,pk):
    if request.user.is_authenticated and request.user.is_patient:
        prescription = Prescription.objects.get(prescription_id=pk)
        prescription.delete()
        messages.success(request, 'Prescription Deleted')
        return redirect('patient-dashboard')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')

@csrf_exempt
@login_required(login_url="login")
def delete_report(request,pk):
    if request.user.is_authenticated and request.user.is_patient:
        report = Report.objects.get(report_id=pk)
        report.delete()
        messages.success(request, 'Report Deleted')
        return redirect('patient-dashboard')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')

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
    


