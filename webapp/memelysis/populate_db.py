import json
from index.models import *
import requests
from datetime import datetime, timezone

response = requests.get('https://storage.googleapis.com/images-and-logs/tmp-data-for-website/all_data.json?hl=pl')
meme_dicts = []
for x in response.text.split('\n'):
    try:
        meme_dict = json.loads(x)
    except json.decoder.JSONDecodeError:
        pass
    if type(meme_dict) == dict:
        try:
            datetime.fromtimestamp(int(float(meme_dict['timestamp'])))
            meme_dicts.append(meme_dict)
        except ValueError:
            pass


source_names = {meme_dict['source'] for meme_dict in meme_dicts}
Sources.objects.bulk_create([
    Sources(name=source_name) for source_name in source_names
], ignore_conflicts=True)


sources = list(Sources.objects.all().values())
meme_dicts_to_populate = [{'meme_id': meme_dict['id'],'url': meme_dict['url'],'image_path': meme_dict['image_path'],'source_id':next(source for source in sources if source['name'] == meme_dict['source'])['id'],'meme_datetime': datetime.fromtimestamp(int(float(meme_dict['timestamp'])), tz=timezone.utc)} for meme_dict in meme_dicts]

memes_existing = set(Memes.objects.all().values_list('meme_id', flat=True))
memes_dicts_to_create = []
memes_dicts_to_update = []
for i, meme_dict in enumerate(meme_dicts_to_populate):
    if meme_dict['meme_id'] not in memes_existing:
        memes_dicts_to_create.append(meme_dict)
    else:
        memes_dicts_to_update.append(meme_dict)

Memes.objects.bulk_create([Memes(**meme_dict) for meme_dict in memes_dicts_to_create], ignore_conflicts=True)

memes_mapping = dict(Memes.objects.all().values_list('id', 'meme_id'))
memes_reverse_mapping = {v:k for k,v in memes_mapping.items()}

muss_dicts_to_populate = [{'meme_id': meme_dict['id'],'upvotes':meme_dict['upvotes'],'upvotes_centile':meme_dict['upvotes_centile']} for meme_dict in meme_dicts]
muss_existing = set(MemesUpvotesStatistics.objects.all().values_list('meme_id', flat=True))
muss_dicts_to_create = []
muss_dicts_to_update = []
for i, muss_dict in enumerate(muss_dicts_to_populate):
    muss_dict['meme_id'] = memes_reverse_mapping[muss_dict['meme_id']]
    if muss_dict['meme_id'] not in muss_existing:
        muss_dicts_to_create.append(muss_dict)
    else:
        muss_dicts_to_update.append(muss_dict)


MemesUpvotesStatistics.objects.bulk_create([MemesUpvotesStatistics(**muss_dict) for muss_dict in muss_dicts_to_create], ignore_conflicts=True)



mcs_dicts_to_populate = [{'meme_id': meme_dict['id'],'cluster':meme_dict['cluster']} for meme_dict in meme_dicts]
mcs_existing = set(MemesClusters.objects.all().values_list('meme_id', flat=True))
mcs_dicts_to_create = []
mcs_dicts_to_update = []
for i, mcs_dict in enumerate(mcs_dicts_to_populate):
    mcs_dict['meme_id'] = memes_reverse_mapping[mcs_dict['meme_id']]
    if mcs_dict['meme_id'] not in mcs_existing:
        mcs_dicts_to_create.append(mcs_dict)
    else:
        mcs_dicts_to_update.append(mcs_dict)


MemesClusters.objects.bulk_create([MemesClusters(**mcs_dict) for mcs_dict in mcs_dicts_to_create], ignore_conflicts=True)






