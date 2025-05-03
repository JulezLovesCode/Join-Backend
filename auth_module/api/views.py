import uuid
from rest_framework import generics
from .serializers import UserProfileSerializer, RegistrationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate  
from auth_module.models import ExtendedUserInformation as UserProfile  
User = get_user_model()  
class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=400)

        user = authenticate(request, username=user.email, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "username": user.username, "email": user.email}, status=200)
        else:
            return Response({"error": "Invalid credentials"}, status=400)
class RegistrationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            UserProfile.objects.create(user=saved_account)
            return Response({
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
class GuestLoginView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        guest_id = str(uuid.uuid4()) 
        return Response({"guest_id": guest_id}, status=200)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()  
        return Response({'message': 'Logged out successfully'})
