from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


from .forms import CreateUserForm
from .models import *

import secrets

import stripe

from datetime import datetime



# Create your views here.
def index(request):
    context = {}

    if request.user.is_authenticated:
        User = request.user
        context['User'] = User
        
        current_user = user.objects.get(user=User)
        context['user'] = current_user

        try:
            card = Card.objects.get(user=User)
            context['card'] = card
        except:
            pass

    return render(request,"base/index.html",context)

def test(request):
    context = {}
    return render(request,"base/testpage.html",context)

def test_dashboard(request):
    return render(request,"base/testdashboard.html")

def signup(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)

        if form.is_valid():
            current_user = form.save()
            new_user = user.objects.create(
                user = current_user,
                api_key = secrets.token_hex(16),
            )

            package = Package.objects.get(name="Free")

            subscription = Subscription.objects.create(
                user = current_user,
                plan = package,
                current_period_start = "",
                current_period_end = "",
            )
            messages.success(request,"Account successfully created.")
            return redirect('signin')
        else:
            messages.error(request,"There's an error!")
            return redirect('signup')
    context = {'form':form}
    return render(request,"base/signup.html",context)

def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('dashboard')
        else:
            messages.error(request,'username or password is incorrect')
            return redirect('signin')
    return render(request,"base/signin.html")

@login_required(login_url="signin") 
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required(login_url="signin") 
def dashboard(request):
    User = request.user
    current_user = user.objects.get(user=User)
    app = App.objects.filter(user=User)

    context = {'User':User,'user':current_user,'apps':app}

    try:
        card = Card.objects.get(user=User)
        context['card'] = card
    except:
        pass

    try:
        payment_history = PaymentHistory.objects.all().filter(user=User)
        context['payment_historys'] = payment_history
    except:
        pass

    return render(request,"base/dashboard.html",context)

def create_app(request):
    if request.method == "POST":
        name = request.POST.get('app_name')

        User = request.user
        current_user = user.objects.get(user=User)
        app = App.objects.filter(user=User)

        subscription = Subscription.objects.get(user=User)

        package = Package.objects.get(name=subscription.plan.name)

        if subscription.plan.name == "Enterprise" or app.count() < package.max_apps:
            if App.objects.filter(name=name).exists():
                return JsonResponse({'error': "App with the same name already exists!"})
            else:
                app = App.objects.create(
                    user = request.user,
                    name = name,
                )

                return JsonResponse({'data':'App has been created successfully!','name': app.name})
        else:
            return JsonResponse({'error': "Maximum app limit exceded!"})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def update_profile(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        current_user = User.objects.get(username=request.user)
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = email
        current_user.save()

        return JsonResponse({'data':"Account has been updated successfully!",'first_name': current_user.first_name,'last_name':current_user.last_name,'email':current_user.email})

    return JsonResponse({'error': "There's an error!"})

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

def payment_success(request):
    return render(request,"base/success.html")

def payment_cancelled(request):
    return render(request,"base/cancelled.html")

@csrf_exempt
def create_checkout_session(request,lookup_name):
    print(request.method)
    if request.method == 'GET':
        domain_url = 'http://127.0.0.1:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + 'payment-success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'payment-cancelled/',
                payment_method_types=['card'],
                metadata = {
                    'package':lookup_name,
                    'client_reference_id' :request.user.id if request.user.is_authenticated else None,
                    },
                
                mode='subscription',
                line_items=[
                    {
                        'price': settings.PRICE_IDS[lookup_name],
                        'quantity': 1,
                    }
                ],
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

def update_card(request):
    if request.method == "POST":
        card_number = request.POST.get('card_number')
        expiration_date = request.POST.get('expiration_date')
        cvc = request.POST.get('cvc')

        exp_month = expiration_date.split("/")[0]
        exp_year = expiration_date.split("/")[1]

        user_ = request.user
        subscription = Subscription.objects.get(user=user_)
        stripe_customer = StripeCustomer.objects.get(user=user_)

        stripe.api_key = settings.STRIPE_SECRET_KEY

        customer = stripe.Customer.retrieve(stripe_customer.stripeCustomerId)


        #create new payment method
        new_payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": card_number,
                "exp_month": exp_month,
                "exp_year": exp_year,
                "cvc": cvc,
            },
        )

        try:
            # Attach the Payment Method to a customer
            new_payment_method.attach(customer=customer.id)


            # Create a Payment Intent
            payment_intent = stripe.PaymentIntent.create(
                amount=50,  # Amount in cents
                currency="usd",
                payment_method=new_payment_method.id,
                customer=customer.id,
                confirmation_method="manual",
                confirm=True,
            )

            if payment_intent.status != "succeeded":
                # Confirm the Payment Intent
                confirmtion = stripe.PaymentIntent.confirm(payment_intent.id)

            # Retrieve the Payment Method object
            new_payment_method = stripe.PaymentMethod.retrieve(new_payment_method.id)
            print(new_payment_method)

            # Check the card.checks attribute
            if new_payment_method.card.checks.cvc_check == "pass" or new_payment_method.card.checks.address_line1_check == "pass":
                print("Card was verified!")
                
                stripe_subscription = stripe.Subscription.retrieve(subscription.stripeSubscriptionId)

                #get old payment method
                old_payment_method = stripe.PaymentMethod.retrieve(stripe_subscription.default_payment_method)

                #detach payment method
                stripe.PaymentMethod.detach(old_payment_method.id)

                #attch payment method to customer
                new_payment_method.attach(customer=stripe_customer.stripeCustomerId)

                customer = stripe.Customer.modify(
                    stripe_customer.stripeCustomerId,
                    invoice_settings={
                        "default_payment_method": new_payment_method.id,
                    },
                )

                stripe.Subscription.modify(
                    subscription.stripeSubscriptionId,
                    default_payment_method = new_payment_method.id,
                    metadata={
                        "client_reference_id":request.user.id if request.user.is_authenticated else None,
                    }
                )

                try:
                    # Create the refund
                    refund = stripe.Refund.create(
                        payment_intent=payment_intent.id,
                        amount=50,  # The amount to refund in cents
                    )
                    print('Refund created:', refund.id)
                except stripe.error.StripeError as e:
                    print('Error creating refund:', e)

                response = {
                    'data': 'Card has been updated successfully! refresh to see changes.'
                }

            else:
                print("Card could not be verified.")
                response = {
                    'error': "Card could not be verified."
                }

        except stripe.error.CardError as e:
            # Handle the card error
            print("Card Error:", e)
            print("Code:", e.code)
            print("Message:", e.user_message)

            response = {
                'error': e.user_message
            }


        except stripe.error.StripeError as e:
            # Handle other Stripe errors
            print("Stripe Error:", e)

            response = {
                    'error': "Card could not be verified."
            }


        except Exception as e:
            # Handle other exceptions
            print("Error:", e)

            response = {
                    'error': "Card could not be verified."
            }
        

        return JsonResponse(response)

