# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import traceback
import datetime

from django import forms
from django.forms import model_to_dict
from django.shortcuts import render_to_response, RequestContext
from django.utils import simplejson
from django.http import HttpResponse

from annoying.functions import get_object_or_None

logger = logging.getLogger(__name__)


#
# ================ Serializador json ======================================
#
def json_serializer(objeto):
    obj = dict()
    for field, value in objeto.iteritems():
        if not field.startswith('_'):
            if isinstance(value, datetime.datetime
                ) or isinstance(value, datetime.date):
                obj[field] = value.strftime("%d/%m/%Y")
            else:
                obj[field] = value or ''
    return obj


#
# ========== Custom ModelForm ============================
#
class AjaxModelForm(forms.ModelForm):
    """
    Custom model form para trabalhar com o ajaxforms (nosso plugin do jQuery)
    """
    id = forms.IntegerField(widget=forms.widgets.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        r = super(AjaxModelForm, self).__init__(*args, **kwargs)

        if hasattr(self, 'field_labels'):
            for field, label in self._field_labels.iteritems():
                self.fields[field].label = label

        return r

    def _field_label(self, field):
        if field == '__all__':
            return '__all__'
        return self.fields[field].label or field.title()

    def validation(self, field, msg, condition):
        if condition:
            label = self._field_label(field)
            self.errors[label] = unicode(msg)

    def is_valid(self):
        _is_valid = super(AjaxModelForm, self).is_valid()
        for field in self.fields:
            if field in self.errors:
                label = self._field_label(field)
                msg = self.errors[field]
                del self.errors[field]
                self.errors[label] = msg
        return _is_valid

    def add_user(self, request):
        self.user = request.user

    def save(self, *args, **kwargs):
        if self.user:
            self.instance.user = self.user
        elif 'user' in self.cleaned_data:
            self.instance.user = self.cleaned_data['user']
        return super(AjaxModelForm, self).save(*args, **kwargs)


#
# ===========  Decorator que processa forms em uma view, via ajax =============
#
try:
    from functools import wraps
except ImportError:
    def wraps(wrapped, assigned=('__module__', '__name__', '__doc__'),
              updated=('__dict__',)):
        def inner(wrapper):
            for attr in assigned:
                setattr(wrapper, attr, getattr(wrapped, attr))
            for attr in updated:
                getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
            return wrapper
        return inner


def ajax_form(template=None, form_class=None, form_name="form"):
    def renderer(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            output = function(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            #tmpl = output.pop('TEMPLATE', template)

            logger.debug('request via {}'.format(request.method))
            if request.method == 'GET':
                logger.debug('[ajaxforms] acesso via GET')
                form = form_class()

                # callback on_get
                if 'on_get' in output:
                    logger.debug('[ajaxforms] callback on_get:')
                    output.pop('on_get')(request)

                retorno = {form_name: form}
                retorno.update(output)
                return render_to_response(template, retorno,
                            context_instance=RequestContext(request))

            request.POST = request.POST.copy()

            # callback on_before_validation
            if 'on_before_validation' in output:
                logger.debug('[ajaxforms] callback on_before_validation:')
                output.pop('on_before_validation')(request)

            logger.debug('[ajaxforms] post data: %s' % request.POST)
            id_ = request.POST.get('id', '') or \
                  request.POST.get('pk', '') or None
            if id_:
                instance = get_object_or_None(form_class.Meta.model(), id=id_)
                form = form_class(request.POST, instance=instance)
            else:
                form = form_class(request.POST)
            form.add_user(request)
            json_ = {}
            if form.is_valid():
                try:
                    # callback before save
                    if 'on_before_save' in output:
                        logger.debug('[ajaxforms] callback on_before_save:')
                        output.pop('on_before_save')(request, form)

                    obj = form.save()

                    # callback after save
                    if 'on_after_save' in output:
                        try:
                            logger.debug('[ajaxforms] callback on_after_save:')
                            output.pop('on_after_save')(request, obj)
                        except Exception as err:
                            logger.error('[utils.py] Erro no on_after_save: {}'
                                ''.format(err))
                            traceback.print_exc()
                    try:
                        obj_serialized = json_serializer(model_to_dict(obj))
                        obj_serialized['repr'] = unicode(obj)
                        json_ = simplejson.dumps({
                            'success': 'true',
                            'obj': obj_serialized
                        })
                    except Exception as err:
                        logger.error('Erro ao parsear json: {} \n{}'
                            ''.format(err, traceback.format_exc()))
                except Exception as err:
                    logger.error('[ajaxforms] Erro ao salvar dados: {} \n{}'
                        ''.format(err, traceback.format_exc()))
            else:
                logger.info('[ajaxforms] form invalido: {}'
                    ''.format(form.errors))

                # call on invalid
                if 'on_invalid_form' in output:
                    logger.debug('[utils.py] callback on_invalid_form:')
                    output.pop('on_invalid_form')(request, form)

                json_ = simplejson.dumps({
                    'success': 'false',
                    'errors': form.errors,
                })
            logger.debug('[utils.py] retornando json: {}'.format(json_))
            return HttpResponse(json_, mimetype="application/json")
        return wrapper
    return renderer
