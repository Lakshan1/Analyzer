from django.urls import path

from . import views

urlpatterns = [
    path("",views.index,name="index"),
    path("test/",views.test,name="test"),
    path("test-dashboard/",views.test_dashboard,name="test_dashboard"),
    path("signup/",views.signup,name="signup"),
    path("signin/",views.signin,name="signin"),
    path("logout/",views.logout_view,name="logout"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("create-app/",views.create_app,name="create_app"),
    path("update-profile/",views.update_profile,name="udate_profile"),
    path("update-card/",views.update_card,name="udate_card"),
    path("change-subscription/",views.change_subscription,name="change_subscription"),
    path("delete-card/",views.delete_card),


    path('config/', views.stripe_config), 
    path("payment-success/",views.payment_success,name="payment_success"),
    path("payment-cancelled/",views.payment_cancelled,name="payment_cancelled"),
    path("create-checkout-session/<str:lookup_name>/",views.create_checkout_session,name="create-checkout-session"),
    path('webhook/', views.stripe_webhook),
]