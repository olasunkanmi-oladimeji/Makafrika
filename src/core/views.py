from turtle import color
from django.shortcuts import render,get_object_or_404,redirect
from .models import (Banner,Category,Product,OrderItem,Order,Address,ProductReview,
                    Address,Payment,Wishlist,Coupon,Color,Size,Refund)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg
from django.http import JsonResponse
from .forms import ReviewAdd,CheckoutForm,CouponForm,RefundForm
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.template.loader import render_to_string
import random
import datetime
import string
# Create your views here.
def AboutView(request):
    return render(request,'core/about-us.html')
def HomeView(request):
    banner = Banner.objects.all().order_by("-id")
    categories = Category.objects.all().order_by('title')
    product  = Product.objects.all().order_by('-id')
    
    page = request.GET.get('page', 1)

    paginator = Paginator(product, 8)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context ={
        'categories' : categories,
        'page_obj':page_obj,
        'banner':banner,
        

    }
    return render(request,"core/home-page.html",context)

def save_review(request,pid):
	product=Product.objects.get(pk=pid)
	user=request.user
	review=ProductReview.objects.create(
		user=user,
		product=product,
		review_text=request.POST['review_text'],
		review_rating=request.POST['review_rating'],
		)
	data={
		'user':user.username,
		'review_text':request.POST['review_text'],
		'review_rating':request.POST['review_rating']
	}

	# Fetch avg rating for reviews
	avg_reviews=ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
	# End

	return JsonResponse({'bool':True,'data':data,'avg_reviews':avg_reviews})

def product_detail(request,slug):
    
    product=Product.objects.get(slug=slug)
    related_products=Product.objects.filter(category=product.category).exclude(slug=slug)[:1]
    reviewForm= ReviewAdd()
    canAdd=True

    reviewCheck=ProductReview.objects.filter(user=request.user,product=product).count()
    if request.user.is_authenticated:
        if reviewCheck > 0:
            canAdd=False
    
    reviews=ProductReview.objects.filter(product=product)

    avg_reviews=ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))

    context={
        'data':product,
        'related':related_products,
        'reviewForm':reviewForm,
        'canAdd':canAdd,
        'reviews':reviews,
        'avg_reviews':avg_reviews
        
    }

    return render(request, 'core/product-page.html',context)

