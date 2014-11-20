# coding: utf-8
from redis import StrictRedis
import simplejson as json

redis = StrictRedis(host='10.0.2.2', port=6379, db=0)

def send_to_redis(obj):
    oid = obj['oid']
    redis.rpush('mootiro:migrations', oid)
    redis.set('mootiro:{}'.format(oid), json.dumps(obj))

def migrate_all():
    migrate_organizations()

def migrate_organizations():
    from organization.models import Organization

    for org in Organization.objects.all():
        obj = parse_organization(org)
        send_to_redis(obj)

def parse_organization(org):
    return {
        'oid': 'o{}'.format(org.id),
        'mootiro_type': 'organization',
        'name': org.name,
        'description': org.description,
        "created_at": str(org.creation_date),
        "updated_at": str(org.last_update),
        "contacts": org.contacts,
        "aditional_info": {
            'target_audiences':  [ta.name for ta in org.target_audiences.all() if ta],
            'short_description': org.short_description,
            'creator': org.creator.name if org.creator else None,
        },
        'tags': [tag.name for tag in org.tags.all() if tag] + [c.get_translated_name() for c in org.categories.all() if c],
        'geometry': org.geometry.wkt,
        # logo ? logo_category ? logo_choice ?
    }

