from django.conf import settings  # import the settings file


def social_keys(context):
    return {'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID}
