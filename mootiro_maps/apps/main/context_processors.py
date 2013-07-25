from django.conf import settings  # import the settings file
from django.middleware.csrf import get_token


def komoo_namespace(request):
    """Sets implicit values for the KommoNS variable.

    This variable is used to set the application's javascript namespace.

    Returns:
        isAuthenticated: if the user is authenticated or not
        user: a json representation for the current user
        lang: the language being used
        facebookAppId: app id for facebook integration
        require_baseUrl: use for proper requirejs configuration. Used to serve
            minified static files on production and regular static files on
            development.
        csrf_token: token for cross-site request forgery protection.
        staticUrl: our configured statics url root.

    """
    user_dict = request.user.to_dict()
    user = {
        'id': user_dict.get('id', None),
        'name': user_dict.get('name', 'Anonymous'),
        'email': user_dict.get('email', None),
        'url': user_dict.get('url', ''),
    }
    return {
        'KomooNS': {
            'isAuthenticated': request.user.is_authenticated(),
            'user_data': user,
            'lang': (getattr(request, 'LANGUAGE_CODE', None) or
                     settings.LANGUAGE_CODE),
            'facebookAppId': settings.FACEBOOK_APP_ID,
            'require_baseUrl': (settings.STATIC_URL +
                                'js' if settings.DEBUG else 'js.build'),
            'csrf_token': get_token(request),
            'staticUrl': settings.STATIC_URL,
        },
        'SITE_URL': settings.SITE_URL,
    }
