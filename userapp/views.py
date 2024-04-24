from datetime import date, datetime, timedelta


from django.contrib.auth import authenticate,logout
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from travelagencyproject.settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET_KEY

from django.db.models import Q, Sum, Count
from userapp.form import UserRegistrationForm
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404

from adminapp.models import PackageDateModel
from .models import PackagesModel, NationModel, NationImageModel, PackagePageModel, ReviewModel, TravelTipsModel, \
    PackagePlanModel, UserModel, UserImageModel, MapArea, Payment, Contact
import razorpay






# Create your views here.
def home(request):
    data = PackagesModel.objects.filter(nation_id=1)
    data2 = NationModel.objects.filter(nation_id=1)
    nations = NationModel.objects.all()
    # nation_names = [obj.nation_name for obj in nations]
    # print(nation_names)

    if request.session.get('user'):
        user = request.session.get('user')
        name_data = UserModel.objects.get(User_name=user)
        name = name_data.User_name
        if request.session.get('nation'):
            user = request.session.get('user')
            name_data = UserModel.objects.get(User_name=user)
            name = name_data.User_name
            nation = request.session.get('nation')
            data = PackagesModel.objects.filter(nation_id=nation)
            data2 = NationModel.objects.filter(nation_id=nation)
            return render(request, 'home.html', {"DATA": data, 'data2': data2, "category": nations, 'name': name})
        return render(request, 'home.html', {"DATA": data, 'data2': data2, "category": nations, 'name': name})
    return render(request, 'home.html', {"DATA": data, 'data2': data2, "category": nations})


def search(request):
    data1 = PackagesModel.objects.all()
    sort_data = None
    category_data = None
    search_data = ''
    nations = NationModel.objects.all()
    if request.method == 'POST':
        search_data = request.POST.get('search', '')
        sort_data = request.POST.get('sort-select')
        category_data = request.POST.get('category-select')
        if category_data:
            print(category_data)
            data1 = data1.filter(nation__nation_name__icontains=category_data)
            print(data1.values)
        if search_data:
            data1 = data1.filter(
                Q(nation__nation_name__icontains=search_data) |
                Q(total_days__icontains=search_data) |
                Q(package_name__icontains=search_data) |
                Q(price__icontains=search_data) |
                Q(start_date__icontains=search_data) |
                Q(end_date__icontains=search_data)
            )

        if sort_data == "small":
            data1 = data1.order_by('price')
        else:
            data1 = data1.order_by('-price')
        if not data1.exists():
            return redirect('/')
    return render(request, 'search_page.html',
                  {'DATA': data1, "search_data": search_data, "category_data": category_data, "category": nations,
                   'search': sort_data})
    # return redirect('/search_page')


def user_profile(request):
    if request.session.get('user'):
        user = request.session.get('user')
        user_model = UserModel.objects.get(User_name=user)
        user_login_id = user_model.User_id
        user_data = UserModel.objects.filter(User_name=user)
        user_login = UserImageModel.objects.filter(user=user_login_id)
        booking_data = Payment.objects.filter(user=user)
        return render(request, 'user_profile.html',
                      {"user": user_login, 'booking_data': booking_data, 'user_data': user_data})
    return redirect('/login')


def contact(request):
    if request.session.get('user'):
       if request.method == 'POST':
          name = request.POST.get('name')
          phone = request.POST.get('phone')
          email = request.POST.get('email')
          message = request.POST.get('message')
          print(email)
          cont_obj = Contact()
          cont_obj.name = name
          cont_obj.phone = phone
          cont_obj.email = email
          cont_obj.message = message
          cont_obj.save()
          messages.success(request, 'Your message has been sent successfully!')
          return redirect('/contact')
       return render(request, 'contact.html')
    return redirect('/login')

def destination(request):
    user = request.session.get('user')
    try:
        name_data = UserModel.objects.get(User_name=user)
        name = name_data.User_name
    except UserModel.DoesNotExist:
        name = None  # Set name to None if user is not logged in
    DATA = NationImageModel.objects.all()
    return render(request, 'destination.html', {"data": DATA, 'name': name})
def forgot(request):
    return render(request, 'forgotpassword.html')