def change_subscription(request):
    if request.method == "POST":
        lookup_name = request.POST.get('lookup_name')

        user_ = request.user
        subscription = Subscription.objects.get(user=user_)

        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            retrived_subscrition = stripe.Subscription.retrieve(
                subscription.stripeSubscriptionId,
            )

            old_item_id = retrived_subscrition['items']['data'][0]['id']

            stripe.Subscription.modify(
                subscription.stripeSubscriptionId,
                items=[{
                    "price": settings.PRICE_IDS[lookup_name],
                }],
                metadata={
                    "client_reference_id":request.user.id if request.user.is_authenticated else None,
                }
            )

            stripe.Subscription.modify(
                subscription.stripeSubscriptionId,
                items=[{
                    'id': old_item_id,
                    'deleted': True,
                }]
            )

            subscription = Subscription.objects.get(user=user_)

            package = Package.objects.get(name=lookup_name)

            response = {
                    'data': f"You have changed your subscription to {lookup_name}. You will be charged ${package.price} for your new plan from next billing date - {subscription.current_period_end}, until then you can continue to use your current plan and it's benefits."
            }

        except stripe.error.StripeError as e:
            # Handle other Stripe errors
            print("Stripe Error:", e)

            response = {
                    'error': "Package can't be switched."
            }

        except Exception as e:
            # Handle other exceptions
            print("Error:", e)

            response = {
                    'error': "Package can't be switched."
            }

        return JsonResponse(response)

