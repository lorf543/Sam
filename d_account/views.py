from django.shortcuts import get_list_or_404,get_object_or_404,render,redirect
from django.utils.timezone import now 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import HttpResponseForbidden

from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from d_store.models import PossibleBuyer,UserProfile,Comments
from d_payments.models import Invoice,InvoinceProduct
from .forms import CommentsForm,UserProfileForm, PedidosForm,CustomUserCreationForm



def user_register(request):
    return render(request, 'account/signup.html')

def user_login(request):
    return render(request, 'account/login.html')


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "d_account/edit_profile.html", {"form": form})


def custom_signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = "allauth.account.auth_backends.AuthenticationBackend"
            login(request, user)
            return redirect("edit_profile")
    else:
        form = CustomUserCreationForm()
    return render(request, "account/signup.html", {"form": form})


@login_required(login_url="account_login")
def my_account(request):
    buyerlist = get_list_or_404(PossibleBuyer)
    invoices = Invoice.objects.filter(user=request.user)
    current_user = request.user
    user_profile = UserProfile.objects.get(user=current_user)
    product_invoices = InvoinceProduct.objects.filter(user=request.user)

    # Paginación
    paginator = Paginator(buyerlist, 5)
    page = request.GET.get('page')

    try:
        buyerlist_paginated = paginator.page(page)
    except PageNotAnInteger:
        buyerlist_paginated = paginator.page(1)
    except EmptyPage:
        buyerlist_paginated = paginator.page(paginator.num_pages)

    context = {
        'buyerlist_paginated': buyerlist_paginated,
        'invoices': invoices,
        'current_user': current_user,
        'user_profile': user_profile,
        'product_invoices': product_invoices,
    }

    return render(request, 'd_account/my_account.html', context)
  




def create_comment(request, pk):
    # Obtener el objeto PossibleBuyer
    customer = get_object_or_404(PossibleBuyer, id=pk)
    
    if request.method == 'POST':
        form = CommentsForm(request.POST)
        if form.is_valid():
            # Guardar el comentario
            comentario = form.save(commit=False)
            comentario.post = customer  # Asignar el PossibleBuyer al comentario
            comentario.autor = request.user  # Asignar el usuario actual como autor
            comentario.save()  # Guardar el comentario en la base de datos
            
            # Actualizar los campos de PossibleBuyer
            customer.checked = True  # Marcar como revisado
            customer.checked_by = request.user  # Usuario que hizo el comentario
            customer.when_checked = now()  # Fecha y hora actuales
            customer.save()  # Guardar los cambios en PossibleBuyer
            
    else:
        form = CommentsForm()
    
    # Redirigir a la vista handle_buyer
    return redirect("handle_buyer", customer.id)


def update_comment(request, pk):
    comentario = get_object_or_404(Comments, id=pk)

    # Verificar si el usuario actual es el autor del comentario
    if comentario.autor != request.user:
        return HttpResponseForbidden("No tienes permiso para editar este comentario.")  # Respuesta 403

    if request.method == 'POST':
        form = CommentsForm(request.POST, instance=comentario)
        if form.is_valid():
            form.save()
            # Redirigir a la vista handle_buyer con el ID del PossibleBuyer asociado
            return redirect("handle_buyer", comentario.post.id)
    else:
        form = CommentsForm(instance=comentario)

    return render(request, 'd_store/update_comment.html', {'form': form})




#_____________________pedidos__________________________

def create_pedido(request):
    form = PedidosForm()
    context = {'form':form}
    return render(request,'pedidos/create_pedido.html',context)