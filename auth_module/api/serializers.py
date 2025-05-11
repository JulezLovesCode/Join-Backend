from rest_framework import serializers
from auth_module.models import ExtendedUserInformation as UserProfile, EmailBasedAuthenticationUser as CustomUser  
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    class Meta:
        model = UserProfile
        fields = ["user", "username", "email", "bio", "location"]
class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser  
        fields = ['username', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if 'password' not in data or 'repeated_password' not in data:
            raise serializers.ValidationError({'password': 'Password fields are required.'})

        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})

        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already exists'})
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')  
  
        user = CustomUser(username=validated_data['username'], email=validated_data['email'])
        user.set_password(validated_data['password'])  
        user.save()

        return user