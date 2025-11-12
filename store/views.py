from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
def product_list(request):
    categories = request.GET.getlist('category')
    
    if categories:
        products = Product.objects.filter(category__in=categories)
    else:
        products = Product.objects.all()
    
    # Get all available categories for the filter
    all_categories = Product.CATEGORY_CHOICES
    
    context = {
        'products': products,
        'all_categories': all_categories,
        'selected_categories': categories,
    }
    return render(request, 'product_list.html', context)

def dashboard(request):
    if not request.user.is_staff:
        return redirect('store:product_list')
        
    # Get dashboard statistics
    total_products = Product.objects.count()
    total_users = User.objects.count()
    recent_products = Product.objects.order_by('-id')[:5]
    
    # Calculate total inventory value
    total_value = Product.objects.aggregate(total=Sum('price'))['total'] or 0
    
    context = {
        'total_products': total_products,
        'total_users': total_users,
        'total_value': total_value,
        'recent_products': recent_products,
    }
    return render(request, 'dashboard.html', context)

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        # Get cart items for response
        cart_items = cart.items.all()
        cart_data = []
        total = 0
        
        for item in cart_items:
            item_total = item.product.price * item.quantity
            total += item_total
            cart_data.append({
                'name': item.product.name,
                'price': str(item.product.price),
                'quantity': item.quantity,
                'total': str(item_total)
            })
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart!',
            'cart_items': cart_data,
            'cart_total': str(total),
            'cart_count': cart_items.count()
        })
    
    return redirect('store:product_list')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    cart_data = []
    total = 0
    
    for item in cart_items:
        item_total = item.product.price * item.quantity
        total += item_total
        cart_data.append({
            'id': item.id,
            'name': item.product.name,
            'price': str(item.product.price),
            'quantity': item.quantity,
            'total': str(item_total),
            'image_url': item.product.image.url if item.product.image else '/static/placeholder.png'
        })
    
    return JsonResponse({
        'cart_items': cart_data,
        'cart_total': str(total),
        'cart_count': cart_items.count()
    })

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        action = request.POST.get('action')
        
        # Store cart reference before potential deletion
        cart = cart_item.cart
        
        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        
        # Get fresh cart data
        cart_items = cart.items.all()
        cart_data = []
        total = 0
        
        for item in cart_items:
            item_total = item.product.price * item.quantity
            total += item_total
            cart_data.append({
                'id': item.id,
                'name': item.product.name,
                'price': str(item.product.price),
                'quantity': item.quantity,
                'total': str(item_total),
                'image_url': item.product.image.url if item.product.image else '/static/placeholder.png'
            })
        
        return JsonResponse({
            'cart_items': cart_data,
            'cart_total': str(total),
            'cart_count': cart_items.count()
        })
    
    return JsonResponse({'error': 'Invalid request'})

@login_required
def remove_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        
        # Return updated cart data
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        cart_data = []
        total = 0
        
        for item in cart_items:
            item_total = item.product.price * item.quantity
            total += item_total
            cart_data.append({
                'id': item.id,
                'name': item.product.name,
                'price': str(item.product.price),
                'quantity': item.quantity,
                'total': str(item_total),
                'image_url': item.product.image.url if item.product.image else '/static/placeholder.png'
            })
        
        return JsonResponse({
            'cart_items': cart_data,
            'cart_total': str(total),
            'cart_count': cart_items.count()
        })
    
    return JsonResponse({'error': 'Invalid request'})