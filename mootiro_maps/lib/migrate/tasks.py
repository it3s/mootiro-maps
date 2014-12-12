# coding: utf-8
import os
from redis import StrictRedis
import simplejson as json

HOST = os.getenv('REDIS_HOST', '10.0.2.2')
PORT = os.getenv('REDIS_PORT', 6379)
PASS = os.getenv('REDIS_PASS', '')
redis = StrictRedis(host=HOST, port=PORT, db=0, password=PASS)

def send_to_redis(obj):
    oid = obj['oid']
    redis.rpush('mootiro:migrations', oid)
    redis.set('mootiro:{}'.format(oid), json.dumps(obj))

OID_MAPPER = {
    "Organization":    'org',
    "Community":       'com',
    "Resource":        'res',
    "Need":            'ned',
    "User":            'usr',
    "Discussion":      'dis',
    "Comment":         'cmt',
    "Proposal":        'pps',
    "Project":         'pro',
    "Relation":        'rel',
    "Layer":           'lay',
    "UploadedFile":    'fil',
    "Video":           'vid',
    "ModelVersion":    'ver',
    "Signature":       'sig',
    "Report":          'rep',
}
def build_oid(obj):
    return "{}_{}".format(OID_MAPPER[obj.__class__.__name__], obj.id)


def migrate_all():
    migrate_users()
    migrate_organizations()
    migrate_communities()
    migrate_resources()
    migrate_needs()
    migrate_projects()
    migrate_comments()
    migrate_discussions()
    migrate_relations()
    migrate_layers()
    migrate_signatures()
    migrate_reports()
    migrate_files()
    migrate_videos()
    migrate_versions()

def migrate_organizations():
    print "Migrating Organizations"
    from organization.models import Organization

    for obj in Organization.objects.all():
        parsed = parse_organization(obj)
        send_to_redis(parsed)

def get_wkt(obj):
    points = obj.points
    lines = obj.lines
    polys = obj.polys
    # use the geometry collection by default
    geom = obj.geometry
    # check if tere is only one type of geometry. If true selects it.
    if not ((points and lines) or (points and polys) or (lines and polys)):
        if points:
            geom = points
        elif lines:
            geom = lines
        elif polys:
            geom = polys
        else:
            return "POINT EMPTY"
    return geom.wkt

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
        'geometry': get_wkt(obj),
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
        'geometry': get_wkt(obj),
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
        'geometry': get_wkt(obj),
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
        'geometry': get_wkt(obj),
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
        'geometry': get_wkt(obj),
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
        'creator': build_oid(obj.creator) if obj.creator else None,
        'contributors': [build_oid(c) for c in obj.contributors.all()],
        'logo': str(obj.logo) if obj.logo else None ,
        'tags': [tag.name for tag in obj.tags.all()],
        'maptype': obj.maptype,
        'bbox': obj.bbox if obj.bounds else None,
        'custom_bbox': obj.custom_bbox,
        'partners_logo': [logo.file.url for logo in obj.partners_logo()],
        'related_items': [build_oid(i) for i in obj.related_items]
    }

def migrate_layers():
    print "Migrating Layers"
    from komoo_project.models import Layer

    for obj in Layer.objects.all():
        parsed = parse_layer(obj)
        send_to_redis(parsed)

def parse_layer(obj):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'layer',
        'name': obj.name,
        'project': build_oid(obj.project),
        'position': obj.position,
        'visible': obj.visible,
        'fill_color': obj.fillColor,
        'stroke_color': obj.strokeColor,
        'rule': obj.rule,
    }

def migrate_files():
    print "Migrating Files"
    from fileupload.models import UploadedFile

    for obj in UploadedFile.objects.all():
        parsed = parse_file(obj)
        send_to_redis(parsed)

def parse_file(obj):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'file',
        'file': str(obj.file) if obj.file else None,
        'subtitle': obj.subtitle,
        'cover': obj.cover,
        'content_object': build_oid(obj.content_object) if obj.content_object else None,
    }

def migrate_videos():
    print "Migrating Videos"
    from video.models import Video

    for obj in Video.objects.all():
        parsed = parse_video(obj)
        send_to_redis(parsed)

def parse_video(obj):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'video',
        'title': obj.title,
        'description': obj.description,
        'video_url': obj.video_url,
        'video_id': obj.video_id,
        'thumbnail_url': obj.thumbnail_url,
        'service': obj.service,
        'content_object': build_oid(obj.content_object) if obj.content_object else None,
    }


def migrate_versions():
    print "Migrating Versions"
    from model_versioning.models import ModelVersion

    for obj in ModelVersion.objects.all():
        parsed = parse_version(obj)
        send_to_redis(parsed)

def parse_version(obj):
    item_oid = "{}_{}".format(OID_MAPPER[obj.table_ref.split('.')[-1]], obj.object_id)
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'version',
        'item': item_oid,
        'whodunnit': build_oid(obj.creator) if obj.creator else None,
        'created_at': str(obj.creation_date),
        'data': obj.data,
    }

def migrate_signatures():
    print "Migrating Signatures"
    from signatures.models import Signature

    for obj in Signature.objects.all():
        if obj.user and obj.content_object and obj.content_object.__class__.__name__ not in ['Investment']:
            parsed = parse_signature(obj)
            send_to_redis(parsed)

def parse_signature(obj):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'signature',
        'user': build_oid(obj.user),
        'content_object': build_oid(obj.content_object),
    }

def migrate_reports():
    print "Migrating Reports"
    from moderation.models import Report

    for obj in Report.objects.all():
        parsed = parse_report(obj)
        send_to_redis(parsed)

def parse_report(obj):
    return {
        'oid': build_oid(obj),
        'mootiro_type': 'report',
        'user': build_oid(obj.user),
        'content_object': build_oid(obj.moderation.content_object),
        'created_at': str(obj.date),
        'comment': obj.comment,
        'reason': obj.reason_name,
    }
