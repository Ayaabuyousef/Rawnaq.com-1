from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import views
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import (Item, Order, OrderItem)
# Create your views here.

# @login_required
def index(request):
    return render(request,'../templates/registration/index.html')
def sign_up(request):
    context = {}
    form = UserCreationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request,user)
            # login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return render(request,'../templates/registration/index.html') 
    context['form']=form
    return render(request,'../templates/registration/sign_up.html',context) 
    



class HomeView(ListView):
    model = Item
    template_name = "home.html"

class ProductView(DetailView) :
    model = Item
    template_name = "product.html"


def add_to_cart(request, pk) :
    item = get_object_or_404(Item, pk = pk )
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user = request.user,
        ordered = False
    )
    order_qs = Order.objects.filter(user=request.user, ordered= False)

    if order_qs.exists() :
        order = order_qs[0]
        
        if order.items.filter(item__pk = item.pk).exists() :
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Added quantity Item")
            return redirect("core:product", pk = pk)
        else:
            order.items.add(order_item)
            messages.info(request, "Item added to your cart")
            return redirect("core:product", pk = pk)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date = ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item added to your cart")
        return redirect("core:product", pk = pk)


def remove_from_cart(request, pk) :
    item = get_object_or_404(Item, pk = pk )
    order_qs = Order.objects.filter(
        user=request.user, 
        ordered= False
    )
    if order_qs.exists() :
        order = order_qs[0]
        if order.items.filter(item__pk = item.pk).exists() :
            order_item = OrderItem.objects.filter(
                item=item,
                user = request.user,
                ordered = False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "Item remove from your cart")
            return redirect("core:product", pk = pk)
        else:
            messages.info(request, "This Item not in your cart")
            return redirect("core:product", pk = pk)
    else:
        #add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("core:product", pk = pk)