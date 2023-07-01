import os
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import *
from .forms import *
import stripe

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY_TEST')


def index(request):
    return render(request, 'index.html', {})


def products(request):
    all_products = Product.objects.all().order_by('pk')
    p = Paginator(all_products, per_page=6)
    page = request.GET.get('page')
    products_p = p.get_page(page)
    return render(request, 'products.html', {'products_p': products_p})


def search(request):
    search_query = request.GET.get('search', '').strip()
    if search_query:
        searched = Product.objects.filter(product_name__icontains=search_query).order_by('pk')
        p = Paginator(searched, per_page=6)
        page = request.GET.get('page')
        searched = p.get_page(page)
    else:
        searched = Product.objects.none()
    return render(request, 'search.html', {'searched': searched, 'query': search_query})


@login_required(login_url='login')
def favorites(request):
    user_menu = UserMenu.objects.get(user=request.user.id)
    user_favorites = user_menu.favorites.all().order_by('pk')
    p = Paginator(user_favorites, per_page=6)
    page = request.GET.get('page')
    user_favorites = p.get_page(page)
    return render(request, 'favorites.html', {'favorites': user_favorites})


@login_required(login_url='login')
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user_menu = UserMenu.objects.get(user=request.user)
    user_menu.favorites.add(product)
    current_url = request.META.get('HTTP_REFERER')
    return redirect(current_url)


@login_required(login_url='login')
def remove_from_favorites(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user_menu = UserMenu.objects.get(user=request.user)
    user_menu.favorites.remove(product)
    current_url = request.META.get('HTTP_REFERER')
    return redirect(current_url)


@login_required(login_url='login')
def cart(request):
    user_menu = UserMenu.objects.get(user=request.user.id)
    user_cart = user_menu.cart_items.all()
    return render(request, 'cart.html', {'cart_items': user_cart})


@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user_menu = UserMenu.objects.get(user=request.user)
    user_menu.cart_items.add(product)
    current_url = request.META.get('HTTP_REFERER')
    return redirect(current_url)


@login_required(login_url='login')
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user_menu = UserMenu.objects.get(user=request.user)
    user_menu.cart_items.remove(product)
    current_url = request.META.get('HTTP_REFERER')
    return redirect(current_url)


@login_required(login_url='login')
def make_order(request):
    current_url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        quantity = request.POST.getlist('quantity[]')
        p_obj = request.POST.getlist('product_obj[]')
        line_items = []
        for qty, product in zip(quantity, p_obj):
            item = {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product
                    },
                    'unit_amount': int(Product.objects.get(product_name=product).price) * 100
                },
                'quantity': int(qty),
            }
            line_items.append(item)
        session = stripe.checkout.Session.create(
            success_url=request.build_absolute_uri(reverse('success')) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=current_url,
            line_items=line_items,
            mode='payment',
            customer_email=None,
            shipping_address_collection={"allowed_countries": ["US", "CA", "BR"]},
            shipping_options=[
                {
                    "shipping_rate_data": {
                        "type": "fixed_amount",
                        "fixed_amount": {"amount": 0, "currency": "usd"},
                        "display_name": "Free shipping",
                        "delivery_estimate": {
                            "minimum": {"unit": "business_day", "value": 5},
                            "maximum": {"unit": "business_day", "value": 7},
                        },
                    },
                },
                {
                    "shipping_rate_data": {
                        "type": "fixed_amount",
                        "fixed_amount": {"amount": 1500, "currency": "usd"},
                        "display_name": "Next day air",
                        "delivery_estimate": {
                            "minimum": {"unit": "business_day", "value": 1},
                            "maximum": {"unit": "business_day", "value": 1},
                        },
                    },
                },
            ]
        )
        return redirect(session.url)


@login_required(login_url='login')
def success(request):
    session_id = request.GET.get('session_id')
    session = stripe.checkout.Session.retrieve(session_id)
    if session.status == 'complete':
        line_items = stripe.checkout.Session.list_line_items(session_id, limit=100)
        for item in line_items['data']:
            product = get_object_or_404(Product, product_name=item['description'])
            user_menu = UserMenu.objects.get(user=request.user)
            user_menu.cart_items.remove(product)
    return render(request, 'success.html', {})


def register_user(request):
    form = RegisterUserForm()
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['username']
            form.save()
            messages.add_message(request, messages.SUCCESS, f"Registration for {user} successful!")
            return redirect('login')
    return render(request, 'register.html', {'form': form})


def login_user(request):
    form = LoginForm()
    if request.method == 'POST':
        username = request.POST['username_form']
        password = request.POST['password_form']
        remember = request.POST.get('remember')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if remember != 'remember-me':
                request.session.set_expiry(0)
            return redirect('index')
        else:
            messages.add_message(request, messages.ERROR, "Incorrect credentials or user not registered.")
    return render(request, 'login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('index')


@csrf_exempt
def my_webhook_view(request):
    endpoint_secret = os.environ.get('stripe_endpoint_secret')
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=100)
        for item in line_items['data']:
            product = get_object_or_404(Product, product_name=item['description'])
            product.quantity -= item['quantity']
            product.save()

    return HttpResponse(status=200)