def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = UserModel.objects.get(email=email)
        user_id = user.User_id
        user_object = UserModel.objects.get(User_id=user_id)
        user_object.Password = password
        user_object.save()
        return redirect('/login')
    return render(request, 'forgotpassword.html')


def profile_update(request):
    user = request.session.get('user')
    user_model = UserModel.objects.get(User_name=user)
    user_login_id = user_model.User_id
    user_data = UserModel.objects.filter(User_name=user)
    user_login = UserImageModel.objects.filter(user=user_login_id)
    booking_data = Payment.objects.filter(user=user)
    print('hi')
    if request.method == 'POST':
        username = request.POST.get('new-name')
        password = request.POST.get('new-password')
        email = request.POST.get('new-email')
        phone_number = request.POST.get('new-phone-number')
        status = 'active'
        user = request.session.get('user')
        print(user)
        user_model = UserModel.objects.get(User_name=user)
        print(user_model)
        user_id = user_model.User_id
        profile_obj = UserModel.objects.get(User_id=user_id)
        profile_obj.User_name = username
        profile_obj.Password = password
        profile_obj.Email = email
        profile_obj.Phone_number = phone_number
        profile_obj.Status = status
        print('updated successfully')
        profile_obj.save()
        return redirect('/login')
    return render(request, 'user_profile.html', {"user": user_login, 'booking_data': booking_data})


def about(request):
    return render(request, 'about.html')


def packages(request):
    DATA = NationImageModel.objects.all()
    return render(request, 'packages.html', {"data": DATA})


def countries_contents(request):
    id = request.POST.get('nation_image_id')
    data = NationImageModel.objects.filter(nation_image_id=id)
    print(data.values)
    return render(request, 'countries_contents.html', {'data': data})


def countries_contents_map(request, id):
    # id = request.POST.get('nation_image_id')
    data = NationImageModel.objects.filter(nation_image_id=id)
    print(data.values)
    return render(request, 'countries_contents.html', {'data': data})

def country_packages(request):
    if request.method == 'POST':
        request.session['nation'] = request.POST.get('nation_image_id')
        nation_image_id = request.POST.get('nation_image_id')
        data = PackagesModel.objects.filter(nation_id=nation_image_id)
        data2 = NationModel.objects.filter(nation_id=nation_image_id)
        data3 = UserModel.objects.all()
        return render(request, 'country_packages.html', {'data': data, 'data2': data2})
    return redirect('/packages')


def package_plan(request):
    package_date = PackageDateModel.objects.filter(package=request.session.get('package_id'))
    if request.session.get('user'):
        if request.method == 'POST':
            id = request.POST.get('packages_id')
            request.session['package_id'] = id
            data = PackagePlanModel.objects.filter(package_id=id).order_by('oder')
            data2 = PackagesModel.objects.filter(packages_id=id)
            username = request.session['user']
            print(username)
            print(package_date)
            data3 = ReviewModel.objects.filter(packages=id)
            total_rating_sum = data3.aggregate(total_sum=Sum('rating_value'))['total_sum']
            total_rating_count = data3.aggregate(total_count=Count('rating_value'))['total_count']
            if total_rating_sum and total_rating_count:
                average_rating = round((total_rating_sum / total_rating_count), 1)
                print(average_rating)
                return render(request, 'package_plan.html',
                              {'data': data, 'data2': data2, 'data3': data3, 'average_rating': average_rating,
                               'package_date': package_date})
            return render(request, 'package_plan.html',
                          {'data': data, 'data2': data2, 'data3': data3,
                           'package_date': package_date})
        return redirect('/country_packages')
    return redirect('/login')


def traveltips(request):
    DATA = NationImageModel.objects.all()
    return render(request, 'Traveltips.html', {"data": DATA})


def country_traveltips(request):
    id = request.POST.get('nation_image_id')
    data = TravelTipsModel.objects.filter(nation_id=id)
    data2 = NationModel.objects.filter(nation_id=id)
    return render(request, 'country_traveltip.html', {'data': data, 'data2': data2})




#important
def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = UserModel.objects.filter(User_name=username, Password=password).first()
        if user:
            print('Login successful')
            request.session['user'] = username
            return redirect('/')
        else:
            print('Login failed: Invalid credentials')
            if not username:
                username_error = 'Username is required.'
                return render(request, 'login.html',{'username_error': username_error})
            if not password:
                password_error = 'Password is required.'

                return render(request, 'login.html', {'password_error': password_error})
    return render(request, 'login.html')




