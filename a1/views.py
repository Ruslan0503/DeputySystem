from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import *
from .serializers import *
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import AuthenticationForm
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
import json
from rest_framework.permissions import AllowAny 
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from rest_framework.generics import ListAPIView
from .forms import CustomUserForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta
from django.utils import timezone
import re
# Create your views here.

#Admin: DeputySystemAdmin
#parol: admin1234

def home(request):
	if not request.user.is_authenticated:
		return redirect('login')
	pr = Profile.objects.filter(user_id = request.user).first()
	if pr:
		has_leader_role = pr.role.filter(role_name__icontains = "Ishchi guruh rahbari").exists()
	else:
		has_leader_role = False
	sessions = OrganizeSession.objects.filter(passed = False)
	passed_sessions = OrganizeSession.objects.filter(passed = True)
	print(has_leader_role)
	context = {
	'pr':pr,
	'has_leader_role':has_leader_role,
	'sessions':sessions,
	'passed_sessions':passed_sessions,
	}
	return render(request, "home.html", context)

def logoutFunction(request):
	logout(request)
	return redirect("login")


class AdjourmentMeeting(LoginRequiredMixin,TemplateView):
	template_name = "adjourment.html"
	
	def dispatch(self, request, **kwargs):
		try:
			org = OrganizeSession.objects.get(id = self.kwargs['id'])
		except:
			return redirect("home")
		if org.owner != self.request.user:
			return redirect("home")
		return super().dispatch(request, **kwargs)

	def get(self, request, *args, **kwargs):
		now = timezone.now()
		org = OrganizeSession.objects.get(id = kwargs['id'])
		# if not org.council_time - now >= timedelta(minutes = 30):
		# 	return redirect("home")
		sessiontopics = SessionTopic.objects.filter(council_id = org)[2::]
		userss = User.objects.filter(is_superuser = False)
		context = {
			"org":org,
			"sessiontopics":sessiontopics,
			"userss":userss
		}
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		title = request.POST.get('title')
		council_time = request.POST.get('council_time')
		sec = request.POST.get('secretary')
		secretary = User.objects.get(username = sec)
		org = OrganizeSession.objects.get(id = kwargs['id'])
		if org.council_time!=council_time:
			org.participants.clear()
		org.title = title
		org.council_time = council_time
		org.secretary = secretary
		org.save()
		#delete session topics
		topics_to_delete = SessionTopic.objects.filter(council_id = org)[2:]
		ids = [t.id for t in topics_to_delete]
		SessionTopic.objects.filter(id__in=ids).delete()
		topic_names = request.POST.getlist('topic_name')
		for i in topic_names:
			SessionTopic.objects.create(
				council_id = org,
				topic_name = i 
			)
		return redirect("home")


class VotingApiView(APIView):
	permission_classes = [IsAuthenticated]

	def get_context_data(self, **kwargs):
		org = OrganizeSession.objects.filter(id = self.kwargs['id']).first()
		serializer = OrganizeSessionSerializer(org, context = {"request":self.request})
		return serializer

	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		return Response(context.data, status = status.HTTP_200_OK)

	def post(self, request, *args, **kwargs):
		topicid = request.POST.get('topicid')
		topic = SessionTopic.objects.get(id = topicid)
		sessionid = self.kwargs['id']
		vote_value = request.POST.get('vote')
		org = OrganizeSession.objects.filter(id = sessionid).first()
		if vote_value == "agree":
			UserSession.objects.create(
				user_id = request.user,
				session_topic = topic,
				vote_value = UserSession.agree
				)

		if vote_value == "disagree":
			UserSession.objects.create(
				user_id = request.user,
				session_topic = topic,
				vote_value = UserSession.disagree
				)

		if vote_value == "neutral":
			UserSession.objects.create(
				user_id = request.user,
				session_topic = topic,
				vote_value = UserSession.neutral
				)

		if vote_value == "finish":
			#some process here
			topic.done = True
			topic.save()
		return JsonResponse({"message":"done"})

def CheckAttendenceTemplate(request):
	if request.user.is_authenticated:
		data = json.loads(request.body)
		userids = data["userids"]
		userids_int = [int(x) for x in userids]
		sessionid = data["sessionid"]
		org = OrganizeSession.objects.get(id = sessionid)
		pr = request.user.userProfile
		if pr.role.filter(role_name__icontains = "checker").exists():
			session = OrganizeSession.objects.get(id = sessionid)
			session.participants.set(User.objects.filter(id__in=userids_int))
			return JsonResponse({"message":"done"})
		else:
			return JsonResponse({"message":"Sizda ruxsat mavjud emas!"})
	return redirect("home")

