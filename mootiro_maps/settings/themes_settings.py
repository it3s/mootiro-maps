import os.path
from django.utils.translation import ugettext_lazy as _

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

THEMES = ({
    'name': _("Mootiro"),
    'description': _("Mootiro Maps default theme"),
    'screenshot': "/static/default/screenshot.png",
    'template_dir': "default",
    # If you will use TEMPLATE_LOADERS method described in setup section,
    # than you should specify full path
    #'template_dir': os.path.join(PROJECT_ROOT, "templates/theme1"),
    'static_url': "/static/themes/default/",
},
{
    'name': _("Child Friendly Places"),
    'description': _("Child Friendly Places Theme"),
    'screenshot': "/static/child/screenshot.png",
    'template_dir': "child",
    # If you will use TEMPLATE_LOADERS method described in setup section,
    # than you should specify full path
    #'template_dir': os.path.join(PROJECT_ROOT, "templates/theme2"),
    'static_url': "/static/themes/child/",
})

DEFAULT_THEME = 0
