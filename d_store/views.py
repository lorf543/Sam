import re
from django.shortcuts import render,get_list_or_404,get_object_or_404,redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse

from django.http import Http404
from django.core.paginator import Paginator

from django.db.models import Q

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from .models import Car, UserProfile,Category,Product,CartItem,PossibleBuyer
from .filters import ProductFilter
from .forms import PossibleBuyerForm
from d_account.forms import CommentsForm
from . import cocedom 



# Create your views here.

def home(request):
    cars = Car.objects.all()
    
    context = {'cars':cars}
    return render(request,'d_store/index.html',context)

def view_car(request,slug):
    car = get_object_or_404(Car, slug=slug)
    cars = Car.objects.all()
    
    context={'car':car,'cars':cars}
    return render(request,'d_store/view_car.html',context)

def category_list(request,):
    categories = get_list_or_404(Category)   

    context = {
        'categories': categories,
    }
    
    return render(request, 'd_store/category_list.html', context)

def auto_parts(request, slug):
    selected_category = get_object_or_404(Category, slug=slug)
    all_products = selected_category.products_parts.all()

    # Aplicar filtros con la categoría seleccionada
    filtered_products = ProductFilter(
        request.GET, queryset=all_products.order_by('date_added'), category=selected_category
    )

    # Verificar productos en el carrito para el usuario autenticado
    in_cart = []
    if request.user.is_authenticated:
        in_cart = CartItem.objects.filter(user=request.user).values_list('product_id', flat=True)

    # Paginación
    current_page = request.GET.get('page', 1)
    try:
        paginator = Paginator(filtered_products.qs, 5)
        paginated_products = paginator.page(current_page)
    except:
        raise Http404

    context = {
        'filter': filtered_products,
        'products': paginated_products,
        'in_cart': in_cart
    }
    return render(request, 'd_store/auto_parts.html', context)

def add_to_cart_btn(request, product_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    # Obtener el producto
    product = get_object_or_404(Product, id=product_id)

    # Agregar el producto al carrito
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Renderizar el nuevo estado del botón
    context = {
        'product': product,
        'in_cart': True,  # Producto ahora está en el carrito
    }
    button_html = render_to_string('cart/cart_button.html', context, request=request)
    return HttpResponse(button_html)

def search_products(request):
    search_product = request.POST.get('search_product', "").strip()
    products = Product.objects.all()

    if search_product:  # Si hay búsqueda
        products = products.filter(
            Q(brand__icontains=search_product) | 
            Q(description__icontains=search_product) |
            Q(category__name__icontains=search_product)
        )

    # Renderizar el HTML directamente
    context = {'products': products}
    return render(request, 'partials/parts.html', context)

def view_part(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # Obtener productos relacionados (misma categoría, excluyendo el producto actual)
    related_products = Product.objects.filter(
        Q(category=product.category) & ~Q(id=product.id)
    ).order_by('-date_added')[:5]  # Limitar a los 5 más recientes

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'd_store/view_part.html', context)




@login_required(login_url="account_login")    
def handle_buyer(request,pk):
    buyer = get_object_or_404(PossibleBuyer, id=pk)
    car = buyer.car
    form = CommentsForm()
    
    context = {
        'buyer':buyer,
        'car':car,
        'form':form,
    }
    return render(request,'d_store/handle_buyer.html',context )



def buyer_list(request, pk):
    car = get_object_or_404(Car, id=pk)  
    buyers = PossibleBuyer.objects.filter(car=car)  
    
    print(buyers)
    
    context = {'buyers': buyers, 'car': car}
    return render(request, 'd_store/buyer_list.html', context)
    


def possiblebuyer(request, slug):
    car = get_object_or_404(Car, slug=slug)
    form = PossibleBuyerForm(request.POST or None)
    context = {'car': car, 'form': form}

    if request.method == 'POST' and 'HX-Request' in request.headers:
        cedula = request.POST.get('cedula', '').strip()

        if not re.match(r'^\d{3}-\d{7}-\d{1}$', cedula):
            context['error'] = "El formato de la cédula es incorrecto. Debe ser 000-0000000-0."
            return render(request, 'd_store/possiblebuyer_result.html', context)

        resultado = cocedom.ComprobarCedula(cedula)

        if not resultado or 'nombre' not in resultado:
            context['error'] = "La cédula no existe en el registro."
            return render(request, 'd_store/possiblebuyer_result.html', context)

        nombre_completo = resultado.get('nombre', '').strip()
        nombre_partes = nombre_completo.split()

        name = " ".join(nombre_partes[:2]).capitalize() if len(nombre_partes) > 1 else None
        last_name = " ".join(nombre_partes[-2:]).capitalize() if len(nombre_partes) > 1 else None

        if not name or not last_name:
            context['error'] = "No se pudo obtener información válida de la cédula."
            return render(request, 'd_store/possiblebuyer_result.html', context)

        context['nombre'] = nombre_completo.capitalize()
        context['cedula'] = resultado.get('cedula', '').capitalize()

        if form.is_valid():
            possible_buyer = PossibleBuyer.objects.create(
                car=car,
                cedula=cedula,
                name=name,
                last_name=last_name,
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                comment=form.cleaned_data.get('comment', '')  # 🔹 Guarda el comentario si existe
            )
            possible_buyer.save()
            context['success'] = "Tu solicitud ha sido enviada. Tan pronto como sea posible, estaremos en contacto contigo."

        return render(request, 'd_store/possiblebuyer_result.html', context)

    return render(request, 'd_store/possiblebuyer.html', context)



def calculate_payment(request):
    try:
        # Obtener valores de la URL y normalizar el formato numérico
        car_price = request.GET.get("car_price", "0").replace(",", ".")
        initial_payment = request.GET.get("initial_payment", "0").replace(",", ".")
        interest_rate = request.GET.get("interest_rate", "0").replace(",", ".")

        # Convertir a valores numéricos
        car_price = float(car_price)
        initial_payment = float(initial_payment)
        interest_rate = float(interest_rate)
        months = int(request.GET.get("months", 48))

        # Validaciones básicas
        if car_price <= 0 or months <= 0:
            return JsonResponse({"error": "Valores no válidos"}, status=400)

        # Calcular el capital financiado
        principal = car_price - initial_payment

        # Convertir la tasa de interés anual a tasa mensual
        monthly_interest_rate = (interest_rate / 100) / 12

        # Calcular el pago mensual
        if monthly_interest_rate > 0:
            monthly_payment = (principal * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -months)
        else:
            monthly_payment = principal / months  # Si no hay interés

        return HttpResponse(f"Estimado mensual ${monthly_payment:,.2f}")
    
    except Exception as e:
        return HttpResponse(f"Estimado mensual ${monthly_payment:,.2f}")

def check_info(request):
    phone = request.POST.get('phone')
    
    if len(phone) < 10:  # Verifica que tenga más de 11 caracteres
        return HttpResponse(
            "<p class='text-danger fw-bold small container text-wrap container'>Asegúrate de que tenga más de 11 caracteres sin guiones.</p>"
        )
    
    if UserProfile.objects.filter(phone=phone).exists():
        user = UserProfile.objects.get(phone=phone)
  
        
        return render(request,'partials/customer_info.html' ,{'user':user})
    else:
        return HttpResponse(
            "<p class='text-danger fw-bold small container'>Identificación no registrada.</p>"
        )