def AddOkrug(request):
	if request.method == "POST":
		name = request.POST.get('okrugInput')
		
		if len(name)!=0:
			OkrugModel.objects.create(
				okrug_name = name
			)
		return redirect('addsomeonenew')

class VotingTemplateView(LoginRequiredMixin, TemplateView):
	template_name = "voting.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		leader = False
		checker = False
		if self.request.user.is_authenticated:
			try:
				pr = self.request.user.userProfile
				if pr.role.filter(role_name__icontains = "checker").exists():
					checker = True
			except:
				pass
		org = OrganizeSession.objects.filter(id = self.kwargs['id']).first()
		if org.owner == self.request.user:
			leader = True
		if org.secretary == self.request.user:
			context["secretary"] = True
		current_topic = SessionTopic.objects.filter(council_id = org, done = False).first()
		voted_topics = []
		usersessions = []
		participantsnumber = org.participants.count()
		for i in SessionTopic.objects.filter(council_id = org).order_by('done'):
			d = {}
			d["session_topic"] = i
			
			m = {}
			m["session_topic"] = i
			m["remaining"] = participantsnumber - i.agree - i.disagree - i.neutral
			voted_topics.append(m)
			ss = UserSession.objects.filter(session_topic = i, user_id = self.request.user).first()
			if ss:
				d["vote_value"] = ss.vote_value
			else:
				d["vote_value"] = ""
			usersessions.append(d)
		voted = UserSession.objects.filter(session_topic = current_topic, user_id = self.request.user).exists()
		context["checker"] = checker
		context["voted_topics"] = voted_topics
		context["org"] = org
		context["usersessions"] = usersessions
		now = timezone.now()
		context["can_change"] = True #org.council_time - now >= timedelta(minutes = 30) and leader == True
		context["voted"] = voted
		context["session"] = org
		context["current_topic"] = current_topic
		
		if not org.participants.exists():
			context["participants"] = Profile.objects.filter(role__role_name__icontains="deputat")
		context["leader"] = leader
		return context

	def get(self, request, *args, **kwargs):
		org = OrganizeSession.objects.filter(id=self.kwargs['id']).first()
		# if org and org.passed:
		# 	return redirect("home")
		context = self.get_context_data(**kwargs)
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		topicid = request.POST.get('topicid')
		topic = SessionTopic.objects.get(id = topicid)
		sessionid = self.kwargs['id']
		vote_value = request.POST.get('vote')
		org = OrganizeSession.objects.filter(id = sessionid).first()
		if not org.participants.filter(id = request.user.id).exists():
			return redirect("voting", id=sessionid)
		if vote_value == "agree":
			UserSession.objects.create(
				user_id = request.user,
				session_topic = topic,
				vote_value = UserSession.agree
				)

		if vote_value == "disagree":
			UserSession.objects.create(
				user_id = request.user,
				session_topic = topic,
				vote_value = UserSession.disagree
				)

		if vote_value == "neutral":
			UserSession.objects.create(
				user_id = request.user,
				session_topic = topic,
				vote_value = UserSession.neutral
				)

		if vote_value == "finish":
			if topic.topic_name == "Kengashni o'tkazishga rozimisiz?":
				ag = topic.agree if isinstance(topic.agree, (int, float)) else 0
				disag = topic.disagree if isinstance(topic.disagree, (int, float)) else 0
				if disag > ag:
					return redirect("adjourmentmeeting", id=org.id)

			topic.done =True
			topic.save()

			if not SessionTopic.objects.filter(council_id=org, done=False).exists():
				org.passed = True
				org.save()
		

		return redirect("voting", id=sessionid)



#OrganizeSession Api view
class OrganizeSessionApiVie(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, *args, **kwargs):
		users = User.objects.filter(is_superuser = False)
		serializer = InformationuserSerializer(users, many = True, context = {"request":request})
		return Response(serializer.data)

	def post(self, request, *args, **kwargs):
		serializer = OrganizeSessionAndTopicSerializer(data = request.data)
		if serializer.is_valid():
			title = serializer.validated_data['title']
			council_time = serializer.validated_data['council_time']
			sec = serializer.validated_data['secretary']
			secretary = User.objects.filter(username__icontains = sec).first()
			topic_names = serializer.validated_data.get('topic_name')
			org = OrganizeSession.objects.create(
				owner = request.user,
				title = title,
				council_time = council_time,
				secretary = secretary
				)

			SessionTopic.objects.create(
				council_id = org,
				topic_name = "Kengashni o'tkazishga rozimisiz?" 
				)

			for i in topic_names:
				SessionTopic.objects.create(
				council_id = org,
				topic_name = i, 
				)				
			return Response({"message":"Done"}, status = status.HTTP_200_OK)
		return Response({"message":"Yaroqsiz forma!"}, status = status.HTTP_400_BAD_REQUEST)


