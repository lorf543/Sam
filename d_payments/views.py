import stripe
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render,redirect, get_object_or_404,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from d_store.models import Product
from django.db.models import Q
from django.contrib.auth.models import User

from .models import Invoice,InvoinceProduct
from .forms import UserProfileForm, SaleForm
from d_store.models import CartItem, Product,UserProfile

stripe.api_key = settings.STRIPE_SECRET_KEY




@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': str(e)}, status=400)

    # Manejar el evento de pago exitoso
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_successful_payment(session)

    return JsonResponse({'status': 'success'})

def handle_successful_payment(session):

    user_id = session['metadata'].get('user_id')
    if not user_id:
        return
    
            # Usar latest_charge para obtener el Charge
            # Recuperar el PaymentIntent
    payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
    
    charge = stripe.Charge.retrieve(payment_intent.latest_charge)
    receipt_url = charge.receipt_url

    try:
        # Crear una factura
        invoice = Invoice.objects.create(
            user_id=user_id,
            stripe_invoice_id=session.get('payment_intent'),
            total_amount=session['amount_total'] / 100,
            currency=session['currency'],
            status='paid',
            receipt_url=receipt_url
        )
        print(f"Invoice {invoice.id} created successfully.")
    except Exception as e:
        print(f"Error creating invoice: {e}")
        return

    # Reducir stock y vaciar carrito
    try:
        cart_items = CartItem.objects.filter(user_id=user_id)
        for item in cart_items:
            product = item.product
            if product.stock >= item.quantity:
                product.stock -= item.quantity
                product.save()
            else:
                print(f"Insufficient stock for {product.brand}")
        cart_items.delete()
    except Exception as e:
        print(f"Error processing cart items: {e}")
    
    
@login_required
def checkout_htmx(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    cart_items = request.user.cart_items.all()
    total_price = sum(item.get_total_price() for item in cart_items)

    # Crear sesión de Stripe
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'dop',
                    'product_data': {'name': item.product.brand},
                    'unit_amount': int(item.product.price * 100),
                },
                'quantity': item.quantity,
            }
            for item in cart_items
        ],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment_success')),
        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
        metadata={  # Agrega los metadatos aquí
            'user_id': request.user.id,  # Transmite el ID del usuario
        },
    )
    return redirect(session.url, code=303)
    
@login_required
def payment_success(request):
    return render(request, 'd_payments/payment_success.html')

@login_required
def payment_cancel(request):
    return render(request, 'd_payments/payment_cancel.html')    
    
    
@ensure_csrf_cookie
@login_required
def view_cart(request):
    cart_items = request.user.cart_items.all()

    context = {
        'cart_items': cart_items,
    }
    return render(request, 'cart/view_cart.html', context)

@login_required
def update_cart_items(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
    quantity = int(request.POST.get('quantity', 0))

    if quantity < 1:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save()

    # Obtener todos los artículos actualizados en el carrito
    cart_items = CartItem.objects.filter(user=request.user)

    # Calcular el precio total del carrito
    total_price = sum(item.get_total_price() for item in cart_items)

    # Retornar solo los artículos actualizados y el total
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }

    return render(request, 'cart/cart_items_and_total.html', context)


@login_required
def update_cart_total(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)


    context = {
        'total_price': total_price,
    }

    return render(request, 'cart/cart_total.html', context)

