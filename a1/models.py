from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Role(models.Model):
	role_name = models.CharField(max_length = 50)

	def __str__(self):
		return self.role_name

class OkrugModel(models.Model):
	okrug_name = models.CharField(max_length = 50)

	def __str__(self):
		return self.okrug_name

class Profile(models.Model):
	user_id = models.OneToOneField(User, related_name="userProfile" , on_delete = models.SET_NULL, null=True,blank=True)
	phone_number = models.CharField(max_length = 25, null = True, blank = True)
	okrugId = models.ForeignKey(OkrugModel, on_delete = models.SET_NULL, null=True)
	profile_photo = models.ImageField(upload_to = 'profile_imgs/', null=True, blank=True, default = "profile_imgs/default.jpg")
	role = models.ManyToManyField(Role, related_name = "RoleOfUser" , blank=True)
	is_active = models.BooleanField(default = True) 

	def has_role(self, role_name):
		return self.role.filter(role_name = role_name).exists()

	def getUrlOfPhoto(self):
		try:
			return self.profile_photo.url
		except:
			return "profile_imgs/default.jpg"

class OrganizeSession(models.Model):
	owner = models.ForeignKey(User, related_name = "ownerSession",on_delete = models.SET_NULL, null=True, blank=True)
	title = models.CharField(max_length = 500)
	council_time = models.DateTimeField(null = True, blank = True)
	participants = models.ManyToManyField(User, related_name = "participantsOfCouncil")
	secretary = models.ForeignKey(User, on_delete = models.SET_NULL, null=True, blank=True)
	passed = models.BooleanField(default = False)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

	def __str__(self):
		return self.title

class SessionTopic(models.Model):
	council_id = models.ForeignKey(OrganizeSession, on_delete = models.CASCADE)
	topic_name = models.TextField()
	agree = models.IntegerField(null = True, blank = True, default = 0)
	disagree = models.IntegerField(null = True, blank = True, default = 0)
	neutral = models.IntegerField(null = True, blank = True, default = 0)
	done = models.BooleanField(default = False)

	def __str__(self):
		return self.topic_name

class UserSession(models.Model):
	user_id = models.ForeignKey(User, on_delete = models.SET_NULL, null = True, blank = True)
	session_topic = models.ForeignKey(SessionTopic, on_delete = models.CASCADE)
	agree = 'Agree'
	disagree = 'Disagree'
	neutral = 'Neutral'
	CHOICES = [
		(agree, 'agree'),
		(disagree, 'disagree'),
		(neutral, 'neutral'),
	]
	vote_value = models.CharField(max_length = 100, choices = CHOICES)

"""
~ Inserting data
	UserSession.objects.create(user_id = request.id, vote_value = UserSession.agree{or disagree, neutral})

	agreeSessions = UserSession.objects.filter(vote_value = UserSession.agree)
"""
