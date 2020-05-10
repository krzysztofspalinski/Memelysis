from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseNotFound
from datetime import datetime, timezone
from index.models import Memes, Sources
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import IntegrityError


@csrf_exempt
def memes(request):
    if request.method == "POST":
        data = request.POST
        data_password = data.get('password', '')
        if str(data_password) == "82034723402347":
            try:
                meme_id_posted = data['id']
                url_posted = data['url']
                image_path_posted = data['image_path']
                source_posted = data['source']
                meme_timestamp_posted = data['meme_timestamp']
            except KeyError as e:
                return JsonResponse({'error': str(e)})
            else:
                meme_id = str(meme_id_posted)
                url = str(url_posted)
                image_path = str(image_path_posted)
                source, _ = Sources.objects.get_or_create(name=source_posted)
                print(meme_timestamp_posted)
                meme_datetime = datetime.fromtimestamp(
                    int(meme_timestamp_posted), tz=timezone.utc)
                try:
                    meme = Memes.objects.create(
                        meme_id=meme_id,
                        url=url,
                        image_path=image_path,
                        source=source,
                        meme_datetime=meme_datetime
                    )
                    return JsonResponse(serializers.serialize('json', [meme]), safe=False)
                except IntegrityError as e:
                    return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'error': 'Wrong password.'})
    else:
        return JsonResponse({'error': f"This request method is not supported: {request.method}"})
