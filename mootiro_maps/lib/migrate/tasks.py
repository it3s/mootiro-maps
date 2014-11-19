# coding: utf-8

def migrate_all():
    migrate_organizations()

def migrate_organizations():
    from organization.models import Organization

    for org in Organization.objects.all():
        obj = parse_organization(org)
        # send to redis json.dups(obj)

def parse_organization(org):
    return {
        'oid': 'o{}'.format(org.id),
        'mootiro_type': 'organization',
        'name': org.name,
        'description': org.description,
        "created_at": org.creation_date,
        "updated_at": org.last_update,
        "contacts": org.contacts,
        "aditional_info": {
            'target_audiences':  [ta.name for ta in org.target_audiences.all()],
            'short_description': org.short_description,
            'creator': org.creator.name,
        },
        'tags': [tag.name for tag in org.tags.all()] + [c.get_translated_name() for c in org.categories.all()],
        'geometry': org.geometry.wkt,
        # logo ? logo_category ? logo_choice ?
    }

