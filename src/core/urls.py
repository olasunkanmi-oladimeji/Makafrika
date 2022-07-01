from django.urls import path,include
from . import views

from django.conf import settings
from django.conf.urls.static import static
app_name="core"
urlpatterns=[
    path("About", views.AboutView, name="aboutus"),
    path('<slug>/detail',views.product_detail,name='product_detail'),
    path('save-review/<int:pid>',views.save_review, name='save-review'),
    path('Add-To-cart/<slug>',views.add_to_cart,name='add_to_cart'),
    path('Remove-FROM-cart/<slug>',views.remove_from_cart,name='remove_from_cart'),
    path('Remove-Item-cart/<slug>',views.remove_single_item_from_cart,name='remove_item_cart'),
    path('order-cart', views.cartfunc.as_view(),name='cart-order'),
    path('checkout',views.CheckoutView.as_view(),name='checkout'),
    path('payment/<payment_option>',views.Paystacktview.as_view(),name='payment'),
    path('payment/verify/<id>',views.verify,name='verify'),
    path('cash-payment',views.cashpayment,name='cashpayment'),
    path('my-orders',views.my_orders, name='my_orders'),
    path('my-orders-items/<int:id>',views.my_order_items, name='my_order_items'),
    path('add-wishlist/<id>',views.add_wishlist, name='add_wishlist'),
    path('my-wishlist',views.my_wishlist, name='my_wishlist'),
    path('delete-item-wishlist/<id>',views.delete_wishlist, name='delete_wishlist'),
    path('search',views.searchitem,name='search'),
    path('product-category/<slug:category_slug>',views.category,name='category_detail'),
    path("add-coupon",views.AddCouponView.as_view(), name="addcoupon"),
    path('Refund-item',views.RequestRefundView.as_view(),name='refund-item'),
    


]