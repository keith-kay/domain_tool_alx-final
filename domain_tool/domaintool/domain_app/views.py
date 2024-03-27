from django.http import JsonResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CompanyForm, DomainForm, UserForm
from django.utils.html import format_html
from .models import Company, Domain
from django.db.models import Q
from django.views import View
import requests, json, logging
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils import timezone
from datetime import date,datetime, timedelta
from .models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.views.decorators.http import require_POST
import time
import schedule
# Create your views here.

def index(request):
    
    return render(request, "index.html")

def copyright(request):
    current_year = datetime.datetime.now().year
    context = {
        'current_year': current_year
    }
    template_names = ['dashboard.html', 'base_dash.html']  # List of template names
    return render(request, template_names, context)

@login_required(login_url="signin")
def dashboard(request):
    active_domains = Domain.objects.filter(expiry_date__gte=date.today()).count()
    expired_domains = Domain.objects.filter(expiry_date__lt=date.today()).count()

    context = {
        'active_domains': active_domains,
        'expired_domains': expired_domains,
        'domains': Domain.objects.all(),
    }

    return render(request, 'dashboard.html', context)

def base_domain_tbl(request):
    domains = Domain.objects.all()
    print(domains) 
    context = {'domains': domains}
    return render(request, 'base_dash.html', context)


def signin(request):
    msg = ""
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the user exists with the given email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        # Check if the user exists and is not active
        if user and not user.is_active:
            msg = "Account inactive! Contact admin"
        else:
            # Attempt to authenticate the user
            user = authenticate(request, username=email, password=password)

            # Check if authentication was successful and user is active
            if user and user.is_active:
                # Print all fields of the user
                login(request, user)

                if "next" in request.POST:
                    return redirect(request.POST.get("next"))
                return redirect("dashboard")
            else:
                msg = "Invalid credentials"

    context = {"msg": msg}
    return render(request, "signin.html", context)

def signout(request):
    logout(request)
    return redirect("index")

def list_users(request):
    users = User.objects.all()
    
    threshold_date = timezone.now() + timedelta(days=30)

    # Query the database for domains with expiry date less than or equal to 30 days
    expiring_domains = Domain.objects.filter(expiry_date__lte=threshold_date)

    # Count the number of expiring domains
    domain_count = expiring_domains.count()
    
    now = timezone.now()
    for domain in expiring_domains:
        domain.remaining_days = (domain.expiry_date - now).days

    # Pass the data to the template
    context = {
        'domain_count': domain_count,
        'expiring_domains': expiring_domains,
        'users': users,
        'now': now
    }
    return render(request, 'users_list.html', context)

@login_required(login_url="signin")
def add_user(request, id=0):
    threshold_date = timezone.now() + timedelta(days=30)

    # Query the database for domains with expiry date less than or equal to 30 days
    expiring_domains = Domain.objects.filter(expiry_date__lte=threshold_date)

    # Count the number of expiring domains
    domain_count = expiring_domains.count()
    
    now = timezone.now()
    for domain in expiring_domains:
        domain.remaining_days = (domain.expiry_date - now).days
        
    if request.method == "GET":
        if id == 0:
            form = UserForm()
        else:
            user = get_object_or_404(User, pk=id)
            form = UserForm(instance=user)
        return render(request, "add_user.html", {'form': form})
    else:
        if id == 0:
            form = UserForm(request.POST)
        else:
            user = get_object_or_404(User, pk=id)
            form = UserForm(request.POST, instance=user)
        
        if form.is_valid():
            form.save()
            if id == 0:
                success_message = 'User Added!'
            else:
                success_message = 'User Updated!'
            # Add success message using Django's messages framework
            messages.success(request, success_message)
            users = User.objects.all()
            context = {'users': users}
            return render(request, "users_list.html", context)
        else:
            # Handle the case when the form is not valid
            return render(request, "add_user.html", {'form': form, 'domain_count': domain_count, 'expiring_domains': expiring_domains, 'now': now})

