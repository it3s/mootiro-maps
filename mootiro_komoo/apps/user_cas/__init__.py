# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf import settings
from django.contrib.auth.models import User
from django_cas.backends import CASBackend, _verify


class KomooCASBackend(CASBackend):
    '''If a user manages to log in through CAS, fetch their details from
    MootiroProfile and ensure a corresponding user exists in this app.
    '''
    def authenticate(self, ticket, service):
        """Verifies CAS ticket and gets or creates User object.
        """
        email = _verify(ticket, service)
        if not email:
            return None
        try:
            user = User.objects.get(email__iexact=email)
            # This user already exists in the Mootiro app
            # TODO: Use the MootiroProfile webservice to update avatar etc.
        except User.DoesNotExist:
            # This user does not yet exist in MootiroVote
            # Get username from Profile server
            profile_db = "host='{}' dbname='{}' user='{}' password='{}'" \
                .format(*settings.PROFILE_DATABASE.split("|"))
            import psycopg2
            profile_db_conn = psycopg2.connect(profile_db)
            c = profile_db_conn.cursor()
            c.execute("SELECT nickname FROM \"user\" WHERE email = '{}'".format(email))
            user_info = c.fetchall()
            username = user_info[0][0]
            # This user will have an "unusable" password
            # user = User.objects.create_user(username, '')
            # user.email = email
            # user.save()

            user = User(username=username, email=email)
            # user.set_password(form.cleaned_data['password1'])
            user.email_isvalid = True
            user.save()
            # from forum.actions import UserJoinsAction
            # UserJoinsAction(user=user).save()
        return user
        # '''
        # #~ user, created = User.objects.get_or_create(username=username)
        # #~ if created:
        #     #~ user.set_unusable_password()
        # if authentication_response and _CAS_USER_DETAILS_RESOLVER:
        #     _CAS_USER_DETAILS_RESOLVER(user, authentication_response)
        # #~ user.save()
        # return user
        # '''
