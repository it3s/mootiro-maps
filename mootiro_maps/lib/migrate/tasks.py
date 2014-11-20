# coding: utf-8
from redis import StrictRedis
import simplejson as json

redis = StrictRedis(host='10.0.2.2', port=6379, db=0)

def send_to_redis(obj):
    oid = obj['oid']
    redis.rpush('mootiro:migrations', oid)
    redis.set('mootiro:{}'.format(oid), json.dumps(obj))

OID_MAPPER = {
    "Organization": 'org',
    "Community":    'com',
    "Resource":     'res',
    "Need":         'ned',
    "User":         'usr',
    "Discussion":   'dis',
    "Comment":      'cmt',
    "Proposal":     'pps',
    "Project":      'pro',
    "Relation":     'rel',
}
def build_oid(obj):
    return "{}_{}".format(OID_MAPPER[obj.__class__.__name__], obj.id)


def migrate_all():
    migrate_users()
    migrate_organizations()
    migrate_communities()
    migrate_resources()
    migrate_needs()
    migrate_comments()
    migrate_discussions()
    migrate_relations()
    migrate_projects()

def migrate_organizations():
    print "Migrating Organizations"
    from organization.models import Organization

    for obj in Organization.objects.all():
        parsed = parse_organization(obj)
        send_to_redis(parsed)

def parse_organization(obj):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'organization',
        'name': obj.name,
        'description': obj.description,
        "created_at": str(obj.creation_date),
        "updated_at": str(obj.last_update),
        "contacts": obj.contacts,
        "aditional_info": {
            'target_audiences':  [ta.name for ta in obj.target_audiences.all() if ta],
            'short_description': obj.short_description,
            'creator': obj.creator.name if obj.creator else None,
        },
        'tags': [tag.name for tag in obj.tags.all() if tag] + [c.get_translated_name() for c in obj.categories.all() if c],
        'geometry': obj.geometry.wkt,
        # logo ? logo_category ? logo_choice ?
    }

def migrate_communities():
    print "Migrating Communities"
    from community.models import Community

    for com in Community.objects.all():
        obj = parse_community(com)
        send_to_redis(obj)

def parse_community(obj):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'community',
        'name': obj.name,
        'description': obj.description,
        "created_at": str(obj.creation_date),
        "updated_at": str(obj.last_update),
        "contacts": obj.contacts,
        "aditional_info": {
            "population": obj.population,
            'short_description': obj.short_description,
            'creator': obj.creator.name if obj.creator else None,
        },
        'tags': [tag.name for tag in obj.tags.all() if tag],
        'geometry': obj.geometry.wkt,
    }

def migrate_resources():
    print "Migrating Resources"
    from komoo_resource.models import Resource

    for obj in Resource.objects.all():
        parsed = parse_resource(obj)
        send_to_redis(parsed)

def parse_resource(obj):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'resource',
        'name': obj.name,
        'description': obj.description,
        "created_at": str(obj.creation_date),
        "updated_at": str(obj.last_update),
        "contacts": obj.contacts,
        "aditional_info": {
            'short_description': obj.short_description,
            'creator': obj.creator.name if obj.creator else None,
        },
        'tags': [tag.name for tag in obj.tags.all() if tag] + ([obj.kind.name] if obj.kind else []),
        'geometry': obj.geometry.wkt,
    }

def migrate_needs():
    print "Migrating Needs"
    from need.models import Need

    for obj in Need.objects.all():
        parsed = parse_need(obj)
        send_to_redis(parsed)

def parse_need(obj):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'need',
        'name': obj.name,
        'description': obj.description,
        "created_at": str(obj.creation_date),
        "updated_at": str(obj.last_update),
        "contacts": obj.contacts,
        "aditional_info": {
            'short_description': obj.short_description,
            'creator': obj.creator.name if obj.creator else None,
            'target_audiences':  [ta.name for ta in obj.target_audiences.all() if ta],
        },
        'tags': [tag.name for tag in obj.tags.all()] + [cat.name for cat in obj.categories.all()],
        'geometry': obj.geometry.wkt,
    }

def migrate_comments():
    print "Migrating Comments"
    from komoo_comments.models import Comment

    for obj in Comment.objects.all():
        parsed = parse_comment(obj)
        send_to_redis(parsed)

def parse_comment(obj):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'comment',
        'author': build_oid(obj.author),
        'comment': obj.comment,
        'created_at': str(obj.pub_date),
        'content_object': build_oid(obj.content_object),
        'additional_info': {
            'sub_comments': obj.sub_comments,
            'parent': build_oid(obj.parent) if obj.parent else None,
        }
    }

def migrate_discussions():
    print "Migrating Discussions"
    from discussion.models import Discussion

    for obj in Discussion.objects.all():
        if obj.content_object and obj.text:
            parsed = parse_discussion(obj)
            send_to_redis(parsed)

def parse_discussion(obj):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'discussion',
        'author': build_oid(obj.last_editor) if obj.last_editor else None,
        'comment': obj.text,
        'created_at': str(obj.last_update),
        'content_object': build_oid(obj.content_object),
        'additional_info': {},
    }

def migrate_users():
    print "Migrating Users"
    from authentication.models import User

    for obj in User.objects.all():
        parsed = parse_user(obj)
        send_to_redis(parsed)

def parse_user(obj):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'user',
        'name': obj.name,
        'email': obj.email,
        'about_me': obj.about_me,
        'cripted_password': obj.password,
        'contacts': obj.contacts,
        'created_at': str(obj.creation_date),
        'language': obj.language,
        'is_admin': obj.is_admin,
        'is_active': obj.is_active,
        'geometry': obj.geometry.wkt,
        'avatar': obj.avatar if obj.avatar != "/static/img/user-placeholder.png" else None,
    }

def migrate_relations():
    print "Migrating Relations"
    from relations.models import Relation

    for obj in Relation.objects.all():
        parsed = parse_relation(obj, Relation)
        send_to_redis(parsed)

def parse_relation(obj, model):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'relation',
        'oid_1': build_oid(model.get_model_from_oid(obj.oid_1)),
        'oid_2': build_oid(model.get_model_from_oid(obj.oid_2)),
        'rel_type': obj.rel_type,
        'direction': 'dir' if obj.direction == '+' else 'rev',
        'created_at': str(obj.creation_date),
        'updated_at': str(obj.last_update),
        'metadata': obj.metadata_dict(),
    }

def migrate_projects():
    print "Migrating Projects"
    from komoo_project.models import Project

    for obj in Project.objects.all():
        parsed = parse_project(obj)
        send_to_redis(parsed)

def parse_project(obj):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'project',
        'name': obj.name,
        'description': obj.description,
        "created_at": str(obj.creation_date),
        "updated_at": str(obj.last_update),
        "contacts": obj.contacts,
        'short_description': obj.short_description,
        'creator': obj.creator.name if obj.creator else None,
        'contributors': [build_oid(c) for c in obj.contributors.all()],
        'logo': str(obj.logo) if obj.logo else None ,
        'tags': [tag.name for tag in obj.tags.all()],
        'maptype': obj.maptype,
        'bbox': obj.bbox if obj.bounds else None,
        'custom_bbox': obj.custom_bbox,
        'partners_logo': [logo.file.url for logo in obj.partners_logo()],
        'related_items': [build_oid(i) for i in obj.related_items]
    }