@login_required
def add_to_cart_htmx(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Retorna una respuesta sin contenido
    return HttpResponse(status=204)


@login_required(login_url="login")
def vender(request, slug):
    # Obtén el producto usando el slug
    product = get_object_or_404(Product, slug=slug)
    form = SaleForm()
    
    # Asegúrate de que el producto existe
    if not product:
        return HttpResponse("Producto no encontrado", status=404)

    # Puedes agregar más lógica para manejar la venta aquí
    customer = UserProfile.objects.filter(phone='809-555-5555').first()

    # Pasar el producto y cliente al contexto
    context = {
        'product': product,
        'customer': customer,
        'form':form
    }
    return render(request, 'd_payments/ventas/vender.html', context)

def check_customer(request):
    if request.method == 'POST':
        phone = request.POST.get('customer-phone')
        customer = UserProfile.objects.filter(phone=phone).first()
        request.session['phone'] = phone
        form = SaleForm()
        
        # Assuming you have a way to fetch the product based on slug or another identifier
        product = Product.objects.first()  # Example; fetch product based on your logic
         
        context = {
            'customer': customer, 
            'form': form, 
            'product': product
        }
        
        if customer:
            return render(request, 'd_payments/ventas/found.html', context)
        else:
            return render(request, 'd_payments/ventas/not_found.html', context)
    return HttpResponse(redirect('home'))


@login_required(login_url="login")
def procesar_venta(request, slug):
    # Recuperar el producto basado en el slug proporcionado
    product = get_object_or_404(Product, slug=slug)
    print(f"Producto recuperado: {product}, Stock: {product.stock}")

    phone = request.session.get('phone')
    customer = UserProfile.objects.filter(phone=phone).first()
    print(f"Cliente encontrado: {customer}")
    
    if request.method == 'POST':
        form = SaleForm(request.POST)
        form.instance.product = product  # Establecer el producto seleccionado

        if form.is_valid():
            # Recuperar los datos del formulario
            quantity = form.cleaned_data['quantity']
            payment_method = form.cleaned_data['payment_method']

            # Verificar si la cantidad solicitada es mayor al stock disponible
            if quantity > product.stock:
                return render(request, 'd_payments/ventas/error.html', {
                    'error': f'La cantidad solicitada ({quantity}) es mayor al stock disponible ({product.stock})',
                    'product': product
                })
                    
            # Guardar la factura si la cantidad es válida
            invoice = form.save(commit=False)
            invoice.user = customer.user  # Asignar el objeto User asociado con UserProfile
            invoice.product = product
            invoice.currency = "DOP"
            invoice.payment_method = payment_method
            invoice.added_by = request.user
            invoice.status = "Pagado"
            invoice.quantity = quantity
            invoice.total_amount = quantity * product.price
            invoice.save()

            # Actualizar el stock del producto después de guardar la factura
            product.stock = product.stock - quantity
            product.save()

            return render(request, 'd_payments/ventas/confirmacion.html', {'product': product, 'invoice': invoice, 'customer':customer})

        else:
            return render(request, 'd_payments/ventas/error.html', {'error': 'Formulario inválido', 'product': product})

    else:
        form = SaleForm()

    return render(request, 'd_payments/ventas/procesar_venta.html', {'form': form})


    #         # Make sure the product and quantity are valid
    #         if product and quantity > 0:
    #             # Create an invoice for the sale
    #             invoice = InvoinceProduct(
    #                 user=request.user,
    #                 product=product,
    #                 quantity=quantity,
    #                 payment_method=payment_method,
    #                 total_amount=product.price * quantity,
    #                 currency='USD',  # Adjust the currency as needed
    #                 status='Pagado',  # Set the status based on your logic
    #                 added_by=request.user,
    #                 updated_by=request.user,
    #             )
    #             # Save the invoice object to the database
    #             invoice.save()

    #             # Update the product stock
    #             product.stock -= quantity
    #             product.save()

    #             # Redirect or render a confirmation page with the invoice details
    #             return render(request, 'd_payments/ventas/confirmacion.html', {'invoice': invoice})
    #         else:
    #             # Handle invalid data (e.g., product or quantity issues)
    #             return render(request, 'd_payments/ventas/error.html', {'error': 'Invalid product or quantity'})
    #     else:
    #         # Handle the case where the form is not valid
    #         return render(request, 'd_payments/ventas/error.html', {'error': 'Formulario no válido'})
    # else:
    #     form = SaleForm()  # Initialize the form for the user to fill
    # return render(request, 'd_payments/ventas/procesar_venta.html', {'product': product, 'customer': customer})

def add_customer(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()  # El método save() maneja tanto User como UserProfile
            return redirect('check_customer')  # Redirige a la página de verificación
    else:
        form = UserProfileForm()

    context = {'form': form}
    return render(request, 'd_payments/ventas/add_customer.html', context)