from django.shortcuts import render
from django.shortcuts import render

from .models import invitor_code, generated_invitor_code


def invitation_code_insert_view(request):
    invitation_code = request.GET.get('code')
    context = {}
    if invitation_code:
        invitor_instance = invitor_code.objects.filter(code=str(invitation_code))
        g_invitor = generated_invitor_code.objects.filter(code=str(invitation_code))
        if invitor_instance.exists() and request.user.is_authenticated:
            invitor_instance = invitor_instance.first()
            if not invitor_instance.invited_users.filter(username=request.user.username).exists():
                invitor_instance.invitations+=1
                invitor_instance.invited_users.add(request.user)
                invitor_instance.save()
                context.update({'status':200})
        elif g_invitor.exists() and request.user.is_authenticated:
            g_invitor = g_invitor.first()
            if not g_invitor.invited_users.filter(username=request.user.username).exists():
                g_invitor.invitations+=1
                g_invitor.invited_users.add(request.user)
                g_invitor.save()
                context.update({'status':200})
        else:
            context.update({'status':401})
    else:
        context.update({'status': 401})

    return render(request, 'invitation_code.html', context=context)