def delete_card(request):
    if request.method == "POST":
        stripe.api_key = settings.STRIPE_SECRET_KEY
        user_ = request.user

        stripe_customer = StripeCustomer.objects.get(user=user_)

        subscription_ = Subscription.objects.get(user=user_)

        customer = stripe.Customer.modify(
            stripe_customer.stripeCustomerId,
            metadata = {
                "card-deletion":True
                
            }
        )

        subscription = stripe.Subscription.retrieve(subscription_.stripeSubscriptionId)

        payment_method = stripe.PaymentMethod.retrieve(subscription.default_payment_method)
        stripe.PaymentMethod.detach(payment_method.id)

        stripe.Subscription.delete(subscription.id)

        return JsonResponse({'data':'Card has been deleted successfully!'})

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    print(event['type'])

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # print("checkout.session.completed: ",session)

        # Fetch all the required data from session
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get('subscription')

        # Get the user and create a new StripeCustomer
        user_ = User.objects.get(id=client_reference_id)
        StripeCustomer.objects.create(
            user=user_,
            stripeCustomerId=stripe_customer_id,
        )

        #get stripe customer
        customer = stripe.Customer.retrieve(session['customer'])
        # print(customer)
        
        subscription = stripe.Subscription.retrieve(stripe_subscription_id)

        package = Package.objects.get(name=session.get('metadata')['package'])
        
        subscription_ = Subscription.objects.get(
            user=user_
        )

        subscription_.stripeSubscriptionId=stripe_subscription_id
        subscription_.plan=package
        subscription_.current_period_start=str(datetime.utcfromtimestamp(subscription['current_period_start']))
        subscription_.current_period_end = str(datetime.utcfromtimestamp(subscription['current_period_end']))
        subscription_.save()

        payment_history = PaymentHistory.objects.create(
                user=user_,
                amount=package.price,
                status="Successful",
        )

        stripe.Customer.modify(
            customer.id,
            metadata = {
                'client_reference_id' : client_reference_id,
            },
        )

        payment_method = stripe.PaymentMethod.retrieve(subscription.default_payment_method)

        card_info = payment_method.card

        Card.objects.create(
            user=user_,
            brand=card_info.brand,
            exp_month=card_info.exp_month,
            exp_year=card_info.exp_year,
            last4=card_info.last4
        )

        current_user = user.objects.get(user=user_)
        current_user.package = package
        current_user.save()

        print(user_.username + ' just subscribed.')

    elif event['type'] == 'customer.subscription.updated':
        session = event['data']['object']
        # print("customer.subscription.updated: ",session)

        try:
            #get stripe customer
            customer = stripe.Customer.retrieve(session['customer'])
            # print(customer)

            user_ = User.objects.get(id=customer.metadata['client_reference_id'])
            current_user = user.objects.get(user=user_)

            try:
                plan = stripe.Product.retrieve(session.get('items')['data'][1]['plan']['product'])
            except:
                plan = stripe.Product.retrieve(session.get('items')['data'][0]['plan']['product'])

            package = Package.objects.get(name=plan['name'])

            current_user.package = package
            current_user.save()

            subscription = Subscription.objects.get(user=user_)
            subscription.current_period_start = str(datetime.utcfromtimestamp(session.get('current_period_start')))
            subscription.current_period_end = str(datetime.utcfromtimestamp(session.get('current_period_end')))
            subscription.save()

            try:
                subscription = stripe.Subscription.retrieve(subscription.stripeSubscriptionId)

                payment_method = stripe.PaymentMethod.retrieve(subscription.default_payment_method)

                card_info = payment_method.card

                card = Card.objects.get(user=user_)
                card.brand=card_info.brand
                card.exp_month=card_info.exp_month
                card.exp_year=card_info.exp_year
                card.last4=card_info.last4
                card.save()

                print(card.last4)
            except Exception as e:
                # Handle other exceptions
                print("Error:", e)
        except Exception as e:
            # Handle other exceptions
            print("Error:", e)

    elif event['type'] == 'invoice.payment_succeeded':
        session = event['data']['object']
        # print('invoice.payment_succeeded: ',session)
        print("working payment succeed")
        try:
            #get stripe customer
            customer = stripe.Customer.retrieve(session['customer'])
            # print(customer)

            user_ = User.objects.get(id=customer.metadata['client_reference_id'])

            subscription = stripe.Subscription.retrieve(session.get('subscription'))

            plan = stripe.Product.retrieve(subscription['items']['data'][0]['price']['product'])
            
            package = Package.objects.get(name=plan['name'])

            subscription = Subscription.objects.get(user=user_)
            subscription.plan = package
            subscription.save(force_update=True)

            payment_history = PaymentHistory.objects.create(
                user=user_,
                amount=package.price,
                status="Successful",
            )
            print("working payment succeed 1")
        except Exception as e:
            # Handle other exceptions
            print("Error:", e)

    elif event['type'] == 'invoice.payment_failed':
        session = event['data']['object']
        
        try:
            #get stripe customer
            customer = stripe.Customer.retrieve(session['customer'])
            # print(customer)

            user_ = User.objects.get(id=customer.metadata['client_reference_id'])

            subscription = stripe.Subscription.retrieve(session.get('subscription'))

            plan = stripe.Product.retrieve(subscription['items']['data'][0]['price']['product'])
            
            package = Package.objects.get(name=plan['name'])

            subscription = Subscription.objects.get(user=user_)
            subscription.plan = package
            subscription.save(force_update=True)

            payment_history = PaymentHistory.objects.create(
                user=user_,
                amount=package.price,
                status="Failed",
            )
        except Exception as e:
            # Handle other exceptions
            print("Error:", e)

    elif event['type'] == 'customer.subscription.deleted':
        session = event['data']['object']

        # print("customer.subscription.deleted: ",session)

        customer = stripe.Customer.retrieve(session['customer'])

        user_ = User.objects.get(id=customer.metadata['client_reference_id'])

        package = Package.objects.get(name="Free")

        current_user = user.objects.get(user=user_)
        current_user.package = package
        current_user.save()

        card = Card.objects.get(user=user_)
        card.delete()

        strie_customer = StripeCustomer.objects.get(user=user_)
        strie_customer.delete()

        subscription = Subscription.objects.get(user=user_)
        subscription.plan = package
        subscription.current_period_start = ""
        subscription.current_period_end = ""
        subscription.save()

        stripe.Customer.delete(customer.id)
        
    return HttpResponse(status=200)


    