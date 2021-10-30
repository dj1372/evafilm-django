from django.contrib import admin

from django.utils.html import mark_safe

from .models import invitor_code, generated_invitor_code
# Register your models here.



@admin.register(invitor_code)
class invitor_admin(admin.ModelAdmin):
    list_display = ("__str__", "invite_count", "my_code_invitations")
    #invited users username inline widget
    def my_code_invitations(self, obj):
        if obj.invited_users.exists():
            invited = [str(x.username) for x in obj.invited_users.iterator()]
            string = ", ".join(invited)

            results = []
            for i in invited:
                results.append(f'<li>{i}</li>')
            html_result = " ".join(results)
            html_content = f"""
                <div style="height:60px; overflow:hidden; overflow-y:scroll">
                    <ul>
                        {html_result}
                    </u>
                </div>
            """
            return mark_safe(html_content)
        else:
            return "no body"

    my_code_invitations.short_description = "دعوت شدگان"
    #cout of invited users inline widget
    def invite_count(self, obj):
        return obj.invitations
    invite_count.short_description = "تعداد دعوت ها"


@admin.register(generated_invitor_code)
class generated_invitor_code_admin(admin.ModelAdmin):
    list_display = ("__str__", "invite_count", "my_code_invitations")
    fields = ("code", )
    def my_code_invitations(self, obj):
        if obj.invited_users.exists():
            invited = [str(x.username) for x in obj.invited_users.iterator()]
            string = ", ".join(invited)

            results = []
            for i in invited:
                results.append(f'<li>{i}</li>')
            html_result = " ".join(results)
            html_content = f"""
                <div style="height:60px; overflow:hidden; overflow-y:scroll">
                    <ul>
                        {html_result}
                    </u>
                </div>
            """
            return mark_safe(html_content)
        else:
            return "no body"

    my_code_invitations.short_description = "دعوت شدگان"

    def invite_count(self, obj):
        return obj.invitations

    invite_count.short_description = "تعداد دعوت ها"