@login_required(login_url="signin")
def company_list(request, id=0):    
    threshold_date = timezone.now() + timedelta(days=30)

    # Query the database for domains with expiry date less than or equal to 30 days
    expiring_domains = Domain.objects.filter(expiry_date__lte=threshold_date)

    # Count the number of expiring domains
    domain_count = expiring_domains.count()
    
    now = timezone.now()
    for domain in expiring_domains:
        domain.remaining_days = (domain.expiry_date - now).days

    # Pass the data to the template
    context = {
        'domain_count': domain_count,
        'expiring_domains': expiring_domains,
        'now': now,
    } 
    if request.method == "GET":
        if id==0:
            form = CompanyForm()
        else:
            company = Company.objects.get(pk=id)
            form = CompanyForm(instance=company)
        return render(request, "manage_company.html",{'form':form,'domain_count': domain_count,'expiring_domains': expiring_domains, 'now': now, })
    else:
        if id == 0:
            form = CompanyForm(request.POST)
        else:
            company = Company.objects.get(pk=id)   
            form = CompanyForm(request.POST,instance=company) 
        if form.is_valid():
            form.save()
            messages.success(request, 'Company Added!')
            context = {'companies': Company.objects.all()}
        return render(request, "company_list.html", {'domain_count': domain_count,'expiring_domains': expiring_domains, 'now': now, 'companies': Company.objects.all()})


@login_required(login_url="signin")
def company_list(request, id=0):
              
    threshold_date = timezone.now() + timedelta(days=30)

    # Query the database for domains with expiry date less than or equal to 30 days
    expiring_domains = Domain.objects.filter(expiry_date__lte=threshold_date)

    # Count the number of expiring domains
    domain_count = expiring_domains.count()
    
    now = timezone.now()
    for domain in expiring_domains:
        domain.remaining_days = (domain.expiry_date - now).days

    if request.method == "GET":
        if id == 0:
            form = CompanyForm()
        else:
            company = get_object_or_404(Company, pk=id)
            form = CompanyForm(instance=company)
        return render(request, "manage_company.html", {'form': form, 'domain_count': domain_count, 'expiring_domains': expiring_domains, 'now': now})
    else:
        if id == 0:
            form = CompanyForm(request.POST)
        else:
            company = get_object_or_404(Company, pk=id)
            form = CompanyForm(request.POST, instance=company)

        if form.is_valid():
            form.save()
            if id == 0:
                success_message = 'Company Added!'
            else:
                success_message = 'Company Updated!'
            # Add success message using Django's messages framework
            messages.success(request, success_message)
            context = {'companies': Company.objects.all()}
            return render(request, "company_list.html", {'domain_count': domain_count, 'expiring_domains': expiring_domains, 'now': now, 'companies': Company.objects.all()})
    
@login_required(login_url="signin")
def companies(request):
    threshold_date = timezone.now() + timedelta(days=30)

    # Query the database for domains with expiry date less than or equal to 30 days
    expiring_domains = Domain.objects.filter(expiry_date__lte=threshold_date)

    # Count the number of expiring domains
    domain_count = expiring_domains.count()
    
    now = timezone.now()
    for domain in expiring_domains:
        domain.remaining_days = (domain.expiry_date - now).days

    # Pass the data to the template
    context = {
        'domain_count': domain_count,
        'expiring_domains': expiring_domains,
        'now': now,
        'companies': Company.objects.all()
    }
     
    return render(request,"company_list.html", context)