def logout(request):
    del request.session['user']
    if request.session.get('nation'):
        del request.session['nation']
    if request.session.get('packages_id'):
        print(request.session.get('packages_id'))
        del request.session['packages_id']
    return redirect('/')



#     return render(request, 'register.html')
def register(request):
    """
    Handles user registration, validating and saving form data.

    If the request method is GET, renders an empty registration form.
    If the request method is POST, validates the submitted form data.
    If the form is valid, saves the data and redirects to the home page.

    Parameters:
    - request: HttpRequest object.

    Returns:
    - HttpResponse object rendering the reg_validation.html template with the registration form.
    - Redirects to the home page on successful registration.
    """
    if request.method == 'POST':
        form_obj = UserRegistrationForm(request.POST)
        print(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            print('form submit')
            return redirect('/')
    else:
        form_obj = UserRegistrationForm()
    return render(request, 'register.html', {'form': form_obj})


client = razorpay.Client(auth=("rzp_test_1fobC03iYb0HUi", "gWuvQyKHybJBvnIwjiPNtq9q"))




def initiate_payment(request):
    if request.session.get('user'):
        if request.method == 'POST':
            date1 = PackageDateModel.objects.get(date_id=request.POST.get('start_date'))
            count = int(date1.count)
            package_date = PackageDateModel.objects.filter(package=request.POST.get('packages_id'))
            id = request.POST.get('packages_id')
            request.session['package_id'] = id
            data = PackagePlanModel.objects.filter(package_id=id).order_by('oder')
            data2 = PackagesModel.objects.filter(packages_id=id)
            username = request.session['user']
            # print(username)
            # print(package_date)
            data3 = ReviewModel.objects.filter(packages=id)
            total_rating_sum = data3.aggregate(total_sum=Sum('rating_value'))['total_sum']
            total_rating_count = data3.aggregate(total_count=Count('rating_value'))['total_count']
            # average_rating = round((total_rating_sum / total_rating_count), 1)
            if total_rating_sum is not None and total_rating_count is not None and total_rating_count != 0:
                average_rating = round((total_rating_sum / total_rating_count), 1)
                print(average_rating)
            else:
                average_rating = None
            print(average_rating)
            members = int(request.POST.get('members'))
            updated_count = count - members
            if updated_count > 0:
                # Use Razorpay API to create payment order with selected payment option
                id = request.POST.get('packages_id')
                # print(id)
                user = request.session.get('user')
                # date1 = PackageDateModel.objects.get(date_id=request.POST.get('start_date'))
                start_date = date1.start_date
                count = date1.count
                members = int(request.POST.get('members'))
                updated_count = count - members
                date_id = date1.date_id
                obj1 = PackageDateModel.objects.get(date_id=date_id)
                obj1.count = updated_count
                obj1.save()
                days=PackagesModel.objects.get(packages_id=id)
                number_to_add = days.total_days
                print(number_to_add)
                end_date = start_date + timedelta(days=number_to_add)
                print(end_date)
                data2 = PackagesModel.objects.filter(packages_id=id)
                price = PackagesModel.objects.get(packages_id=id)
                price_amount = price.price
                package = price.package_name
                client = razorpay.Client(auth=('rzp_test_1fobC03iYb0HUi', 'gWuvQyKHybJBvnIwjiPNtq9q'))
                amount = (price_amount) * 100
                # print(amount)  # Razorpay expects amount in paise
                payment_order = client.order.create({"amount": amount, "currency": "INR", "payment_capture": "1"})
                # Pass selected payment option
                payment_order_id = payment_order['id']
                # print(payment_order_id)
                return render(request, 'payment.html',
                              {'api_key': RAZORPAY_KEY_ID, 'order_id': payment_order_id, 'data': data2,
                               'start_date': start_date, 'end_date': end_date, 'user': user, 'package': package,
                               'members': members,'price':price_amount})
            return render(request, 'package_plan.html',
                          {'data': data, 'data2': data2, 'data3': data3, 'average_rating': average_rating,
                           'package_date': package_date, 'count': updated_count})
        return render(request, "payment.html")
    return redirect('/login')


def review(request):
    if request.method == 'POST':
        user = request.session.get('user')
        user_data = UserModel.objects.get(User_name=user)
        user_id = user_data.User_id
        package = request.session.get('package_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        obj = ReviewModel()
        # obj.review = review
        obj.user_name = user
        obj.packages = PackagesModel.objects.get(packages_id=package)
        obj.user = UserModel.objects.get(User_id=user_id)
        obj.rating_value = rating
        obj.comment = comment
        obj.save()
        return redirect('/country_packages')
    return render(request, 'review.html')

def profile_review(request, package_name):
    if request.method == 'POST':
        user = request.session.get('user')
        user_data = UserModel.objects.get(User_name=user)
        user_id = user_data.User_id
        packages = PackagesModel.objects.get(package_name=package_name)
        packages_id = packages.packages_id
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        obj = ReviewModel()
        obj.user_name = user
        obj.packages = PackagesModel.objects.get(packages_id=packages_id)
        obj.user = UserModel.objects.get(User_id=user_id)
        obj.rating_value = rating
        obj.comment = comment
        obj.save()
        return redirect('/user_profile')
    return render(request, 'review.html')


def payment_success(request):
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    razorpay_order_id = request.GET.get('razorpay_order_id')
    razorpay_signature = request.GET.get('razorpay_signature')
    start_date = request.GET.get('start_date')

    try:
        # Attempt to parse with full month name format
        formatted_date = datetime.strptime(start_date, "%B %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        try:
            # Attempt to parse with abbreviated month name format
            formatted_date = datetime.strptime(start_date, "%b. %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            print("Unable to parse date with any known format")
            formatted_date = None

    user = request.GET.get('user')
    package = request.GET.get('package')
    members = request.GET.get('members')
    price = request.GET.get('price')

    # Create Payment object
    payment = Payment.objects.create(
        payment_id=razorpay_payment_id,
        order_id=razorpay_order_id,
        signature=razorpay_signature,
        user=user, package=package, members=members, price=price, start_date=formatted_date
    )



    # Fetch package data
    package_data = PackagesModel.objects.filter(package_name=package)

    return render(request, "payment_succ.html",
                  {'payment_id': razorpay_payment_id, 'data': package_data, 'order_id': razorpay_order_id,
                   'payment_signature': razorpay_signature, 'user': user, 'package': package,
                   'members': members})

def cancel(request, id):
    data = Payment.objects.get(id=id)
    members = data.members
    start_date = data.start_date

    data2 = PackageDateModel.objects.get(start_date=start_date)
    date_mem = data2.count
    total_mem = date_mem + members
    mem_obj = PackageDateModel.objects.get(start_date=start_date)
    mem_obj.count = total_mem
    mem_obj.save()
    data.delete()
    return redirect('/user_profile')
def cancel1(request, id):
    data = Payment.objects.get(id=id)
    members = data.members
    start_date = data.start_date
    data2 = PackageDateModel.objects.get(start_date=start_date)
    date_mem = data2.count
    total_mem = date_mem + members
    mem_obj = PackageDateModel.objects.get(start_date=start_date)
    mem_obj.count = total_mem
    mem_obj.save()
    data.delete()
    return redirect('/admin_home')

def get_nation(request):
    if request.method == 'POST':
        coords = request.POST.get('coords')
        try:
            map_area = MapArea.objects.get(coordinates=coords)
            id = map_area.nation_id
            # nation_id=NationModel.objects.get(nation_id=id)
            # print(nation_id)
            data = NationImageModel.objects.filter(nation_image_id=id)
            return render(request, 'countries_contents.html', {'data': data})
        except MapArea.DoesNotExist:
            return JsonResponse({'error': 'Area not found'}, status=404)


def payment_pro(request):
    return render(request, "payment_pro.html")


def payment_failure(request):
    return render(request, "payment_fail.html")


def payment(request):
    return render(request, "payment.html")



def dashboard(request):
    # Retrieve GitHub username from authenticated user's profile
    # github_username = request.user.socialaccount_set.filter(provider='github').first().extra_data.get('login')
    #
    # # Store GitHub username in the session
    # request.session['user'] = github_username

    return render(request, "dashboard.html")