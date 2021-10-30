from django.contrib import admin
from send_message.models import Send_Message

from extensions.utils import Email, my_send_sms

class Send_Message_Manager(admin.ModelAdmin):
	list_display = ('title', "jpublish", "select", "status", "active")
	list_editable = (["status"])

	fieldsets = (
        (None, {'fields': ('title', 'users')}),
        (None, {'fields': ('select', 'message',)}),
        # (None, {'fields': ('active', 'status',)}),
    )	

	def save_model(self, request, obj, form, change):	
	    status = obj.status
	    active = obj.active
	    if status == "p" and active:
	    	title = obj.title
	    	message = obj.message
	    	all_user = [user_email for user_email in [i.email for i in obj.get_all_user()] if user_email != ""]
	    	#///////////////////////////////////////////////////			
	    	if obj.select == "e":
	    		try:
	    			Email.send_mail(title, all_user, "emails/send_mail.html", {"t":title,"d":message})
	    			obj.active = False
	    		except:
	    			pass
	    			
	    	#///////////////////////////////////////////////////			
	    	if obj.select == "p":
	    		Phone_Number_List = [user_phone for user_phone in [i.username for i in obj.get_all_user()] if user_phone != ""]
	    		for x in Phone_Number_List:
	    			is_sended = my_send_sms(message=f"{title}\n{message}", phone=str(x))
		    		if is_sended:
		    			obj.active = False
		    		else:
		    			obj.status = "d"
	    	#///////////////////////////////////////////////////			
	    	if obj.select == "b":
	    		try:
	    			Email.send_mail(title, all_user, "emails/send_mail.html", {"t":title,"d":message})
	    			obj.active = False
	    		except:
	    			pass

	    		#send sms
    			Phone_Number_List = [user_phone for user_phone in [i.username for i in obj.get_all_user()] if user_phone != ""]

	    		for x in Phone_Number_List:
	    			is_sended = my_send_sms(message=f"{title}\n{message}", phone=str(x))
		    		if is_sended:
		    			obj.active = False
		    		else:
		    			obj.status = "d"

	    super().save_model(request, obj, form, change)

admin.site.register(Send_Message, Send_Message_Manager)