from rest_framework import serializers
from .models import SessionTopic,UserSession,Profile,Role,OkrugModel,OrganizeSession
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name']


class SessionTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionTopic
        fields = ['id', 'topic_name', 'agree', 'disagree', 'neutral', 'done']


class OrganizeSessionSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    secretary = UserSerializer()
    participants = UserSerializer(many=True)
    current_topic = serializers.SerializerMethodField()
    voted = serializers.SerializerMethodField()
    leader = serializers.SerializerMethodField()

    class Meta:
        model = OrganizeSession
        fields = [
            'id', 'title', 'council_time', 'owner', 'secretary',
            'participants', 'passed', 'created_at', 'updated_at',
            'current_topic', 'voted', 'leader'
        ]

    def get_current_topic(self, obj):
        topic = SessionTopic.objects.filter(council_id=obj, done=False).first()
        return SessionTopicSerializer(topic).data if topic else None

    def get_voted(self, obj):
        user = self.context['request'].user
        current_topic = SessionTopic.objects.filter(council_id=obj, done=False).first()
        if current_topic:
            return UserSession.objects.filter(session_topic=current_topic, user_id=user).exists()
        return False

    def get_leader(self, obj):
        user = self.context['request'].user
        pr = Profile.objects.filter(user_id=user).first()
        return pr and pr.role.filter(role_name__icontains="ishchi guruh rahbari").exists()



class OrganizeSessionAndTopicSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length = 500)
    secretary = serializers.CharField(max_length = 100)
    topic_name = serializers.ListField(
        child=serializers.CharField(), 
    )
    class Meta:
        model = OrganizeSession
        fields = ['title','council_time', 'secretary','topic_name']

#to send usernames
class InformationuserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


# to change users' passwords
class PasswordChangeSerializer(serializers.Serializer):
    userid = serializers.IntegerField()
    password = serializers.CharField(write_only=True)
    confirmation_password = serializers.CharField(write_only=True)

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.get("confirmation_password")

        # Check if password and confirm_password match
        if password != confirm_password:
            raise serializers.ValidationError("Parollar mos emas")
        
        # Optionally, validate password strength using Django's password validators
        
        return data


#from base to json to send back
class UserDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source = 'user_id.first_name')
    surname = serializers.CharField(source = 'user_id.last_name')
    username = serializers.CharField(source = 'user_id.username')
    profile_photo = serializers.ImageField(use_url=True)
    #roles = serializers.StringRelatedField(many = True)
    class Meta:
        model = Profile
        fields = ['name','surname','username','phone_number','profile_photo','role','okrugId']

# from base to json
class OkrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = OkrugModel
        fields = '__all__'

#from json to base
class CustomUserSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, label='Ism')
    surname = serializers.CharField(max_length=100, label='Familya')
    username = serializers.CharField(max_length=150, label="Foydalanuvchi nomi")
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, label="Parol")
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'}, label="Parolni tasdiqlash")
    phone_number = serializers.CharField(max_length=15, required=False, label="Telefon no'mer")
    profilePhoto = serializers.ImageField(required=False, label="Foydalanuvchi Rasmi")
    okrugid = serializers.CharField(max_length = 100, required = True)
    roles = serializers.ListField(
        child=serializers.CharField(), 
        label="Roli"
    )
    def validate(self, data):
        # Retrieve passwords from validated data
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        # Check if password and confirm_password match
        if password != confirm_password:
            raise serializers.ValidationError("Parollar mos emas")
        
        # Optionally, validate password strength using Django's password validators
        
        return data

#from json to base
class LoginFieldSerializer(serializers.Serializer):
	username = serializers.CharField(max_length = 100)
	password = serializers.CharField(max_length = 100, write_only = True)

	def validate(self, data):
		username = data.get('username')
		password = data.get('password')
		print(username, password)
		user = authenticate(username = username, password = password)
		
		if user is None:
			raise serializers.ValidationError("Invalid credentials")
		
		data['user'] = user
		return data
