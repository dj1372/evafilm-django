from django.views.decorators.http import require_GET
from django.http import HttpResponse
from movies.models import Category
from robots_txt.models import Robots


@require_GET
def robots(request):
    edit_list = ["User-agent: *"]

    select_type = [select_type_val.get('select_type') for select_type_val in
                   [select_type for select_type in Robots.objects.all().values("select_type")]]

    value = [value_val.get('value') for value_val in
             [value for value in Robots.objects.all().values("value")]]

    category_obj = [name_cat.get("name_en") for name_cat in
                    [cat for cat in Category.objects.all().values("name_en")]]

    obj_list_dynamic = list(zip(select_type, value))
    print(obj_list_dynamic)
    for i in obj_list_dynamic:
        edit_list.append(i[0] + " :    /" + i[1] + "/")

    for i in category_obj:
        edit_list.append("Allow:    /tag/" + i + "/")
    edit_list.append("Sitemap:    https://evafilm.stream/sitemap.xml")
    show_list = ""
    for i in edit_list:
        show_list += f"{i}\n"
    return HttpResponse(show_list, content_type="text/plain")
