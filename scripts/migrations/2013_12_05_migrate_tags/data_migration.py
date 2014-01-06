from taggit.models import Tag, TaggedItem


def migrate_tag_objects(ids):
  # tags_count_list = [(t.id, TaggedItem.objects.filter(tag=t).count()) for t in qs]
  print "migrate %s <= %s" % (ids[0], ids[1:])
  target = Tag.objects.get(pk=ids[0])
  tags = ids[1:]
  for tag in tags:
    tag = Tag.objects.get(pk=tag)
    objects = [item.content_object for item in tag.taggit_taggeditem_items.all()]
    for obj in objects:
      print "move %s on object %s to %s" % (tag.id, obj, target.id)
      obj.tags.add(target)
      obj.tags.remove(tag)
    tag.delete()


def migrate_duplicated_tags():
  alreade_migrated = set()
  for tag in Tag.objects.all():
    qs = Tag.objects.filter(name=tag.name.lower())
    ids = set()
    if qs.count() > 1:
      ids.add(tag.id)
      [ids.add(t.id) for t in qs]
      if len(ids & alreade_migrated) == 0:
        migrate_tag_objects(list(ids))
        [alreade_migrated.add(id) for id in ids]

def lowercase_all_tags():
    print 'lowercase_all_tags'
    for tag in Tag.objects.all():
      if not tag.name.islower():
        print "'%s'  ==>  '%s'" % (tag.name, tag.name.lower())
        tag.name = tag.name.lower()
      tag.name = tag.name.strip()
      if not tag.name:
        tag.delete()
      else:
        tag.save()


def run():
  lowercase_all_tags()
  migrate_duplicated_tags()