#Template View
class OrganizeSessions(LoginRequiredMixin,TemplateView):
	template_name = "OrganizeSession.html"
	def get(self, request, *args, **kwargs):
		thecount = OrganizeSession.objects.last()
		if thecount:
			thenum = re.search(r'\d+', thecount.title)
			thenum = int(thenum.group())
			print(thenum)
			if not thenum:
				thenum = 1
			else:
				thenum+=1
		else:
			thenum = 1
		estimated_title = f"Xalq deputatlari Urganch shahar Kengashining {thenum} sessiyasi"
		pr = Profile.objects.filter(user_id = request.user).first()
		if pr and pr.role.filter(role_name__icontains = "ishchi guruh rahbari"):
			checkeruser = Profile.objects.filter(role__role_name__icontains = "checker").values_list("user_id", flat=True)
			userss = User.objects.filter(is_superuser = False).exclude(id__in = checkeruser)
			return render(request, self.template_name, {"userss":userss,"estimated_title":estimated_title})
		else:
			return redirect("home")

	def post(self,request,*args, **kwargs):
		pr = Profile.objects.filter(user_id = request.user).first()
		if pr and pr.role.filter(role_name__icontains = "ishchi guruh rahbari"):
			title = request.POST.get('title')
			council_time = (request.POST.get('council_time'))
			sec = (request.POST.get('secretary'))
			topic_names = (request.POST.getlist('topic_name'))
			secretary = User.objects.filter(username = sec).first()

			org = OrganizeSession.objects.create(
				owner = request.user,
				title = title,
				council_time = council_time,
				secretary = secretary
				)
			SessionTopic.objects.create(
				council_id = org,
				topic_name = "Kengashni o'tkazishga rozimisiz?"
				)
			
			for i in topic_names:
				if len(i)!=0:
					SessionTopic.objects.create(
						council_id = org,
						topic_name = i,
						)
			return redirect("home")
		else:
			return redirect("home")
		
#changing user's passwords => done..
class ManageUsers(TemplateView, ListAPIView):
	template_name = "manageusers.html"

	def get_permissions(self):
		print("get_permission()")
		if self.request.content_type == "application/json":
			return [IsAuthenticated()]
		return []

	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_superuser:
			if request.content_type == "application/json":
				print("api")
				return JsonResponse({"message":"Sizda ruxsat mavjud emas!"}, status = 403)
			else:
				return redirect("home")
		return super().dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		if request.content_type == "application/json":
			profiles = Profile.objects.all()
			serializer = UserDetailSerializer(profiles, many = True ,context = {'request':request})
			return Response(serializer.data)
		else:
			profiles = Profile.objects.all()
			context = {
				"profiles":profiles,
			}
			return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		if request.content_type == "application/json":
			print("api")
			serializer = PasswordChangeSerializer(data = request.data)
			if serializer.is_valid():
				userid = serializer.validated_data['userid']
				newpassword = serializer.validated_data['password']
				passwordconfirm = serializer.validated_data['confirmation_password']
				try:
					user = User.objects.get(id = userid)
					user.set_password(newpassword)
					user.save()
					return JsonResponse({"message":"Bajarildi"})
				except User.DoesNotExist:
					return JsonResponse({"message":"Foydalanuvchi topilmadi"})
			return JsonResponse({"message":serializer.errors})
		else:
			data = json.loads(request.body)
			userid = data.get('userid')
			newpassword = data.get('password')
			
			try:
				user = User.objects.get(id = userid)
				user.set_password(newpassword)
				user.save()
				return JsonResponse({"message":"Bajarildi"})
			except User.DoesNotExist:
				return JsonResponse({"message":"Foydalanuvchi topilmadi"})


