import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie

# 1. Page principale (Kat3ti l'CSRF Cookie l React)
@ensure_csrf_cookie
def chat_index(request):
    return render(request, 'chat/index.html')

# 2. Register (Création de compte)
def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Le nom d\'utilisateur et le mot de passe sont obligatoires.'}, status=400)
            
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Ce nom d\'utilisateur est déjà pris.'}, status=400)
            
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return JsonResponse({'success': True, 'username': user.username})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

# 3. Login (Connexion)
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'username': user.username})
        else:
            return JsonResponse({'error': 'Nom d\'utilisateur ou mot de passe incorrect.'}, status=400)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

# 4. Logout (Déconnexion)
def logout_view(request):
    logout(request)
    return JsonResponse({'success': True})

# 5. API pour vérifier si l'utilisateur est connecté
def current_user_view(request):
    if request.user.is_authenticated:
        return JsonResponse({'username': request.user.username})
    return JsonResponse({'username': None})

# 6. API pour lister les utilisateurs
def users_list_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non autorisé'}, status=401)
    users = User.objects.exclude(id=request.user.id).values_list('username', flat=True)
    return JsonResponse({'users': list(users)})