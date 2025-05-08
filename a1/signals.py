from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Role,SessionTopic,UserSession,OrganizeSession,UserSession

@receiver(post_save, sender = OrganizeSession)
def deletevotes(sender, instance, created, **kwargs):
	if created:
		return

	session_passes = SessionTopic.objects.filter(council_id = instance, topic_name__icontains = "Kengashni o'tkazishga rozimisiz?").first()
	if session_passes and session_passes.done:
		secretary_topic = SessionTopic.objects.filter(council_id = instance, topic_name__icontains = "Kotibni saylashga rozimisiz?").first()
		secretary_topic.agree = 0
		secretary_topic.disagree = 0
		secretary_topic.neutral = 0
		secretary_topic.save()
		UserSession.objects.filter(session_topic = secretary_topic).delete()
	else:
		UserSession.objects.filter(session_topic = session_passes).delete()
		session_passes.agree = 0
		session_passes.disagree = 0
		session_passes.neutral = 0
		session_passes.save()



@receiver(post_save, sender = User)
def createProfileSignal(sender, instance, created, **kwargs):
	if created:
		deputat_role, created_role = Role.objects.get_or_create(role_name = "Deputat")
		p = Profile.objects.create(
			user_id = instance
			)
		p.role.add(deputat_role)



@receiver(post_save, sender = UserSession)
def AddValue(sender, instance, created, **kwargs):
	if created:
		topic = instance.session_topic
		if instance.vote_value == UserSession.agree:
			topic.agree = (topic.agree or 0) + 1
		elif instance.vote_value == UserSession.disagree:
			topic.disagree = (topic.disagree or 0) +1
		elif instance.vote_value == UserSession.neutral:
			topic.neutral = (topic.neutral or 0) +1
		topic.save()