#Registering a user as a Admin => in progress
class AddSomeoneNew(TemplateView,APIView):
	template_name = "addsomeonenew.html"
	form = CustomUserForm()
	context = {'form':form}

	def get_permissions(self):
		print("get_permission()")
		if self.request.content_type == "application/json":
			return [IsAuthenticated()]
		return []

	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_superuser:
			if request.content_type == ('application/json'):
				print("api")
				return JsonResponse({"message": "Sizda ruxsat mavjud emas!"}, status=403)
			else:
				return redirect("home")
				
		return super().dispatch(request, *args, **kwargs)

	def get(self, request, *args, **kwargs):
		if request.content_type == "application/json":
			okrugsm = OkrugModel.objects.all()
			okrugs = OkrugSerializer(okrugsm, many=True)
			return Response(okrugs.data)
		form = CustomUserForm()
		context = {'form':form}
		return render(request, self.template_name, self.context)


	def protcess(self,name,surname,username,password,phone_number,profilePhoto,okrugName,roles):
		print(username,password)
		user = User.objects.create_user(
					first_name = name,
					last_name = surname,
					username = username,
					password = password,
					)
		print(okrugName)
		pr, cr_pr = Profile.objects.get_or_create(user_id = user)
		okrugID = OkrugModel.objects.get(okrug_name__icontains = okrugName)
		if okrugID:
			pr.okrugId = okrugID
		if profilePhoto:
			pr.profile_photo = profilePhoto
		pr.phone_number = phone_number
		for r in roles:
			print(r)
			role = Role.objects.filter(role_name__icontains = r).first()
			pr.role.add(role)
		pr.save()
		return True

	def post(self, request, *args, **kwargs):
		if request.content_type == 'application/json':
			serializer = CustomUserSerializer(data = request.data)
			if serializer.is_valid():
				name = serializer.validated_data["name"]
				surname = serializer.validated_data["surname"]
				username = serializer.validated_data["username"]
				password = serializer.validated_data["password"]
				phone_number = serializer.validated_data["phone_number"]
				profilePhoto = serializer.validated_data.get("profilePhoto", None)
				okrugName = serializer.validated_data["okrugid"]
				roles = serializer.validated_data["roles"]
				tr = self.protcess(name,surname,username,password,phone_number,profilePhoto,okrugName,roles)
				if tr:
					return Response(serializer.data, status = status.HTTP_201_CREATED)
				else:
					return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)		
			return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
		else:
			print('web request')
			form = CustomUserForm(request.POST, request.FILES)
			if form.is_valid():
				name = form.cleaned_data["name"]
				surname = form.cleaned_data["surname"]
				username = form.cleaned_data["username"]
				password = form.cleaned_data["password"]
				phone_number = form.cleaned_data["phone_number"]
				profilePhoto = form.cleaned_data["profilePhoto"]
				okrugName = form.cleaned_data["okrugId"]
				roles = form.cleaned_data["roles"]
				self.protcess(name,surname,username,password,phone_number,profilePhoto,okrugName,roles)
				return redirect("addsomeonenew")
			else:
				for field, errors in form.errors.items():
				    for error in errors:
        				messages.error(request, f"{field}: {error}")
        				print(f"{field}: {error}")

				return render(request, self.template_name)
			return redirect('home')

#refreshing token => done..
class RefreshTokenFunction(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		refresh_token = request.data.get('refresh')

		if not refresh_token:
			return Response({'error':'Refresh token is required'}, status = status.HTTP_400_BAD_REQUEST)

		try:
			refresh = RefreshToken(refresh_token)
			access_token = str(refresh.access_token)
			return Response(
				{
					"access":access_token
				}, status = status.HTTP_200_OK
				)
		except InvalidToken:
			return Response({"error":"Invalid Refresh token"}, status = status.HTTP_400_BAD_REQUEST)

#Login Function for API => done..
class LoginView(TemplateView,APIView):
	template_name = "login.html"
	permission_classes = [AllowAny]
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name)
	def post(self, request, *args, **kwargs):
		if request.content_type == ("application/json"):
			print("api")
			serializers = LoginFieldSerializer(data = request.data)
			if serializers.is_valid():
				user = serializers.validated_data['user']
				login(request,user)
				
				refresh = RefreshToken.for_user(user)
				return Response(
					{
						'refresh':str(refresh),
						'access':str(refresh.access_token)
					},
					status = status.HTTP_200_OK
					)
					
			return Response(serializers.errors, status =  status.HTTP_400_BAD_REQUEST)
		else:
			print("web")
			username = request.POST['username']
			password = request.POST['password']
			print(username,password)
			user = authenticate(request,username = username, password = password)
			if user is not None:
				login(request,user)
				return redirect("home")
			return redirect("login")
