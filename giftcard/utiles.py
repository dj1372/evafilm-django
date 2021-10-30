from datetime import timedelta
from django.utils import timezone

from giftcard.models import GiftCard_Related_to_User
from movies.models import Category


def change_status_False(gift_):
    access_bool = False
    gift_.status = False
    gift_.save()
    return access_bool


def get_access(episode, request):
    all_cats_this_episode: Category = [cat_name.get("name_en") for cat_name in
                                       [l for l in episode.playlist.category.all().values("name_en")]]
    # print(GiftCard_Related_to_User.objects.get_object_or_None_for_check_cat(user=request.user, status=True))
    access_bool = False
    try:
        global gift_
        gift_ = GiftCard_Related_to_User.objects.get_object_or_None_for_check_cat(
            user=request.user, status=True)
        check_cate_status = gift_.gift_code.category.all().values("name_en")
        cat_name_all_this_gift_card = [name.get("name_en") for name in check_cate_status]
        date_enabeld = timezone.localtime(gift_.date_enabeld)
        valid_to = timezone.localtime(gift_.gift_code.valid_to)
        valid_from = timezone.localtime(gift_.gift_code.valid_from)
        valid_day = gift_.gift_code.valid_day
        valid_time_gift_card = date_enabeld + timedelta(days=valid_day)  # compare with now
        now = time = timezone.localtime(timezone.now())  # compare with valid_time_gift_card
        if gift_.gift_code.valid_to < now:
            # gift_.gift_code._state = False
            gift_.gift_code.save()
            raise ("HaHaHaHaHa")

        continue_loop = True
        for i in all_cats_this_episode:
            if continue_loop == True:
                for j in cat_name_all_this_gift_card:
                    if i == j:
                        access_bool = True
                        continue_loop = False
            else:
                break

        if valid_to - timedelta(days=valid_day) < now:
            new_valid_date = (valid_to - date_enabeld).days
            valid_time_gift_card = date_enabeld + timedelta(days=new_valid_date)  # compare with now
            if (valid_time_gift_card < now):
                access_bool = change_status_False(gift_)
            if (date_enabeld > valid_to):
                access_bool = change_status_False(gift_)
            if (valid_time_gift_card > valid_to):
                access_bool = change_status_False(gift_)
        else:
            if (valid_time_gift_card < now):
                access_bool = change_status_False(gift_)
            if (date_enabeld > valid_to):
                access_bool = change_status_False(gift_)
            if (valid_time_gift_card > valid_to):
                access_bool = change_status_False(gift_)
    except:
        access_bool = False

    return access_bool
