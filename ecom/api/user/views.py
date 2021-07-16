from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from .models import CustomUser
from django.contrib.auth import get_user_model, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random
import re
# Create your views here.


def generate_session_token(length=10):
    return ''.join(random.SystemRandom().choice([chr(i) for i in range(91, 123)] + [str(i) for i in range(10)]) for _ in range(length))

@csrf_exempt    
def signin(request):
    if not request.method == 'POST':
        return JsonResponse({'error': 'Send a valid POST request'})
    
    username = request.POST['email']
    password = request.POST['password']

    print(username)
    print(password)


# Validation Part
# ([\w\.\-_]+)?\w+@[\w-_]+(\.\w+){1, }
    if not re.match("^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", username):
        return JsonResponse({'error': 'Enter a valid Email'})

    if len(password) < 8:
        return JsonResponse({'error': 'Enter Password of minimum length 8'})

    UserModel = get_user_model()
    
    try :
        user = UserModel.objects.get(email=username)

        if user.check_password(password):
            usr_dict = UserModel.objects.filter(email=username).values().first()
            usr_dict.pop('password')

            if user.session_token != '0':
                user.session_token = '0'
                user.save()
                return JsonResponse({'error': 'Previous Session still exists'})

# If user token is not 0 then user is already logged in
# Logging out the user will make the session token 0

            token = generate_session_token()
            user.session_token = token
            user.save()
            login(request, user)
            return JsonResponse({'token': token, 'user': usr_dict})
        
        else:
            return JsonResponse({'error': 'Invalid Password'})


    except UserModel.DoesNotExist:
        return JsonResponse({'error': 'Invalid Email'})



def signout(request, id):
    logout(request)
    UserModel = get_user_model() 

    try:
        user = UserModel.objects.get(pk=id)
        user.session_token = '0'
        user.save()

    except UserModel.DoesNotExist:
        return JsonResponse({'error': 'Invalid Credentials'})
        
    return JsonResponse({'success': 'Logged Out Successfully'})


class UserViewSet(viewsets.ModelViewSet):
    permission_classes_by_action = {'create': [AllowAny]}

    queryset = CustomUser.objects.all().order_by('id')
    serializer_class = UserSerializer
    
    def get_permissions(self):

        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]
