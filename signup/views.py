from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def register_view(request):
    if request.user.is_authenticated:
        return redirect('article-list')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"¡Bienvenido, {user.username}! Tu cuenta ha sido creada con éxito. Ya puedes iniciar sesión.")
            return redirect('login')
        else:
            messages.error(request, "Hubo un error en el registro. Por favor, verifica los datos.")
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})
