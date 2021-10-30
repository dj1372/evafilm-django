from django.http.response import HttpResponse
from django.shortcuts import render
from .models import Episode_Last_State
from accounts.models import UserProfile
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.http import require_http_methods

# Create your views here.

User = get_user_model()


@require_http_methods(["POST"])
@requires_csrf_token
def get_last_position(request):
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        user_token_lastposition = request.POST.get("_token")
        user = UserProfile.objects.filter(api_token=user_token_lastposition).first().user
        video = Episode_Last_State.objects.filter(post_id=post_id, user=user).first()
        if video:
            return JsonResponse({'post_id': video.post_id, "last_position": video.last_position})
        else:
            return HttpResponse("post_id not found")


@require_http_methods(["POST"])
@requires_csrf_token
def set_last_position(request):
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        last_position = request.POST.get("last_position")
        position_user_token = request.POST.get("_token")
        position_user = UserProfile.objects.filter(api_token=position_user_token).first().user

        try:
            video = Episode_Last_State.objects.filter(post_id=post_id, user=request.user).first()
            # print("username:", video.user.username)
            # print("token:", position_user_token)
            # print("id_post:", video.post_id)
            # print("update")
            video.last_position = last_position
            video.save()
            # return JsonResponse(
            #     {"token": position_user_token, "user": position_user.username,
            #      "message": "saved"})
        except:
            # print("post_id:", post_id)
            # print("create")
            video = Episode_Last_State(post_id=post_id, last_position=last_position, user=position_user)
            video.save()
            # return JsonResponse({"token": position_user_token,
            #                      "user": position_user.username, "message": "create"})
    return HttpResponse("done")