@login_required
def add_to_cart(request,slug):
    item = get_object_or_404(Product,slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order= order_qs[0]
        #check if order item is already ordered

        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:cart-order")
        else:
            order.items.add(order_item)
            messages.info(request, "item was added to your cart.")
            return  redirect(request.META['HTTP_REFERER'])

    #if order doesn't exist
    else:
        ordered_date=timezone.now()
        order =Order.objects.create(user=request.user,ordered_date=ordered_date, delivery_date= ordered_date )
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:cart-order")

@login_required
def remove_from_cart(request,slug):

    item = get_object_or_404(Product,slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order= order_qs[0]
        #check if order item is already ordered

        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                        item=item,
                        user=request.user,
                        ordered=False)[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
        else:
        # item is not part of cart message
            messages.info(request, "This item was not in your cart")
            return redirect('core:cart-order')
    else:
        # no order message
        messages.info(request, "You do not have an active order")
        return redirect('core:Items_detail',slug=slug)
    return redirect('core:product_detail',slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return  redirect(request.META['HTTP_REFERER'])
        else:
            messages.info(request, "This item was not in your cart")
            return  redirect(request.META['HTTP_REFERER'])

    else:
        messages.info(request, "You do not have an active order")
        return redirect('core:cart-order')

class cartfunc(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            wlist=Wishlist.objects.filter(user=self.request.user).order_by('-id')
            context = {
                'cart_data': order,
                'wlist':wlist
            }
            return render(self.request, 'core/cart-page.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return render(self.request, 'core/cart-page.html')

# Create your views here.
def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

class CheckoutView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'order': order,
                'form':form,
                'couponform': CouponForm(),
                'DISPLAY_COUPON_FORM': True,
            }
            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            return render(self.request, 'core/checkout-page.html',context)
        except ObjectDoesNotExist:
            messages.info(self.request, "you do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    #print("Using the default shipping address")
                    messages.info(self.request, "Using the default shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    name = form.cleaned_data.get(
                        'name')
                    email = form.cleaned_data.get(
                        'email')
                    address = form.cleaned_data.get(
                        'address')

                    phone_no=form.cleaned_data.get(
                        'phone_no')

                    if is_valid_form([address, name,email,phone_no]):
                        shipping_address = Address(
                            user=self.request.user,
                            name=name,
                            email=email,
                            phone_no=phone_no,
                            address=address,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")


                payment_option = form.cleaned_data.get('payment_option')


                if payment_option == 'P':
                    return redirect('core:payment', payment_option='Paystack')
                elif payment_option == 'C':
                    return redirect('core:cashpayment')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
            else:
                 print("User is entering a new user")

        except ObjectDoesNotExist:

            messages.error(self.request, "You do not have an active order")
            return redirect("core:order-summary")

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

class Paystacktview(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.shipping_address:
                pk_public = settings.PAYSTACK_PUBLIC_KEY
                context = {
                    'order': order,
                    'pk_public':pk_public,
                    'DISPLAY_COUPON_FORM': False

                    }
                return render(self.request, 'core/order-confirm.html',context)
            else:

                messages.warning(self.request, "You do have not added a billing addres")
                return redirect("core:order-summary")
        except ObjectDoesNotExist:
            pass


def verify(request,id):


    order =Order.objects.get(user=request.user, ordered=False)
    payment = Payment()
    #payment.payment_charge_id = response
    payment.user =request.user
    payment.amount = order.get_total()
    payment.save()

    order_items = order.items.all()
    order_items.update(ordered =True)
    for item in order_items:
        item.save()
    order.ordered =True
    order.payment = payment
    order.ref_code = create_ref_code()

    current_time = order.delivery_date
    
    d_day =current_time + datetime.timedelta(days=5)
    order.delivery_date =d_day
    order.save()

    messages.success(request,'your order was succesful ' + order.ref_code )
    return redirect ('core:my_orders')

def cashpayment(request):
    order =Order.objects.get(user=request.user, ordered=False)
    payment = Payment()

    payment.user =request.user
    refcode=create_ref_code()
    payment.stripe_charge_id=refcode
    payment.amount = order.get_total()
    payment.save()
    
    order_items = order.items.all()
    order_items.update(ordered =True)
    for item in order_items:
        item.save()
    order.ordered =True
    order.payment = payment
    order.ref_code = refcode

    current_time = order.delivery_date
    d_day =current_time + datetime.timedelta(days=5)
    order.delivery_date =d_day
    order.save()

    messages.success(request,'your order was succesful ' + order.ref_code )
    return redirect ('core:my_orders')

@login_required
def my_orders(request):
	orders=Order.objects.filter(user=request.user,ordered=True).order_by('-id')
	return render(request, 'core/orders.html',{'orders':orders})

# Order Detail
def my_order_items(request,id):
	order=Order.objects.get(pk=id)
	orderitems=OrderItem.objects.filter(order=order).order_by('-id')
	return render(request, 'core/order-items.html',{'orderitems':orderitems})

# Wishlist
@login_required
def add_wishlist(request, id):
    product=Product.objects.get(id=id)
    data={}
    checkw=Wishlist.objects.filter(product=product,user=request.user).count()
    if checkw > 0:
        data={
            'bool':False
        }
    else:
        wishlist=Wishlist.objects.create(
            product=product,
            user=request.user
        )
        data={
            'bool':True
        }
    return redirect(request.META['HTTP_REFERER'])

@login_required
def delete_wishlist(request, id):

    product=Product.objects.get(id=id)
    data={}
    checkw=Wishlist.objects.filter(product=product,user=request.user)
    
    checkw.delete()
    return redirect(request.META['HTTP_REFERER'])
	
# My Wishlist
def my_wishlist(request):
	wlist=Wishlist.objects.filter(user=request.user).order_by('-id')
	return render(request, 'core/wishlist.html',{'wlist':wlist})

def category(request,category_slug):
    #Category
    categorys = Category.objects.all().order_by('title')
    
    colors=Color.objects.all().order_by('-id')
    sizes=Size.objects.all().order_by('title')

    category = None

    minprice = 500
    maxprice = request.GET.get('maxPrice')
    color=request.GET.get('color')
   

    if category_slug:
        category = get_object_or_404(categorys,slug=category_slug)
        item = Product.objects.filter(category=category).order_by('-id')
        itemfilter=item.filter( Q(price__range=(minprice,maxprice))|
                            Q(discount_price__range=(minprice,maxprice))
                            )
        if color:
            itemfilter=item.filter(color__id__in=color)
                
    #pagination and item
    page = request.GET.get('page', 1)

    if itemfilter:

        paginator = Paginator(itemfilter, 12)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
    
    
    else:
        paginator = Paginator(item, 12)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        


    return render(request,'core/shop.html',{   'category':category,
                                                'page_obj':page_obj,
                                                    'categorys' : categorys,
                                                    
                                                    'colors':colors,
                                                    'sizes':sizes
                                                    } )

def searchitem(request):
    categorys = Category.objects.all().order_by('title')
    
    colors=Color.objects.all().order_by('-id')
    sizes=Size.objects.all().order_by('title')
    #Search
    query = request.GET.get('q','')
    if query:
        queryset = (Q(title__icontains=query)|
                    Q(detail__icontains=query)|
                    Q(specs__icontains=query)|
                    Q(label_text__icontains=query)|
                    Q(category__title__icontains=query))
                    
        results =  Product.objects.filter(queryset).distinct()
        
    
    else:
       results = []
    queryset_cat =( Q(category__title__icontains=query))
    related_product = Product.objects.filter(queryset_cat)

    return render(request, 'core/shop.html',{        
                                                'query':query,
                                                'results':results,
                                                'categorys' : categorys,
                                                
                                                'colors':colors,
                                                'sizes':sizes,
                                                'related_product':related_product,
                                                
                                                
   } )

class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "core/refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:refund-item")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:refund-item")

def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        order = Order.objects.get(
                    user=self.request.user, ordered=False)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order.coupon = get_coupon(self.request, code)
                    
                order.save()
                messages.success(self.request, "Successfully added coupon")

                
                
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")
