from django.contrib import admin
from django.contrib import admin
from .models import (Banner,Category,Product,OrderItem,Order,Address,ProductReview,
                    Address,Payment,Wishlist,Coupon,Color,Size,Refund)
# Register your models here.


admin.site.register(Size)
admin.site.register(Refund)
class BannerAdmin(admin.ModelAdmin):
	list_display=('alt_text','image_tag')
admin.site.register(Banner,BannerAdmin)

class CategoryAdmin(admin.ModelAdmin):
	list_display=('title','image_tag')
admin.site.register(Category,CategoryAdmin)

class ColorAdmin(admin.ModelAdmin):
	list_display=('title','color_bg')
admin.site.register(Color,ColorAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display=('title','image_tag','category','status',)
admin.site.register(Product,ProductAdmin)

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    
                    ]
    list_display_links = [
        'user',
        'being_delivered',
        
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted'
                   ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]
admin.site.register(Order,OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',]
admin.site.register(OrderItem,OrderItemAdmin)

class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'name',
        'address',
        'email',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type',]
    search_fields = ['user', 'address', 'name']
admin.site.register(Address,AddressAdmin)

admin.site.register(Payment)


admin.site.register(Wishlist)
admin.site.register(Coupon)
class ProductReviewAdmin(admin.ModelAdmin):
	list_display=('user','product','review_text','get_review_rating')
admin.site.register(ProductReview,ProductReviewAdmin)