def company_delete(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    if request.method == 'POST':
        company.delete()
        messages.error(request, 'Company deleted!')
        return redirect('lists')  # Redirect to the appropriate URL after deletion

    # Optionally, you can provide a response here for other HTTP methods
    return redirect('lists')

@login_required(login_url="signin")
def domain(request):
    threshold_date = timezone.now() + timedelta(days=30)

    # Query the database for domains with expiry date less than or equal to 30 days
    expiring_domains = Domain.objects.filter(expiry_date__lte=threshold_date)

    # Count the number of expiring domains
    domain_count = expiring_domains.count()
    
    now = timezone.now()
    for domain in expiring_domains:
        domain.remaining_days = (domain.expiry_date - now).days

    # Pass the data to the template
    context = {
        'domain_count': domain_count,
        'expiring_domains': expiring_domains,
        'now': now,
        'domains': Domain.objects.all()
    }
    
    return render(request, "manage_domain.html", context)

@login_required(login_url="signin")
def domain_status(request):
    threshold_date = timezone.now() + timedelta(days=30)

    # Query the database for domains with expiry date less than or equal to 30 days
    expiring_domains = Domain.objects.filter(expiry_date__lte=threshold_date)

    # Count the number of expiring domains
    domain_count = expiring_domains.count()
    
    now = timezone.now()
    for domain in expiring_domains:
        domain.remaining_days = (domain.expiry_date - now).days

    # Pass the data to the template
    context = {
        'domain_count': domain_count,
        'expiring_domains': expiring_domains,
        'now': now,
        'domains': Domain.objects.all()
    }
    
    return render(request, "domain_status.html", context)

@login_required(login_url="signin")
def domain_list(request):
    if request.method == "GET":
        #initialize form
        form = DomainForm()
        
        threshold_date = timezone.now() + timedelta(days=30)

        # Query the database for domains with expiry date less than or equal to 30 days
        expiring_domains = Domain.objects.filter(expiry_date__lte=threshold_date)

        # Count the number of expiring domains
        domain_count = expiring_domains.count()
        
        now = timezone.now()
        for domain in expiring_domains:
            domain.remaining_days = (domain.expiry_date - now).days

        # Pass the data to the template
        context = {
            'domain_count': domain_count,
            'expiring_domains': expiring_domains,
            'now': now,
            'form':form
        } 
        
        return render(request, "add_domain.html",context)
    else:
        form = DomainForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Domain Added!')
            context = {'domains': Domain.objects.all()}
        return render(request, "manage_domain.html", context)
    
@require_POST
def update_domain_expiry(request, domain_id):
    data = json.loads(request.body)
    
    # Retrieve the domain instance
    domain = get_object_or_404(Domain, pk=domain_id)

    # Update the expiry date based on the data you received
    # For example, if the data contains a new_expiry_date field:
    updated_expiry_date = data.get('expiry_date')
    domain.expiry_date = new_expiry_date
    domain.save()

    return JsonResponse({'message': 'Domain expiry date updated successfully'})

def lookup(request):
    if request.method == 'POST':
        form = DomainForm(request.POST)
        
        if form.is_valid():
            try:
                domain_value = form.cleaned_data['name']
                
                print(f"Domain Value: {domain_value}")

                # Your API token for whoisjsonapi.com
                api_token = 'IZLCRSx7PSLRvQquhAlp_4XvueuM97S1SghCn-L02L8niSZg6EPraZuvp2umYtk'
                
                # Construct the API URL
                api_url = f'https://whoisjsonapi.com/v1/{domain_value}'
                print(f"api_url: {api_url}")
                # Set the headers for the request
                headers = {
                    'Authorization': f'Bearer {api_token}',
                }
                
                # Send a GET request to the API with headers and timeout
                response = requests.get(api_url, headers=headers)
                
                # Check if the API request was successful
                response.raise_for_status()
                
                # Parse the JSON response
                data = response.json()
                
                print(f"API Response: {response.content}")
                
                # Extract relevant information
                domain_info = data.get('domain', {})
                registration_date_str = domain_info.get('created_date', '')
                expiry_date_str = domain_info.get('expiration_date', '')
                registrar_info = data.get('registrar', {})
                registrar_name = registrar_info.get('name', '')  # Extract registrar name

                # Function to convert date string to the desired format
                def convert_to_desired_format(date_str):
                    try:
                        # Try parsing the date in the first format
                        return datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%SZ')
                    except ValueError:
                        pass  # Ignore the exception for this format
                    try:
                        # Try parsing the date in the second format
                        return datetime.strptime(date_str, '%d.%m.%Y').strftime('%Y-%m-%dT%H:%M:%SZ')
                    except ValueError:
                        pass  # Ignore the exception for this format

                    # If it doesn't match any format, return the original string
                    return date_str

                # Convert dates to the desired format if they match either of the specified formats
                registration_date = convert_to_desired_format(registration_date_str)
                expiry_date = convert_to_desired_format(expiry_date_str)
                
                print(f"Creation Date: {registration_date}")
                print(f"Expiration Date: {expiry_date}")
                print(f"Registrar Name: {registrar_name}")

                # Return the relevant data as JSON
                return JsonResponse({
                    'status': 'success',
                    'registration_date': registration_date,
                    'expiry_date': expiry_date,
                    'registrar_name': registrar_name,  # Include registrar name in the response
                })
            
            except requests.RequestException as e:
                # Handle API request error
                return JsonResponse({'error': f'Failed to retrieve data from the API. Error: {e}'}, status=500)
            
            except Exception as e:
                # Handle other exceptions
                return JsonResponse({'error': f'An unexpected error occurred: {e}'}, status=500)
        
        else:
            # Handle form validation errors
            return JsonResponse({'error': 'Form validation error.'}, status=400)
    
    else:
        return JsonResponse({'error': 'This view is for handling POST requests only.'}, status=400)
    
class DomainUpdateView(View):
    def get(self, request, *args, **kwargs):
        domain_name = self.kwargs.get('domain_name')
        api_token = '' #'HlhEzRXMZigIG5_C8n7vAm6pFPt6NTHpyrHbmE6cZ4YU01ZJdn68s7URm4EtGSC'  # Replace with your actual API token

        # Print the URL before making the API request
        print(f'Requesting API for domain: {domain_name}')
        api_url = f'https://whoisjsonapi.com/v1/{domain_name}'
        print(f"api_url: {api_url}")

        # Set the headers for the request
        headers = {
             'Authorization': f'Bearer {api_token}',
        }

        try:
            # Make the API request
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()  # Check if the API request was successful

            # Parse the JSON response
            data = response.json()
            print(f"API Response: {response.content}")

            # Check if the response has the expected structure
            if 'domain' not in data or 'registrar' not in data:
                raise ValueError('Invalid response structure')

            # Extract relevant information
            
            registrar_info = data['registrar']
            
            # Include the registrar's name in the response
            registrar_name = registrar_info.get('name', 'N/A')

            # Respond with the formatted updated_date and registrar's name
            return JsonResponse({ 'registrar_name': registrar_name})

        except requests.exceptions.RequestException as e:
            # Handle request exceptions
            print(f'Error for {domain_name}: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)

        except ValueError as e:
            # Handle invalid response structure
            print(f'Error for {domain_name}: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)
        

def domain_delete(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id)
    
    if request.method == 'POST':
        # Check if the related Company exists
        try:
            company = domain.company
        except Company.DoesNotExist:
            # Redirect or handle the case where the related Company doesn't exist
            return redirect('domain')  # Adjust the target according to your URL structure

        domain.delete()
        messages.error(request, 'Domain deleted!')
        return redirect('domain')  # Redirect to the appropriate URL after deletion
    
    # Handle other HTTP methods (GET, etc.) as needed
    
    # Optionally, you can provide a response here for other HTTP methods
    return redirect('domain')

# global varibale for updating all domains simultaneously
WHOIS_API_URL = 'https://whoisjsonapi.com/v1/'

def perform_whois_query(domain_name, api_token):
    url = f'{WHOIS_API_URL}{domain_name}'

    # Set up headers with Bearer token
    headers = {
        'Authorization': f'Bearer {api_token}'
    }

    # Make a GET request to the WHOIS API with headers
    response = requests.get(url, headers=headers)
    response_data = response.json()

    # Extract the expiry date from the WHOIS API response
    expiry_date_str = response_data['domain'].get('expiration_date')

    # Print the expiry_date_str and domain name
    print(f'Expiry Date String: {expiry_date_str}')
    print(f'Domain Name: {domain_name}')

    if expiry_date_str:
        try:
            # Try parsing with milliseconds
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            try:
                # If parsing with milliseconds fails, try parsing without milliseconds
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                try:
                    # If both parsing attempts fail, try parsing the date in the second format
                    expiry_date = datetime.strptime(expiry_date_str, '%d.%m.%Y')
                    # Convert the format to '%Y-%m-%dT%H:%M:%SZ'
                    expiry_date_str = expiry_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                except ValueError:
                    pass

        # Make the datetime aware using Django's timezone
        expiry_date_aware = timezone.make_aware(expiry_date, timezone.utc)

        return expiry_date_aware
    else:
        return None

def update_domains(request, *args, **kwargs):
    api_token = 'IZLCRSx7PSLRvQquhAlp_4XvueuM97S1SghCn-L02L8niSZg6EPraZuvp2umYtk' 

    try:
        # Get a list of all domains
        domains = Domain.objects.all()

        for domain in domains:
            if domain.name == 'wasinimaritime.co.ke':
                continue
            
            # Perform a WHOIS query for each domain
            expiry_date = perform_whois_query(domain.name, api_token)

            if expiry_date:
                # Update the domain's expiry_date
                domain.expiry_date = expiry_date
                domain.save()

        # Success message
        message = 'Domains updated successfully.'
        # Get a list of all domains (updated or not)
        updated_domains = Domain.objects.all()
        return JsonResponse({'success': True, 'message': message, 'domains': list(updated_domains.values())})
        
    except Exception as e:
        # Log the error
        print(f'Error updating domains: {e}')
        # Set error message
        message = f'Error updating domains: {e}'
        return JsonResponse({'success': False, 'message': message}, status=500)

def update_domains_result(request, *args, **kwargs):
    # api_token = 'IZLCRSx7PSLRvQquhAlp_4XvueuM97S1SghCn-L02L8niSZg6EPraZuvp2umYtk' 
    success = True
    message = 'Domains updated successfully!'
    total_domains = None
    active_domains = None
    expired_domains = None
    timestamp = None
    
    try:
        # Get a list of all domains
        domains = Domain.objects.all()

        # Calculate total domains, active domains, expired domains
        total_domains = domains.count()
        active_domains = Domain.objects.filter(expiry_date__gte=date.today()).count()
        expired_domains = Domain.objects.filter(expiry_date__lt=date.today()).count()

        for domain in domains:
            # Check if the domain name is 'wasinimaritime.co.ke', skip updating if it is
            if domain.name == 'wasinimaritime.co.ke':
                continue
            
            # Perform a WHOIS query for each domain
            expiry_date = perform_whois_query(domain.name, api_token)

            if expiry_date:
                # Update the domain's expiry_date
                domain.expiry_date = expiry_date
                domain.save()

    except Exception as e:
        # Log the error
        print(f'Error updating domains: {e}')
        # Set success flag to False
        success = False
        # Set error message
        message = f'Error updating domains: {e}'

    # Set the timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Send notification email based on success flag
    send_notification_email_view(message, success, total_domains, active_domains, expired_domains, timestamp)

def send_notification_email_view(message, success, total_domains, active_domains, expired_domains, timestamp):
    # Send notification email logic
    subject = 'Weekly Domain Update'
    if success:
        subject += ' - Success'
        # Compose the email message only if the update was successful
        email_body = (
            "<div>Hello Team,</div><br>"
            "<div>Scheduled domain sync complete;</div><br>"
            "<strong>Total Domains:</strong> {}<br>"
            "<strong>Active Domains:</strong> {}<br>"
            "<strong>Expired Domains:</strong> {}<br>"
            "<strong>Timestamp:</strong> {}<br>"
            "<p>{}</p>"
        ).format(total_domains, active_domains, expired_domains, timestamp,message)
    else:
        subject += ' - Error'
        # Include error message in the email body if there was an error
        email_body = "<p>{}</p>".format(message)

    # Create the EmailMessage object
    email = EmailMessage(
        subject=subject,
        body=email_body,
        from_email='ictsupport@bulkstream.com',
        to=['nancykira21@gmail.com'],
    )

    # Send the email
    email.content_subtype = 'html'
    email.send(fail_silently=False)
    
def scheduled_update():
    # This function will be called by the scheduler
    post_request = HttpRequest()
    post_request.method = 'POST'
    update_domains_result(post_request)

schedule.every().wednesday.at("13:02").do(scheduled_update)
        
class ActiveUserRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated and not self.request.user.is_active:
            return self.handle_inactive_user()
        return super().dispatch(request, *args, **kwargs)

    def handle_inactive_user(self):
        return redirect('inactive_account')

class MyRestrictedView(ActiveUserRequiredMixin, TemplateView):
    template_name = 'inactive.html'        