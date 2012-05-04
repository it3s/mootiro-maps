# -*- coding:utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import ast

from django import template
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from main.utils import templatetag_args_parser, create_geojson
from main.widgets import (ImageSwitch, ImageSwitchMultiple, TaggitWidget,
                          Autocomplete)
from community.models import Community
from need.models import Need, NeedCategory
from organization.models import Organization
from komoo_resource.models import Resource
from proposal.models import Proposal

register = template.Library()


def _get_related_community(obj):
    if isinstance(obj, Community):
        community = obj
    elif isinstance(obj, Need):
        community = obj.community
    elif isinstance(obj, Proposal):
        community = obj.need.community
    else:
        community = None
    return community


@register.simple_tag
def geojson(obj=None):
    """Returns a geojson with obj data"""
    if obj.geometry.empty:
        return '{}'
    return create_geojson([obj]).replace("'", "\\'").replace('"', "'")


@register.inclusion_tag('main/templatetags/menu.html')
def menu(obj=None, selected_area=''):
    community = _get_related_community(obj)
    return dict(community=community, selected_area=selected_area)


@register.inclusion_tag('main/templatetags/community_tabs.html')
def community_tabs(obj=None):
    community = _get_related_community(obj)
    return dict(community=community)


@register.inclusion_tag('main/templatetags/geo_objects_listing.html')
def geo_objects_listing(arg1='', arg2='', arg3=''):
    """Usage: {% geo_objects_listing [show_categories] [switchable] [prefix] %}"""
    parsed_args = templatetag_args_parser(arg1, arg2, arg3)
    show_categories = parsed_args.get('show_categories', 'False').lower() == 'true'
    switchable = parsed_args.get('switchable', 'False').lower() == 'true'
    prefix = parsed_args.get('prefix', '')

    img = {
        'communities': Community.image,
        'communities_off': Community.image_off if switchable else Community.image,
        'needs': Need.image,
        'needs_off': Need.image_off if switchable else Need.image,
        'organizations': Organization.image,
        'organizations_off': Organization.image_off if switchable else Organization.image,
        'resources': Resource.image,
        'resources_off': Resource.image_off if switchable else Resource.image,
    }

    image_field = lambda image, image_off: \
        forms.BooleanField(
            widget=ImageSwitch(image_tick=image, image_no_tick=image_off, prefix=prefix)
        )

    class GeoObjectsForm(forms.Form):
        communities = image_field(img['communities'], img['communities_off'])
        needs = image_field(img['needs'], img['needs_off'])
        organizations = image_field(img['organizations'], img['organizations_off'])
        resources = image_field(img['resources'], img['resources_off'])

        need_categories = forms.ModelMultipleChoiceField(
            queryset=NeedCategory.objects.all().order_by('name'),
            widget=ImageSwitchMultiple(
                get_image_tick=NeedCategory.get_image,
                get_image_no_tick=NeedCategory.get_image_off if switchable \
                                    else NeedCategory.get_image,
                show_names=True,
                prefix=prefix
            )
        )

    form = GeoObjectsForm()

    return dict(form=form, show_categories=show_categories)


@register.inclusion_tag('main/templatetags/geo_objects_add.html')
def geo_objects_add(arg1='', arg2='', arg3=''):
    """Usage: {% geo_objects_add [prefix] %}"""
    parsed_args = templatetag_args_parser(arg1, arg2, arg3)
    prefix = parsed_args.get('prefix', '')

    img = {
        'communities': Community.image,
        'needs': Need.image,
        'organizations': Organization.image,
        'resources': Resource.image,
    }

    return dict(img=img, STATIC_URL=settings.STATIC_URL)


@register.inclusion_tag('main/templatetags/track_buttons.html')
def track_buttons():
    return dict()


@register.inclusion_tag('main/templatetags/taglist.html')
def taglist(obj):
    return dict(object=obj)


@register.inclusion_tag('main/templatetags/pagination.html')
def pagination(collection):
    return dict(collection=collection)


@register.filter
def with_http(link):
    """prepends http:// to a given link if it does not already have"""
    return 'http://{link}'.format(link=link) if not 'http://' in link else link


@register.filter
def split(entry, splitter):
    return entry.split(splitter)


def _get_widgets_dict(obj):
    tag_widget = TaggitWidget(autocomplete_url="/%s/search_by_tag/" % obj)
    tag_widget = "%s \n %s" % (str(tag_widget.media), tag_widget.render('tags'))

    community_widget = Autocomplete(Community, '/community/search_by_name')
    community_widget = "%s \n %s" % (str(community_widget.media),
                                     community_widget.render('community'))

    # filters
    return {
        'tags': tag_widget,
        'community': community_widget
    }


@register.inclusion_tag('main/templatetags/visualization_opts.html', takes_context=True)
def visualization_opts(context, obj, arg1='', arg2=''):
    """
    Templatetag for visualization options (sorters and filters)
    usage:
        {% visualization_opts 'resource' "filters=['tags']" "sorters=['name', 'creation_date']" %}
        {% visualization_opts 'organization' "sorters=['name', 'creation_date']"}
    """
    # parse options
    opts = {}
    for arg in [arg1, arg2]:
        if arg and '=' in arg:
            k, v = arg.split('=')
            v = ast.literal_eval(v)
            opts[k] = v

    field_labels = {
        'tags': _('Tags'),
        'name': _('Name'),
        'title': _('Name'),
        'creation_date': _('Date'),
        'vote': _('Vote'),
        'community': _('Community')
    }

    # sorters
    sort_fields = [(field_labels[field], field) for field in opts.get('sorters', [])]

    # filters
    field_widgets = _get_widgets_dict(obj)
    filter_fields = [(field, field_labels[field], field_widgets[field]) \
                        for field in opts.get('filters', [])]

    return  dict(filters=filter_fields, sorters=sort_fields)


@register.simple_tag(takes_context=True)
def visualization_opts_js(context):
    return """
    <script type="text/javascript">

        $(function(){


          /* Visualization Option */
          $('.view-list-visualization-header').click(function(){
            $('.view-list-visualization-options').slideToggle();
            $('.view-list-visualization-header i').toggleClass('icon-chevron-right');
            $('.view-list-visualization-header i').toggleClass('icon-chevron-down');
          });

          // if we made a query, open selectors
          if(getUrlVars()['sorters'] || getUrlVars()['filters']){
            $('.view-list-visualization-options').show();
            $('.view-list-visualization-header i').removeClass('icon-chevron-right');
            $('.view-list-visualization-header i').addClass('icon-chevron-down');
            $.each( getUrlVars()['filters'].split(',') ,function(idx, field){
              $('.view-list-filter-widget-wrapper[widget-for='+ field + ']').show();
            });
          }

          // get sorters state
          var _sorters = getUrlVars()['sorters'];
          if (_sorters){
            _sorters = _sorters.split(',');
          }
          if (_sorters && _sorters.length > 0 && _sorters[0]){
            $.each(_sorters, function(idx, val){
              $('.view-list-sorter-btn[sorter-name=' + val + ']').addClass('selected');
              if (val.indexOf('date') !== -1){
                date_order = getUrlVars()[val];
                $('.date-sorter-order div[order=' + date_order + '] i').addClass('icon-active');
              }
            });
          } else {
            var main_field = $('.view-list-sorter-btn[sorter-name=name]');
            if (!main_field.length) {
              main_field = $('.view-list-sorter-btn[sorter-name=title]');
            }
            main_field.addClass('selected');
          }

          // get filters state
          var _filters = getUrlVars()['filters'];
          if (_filters){
            _filters = _filters.split(',');
          }
          if (_filters && _filters.length > 0 && _filters[0]){
            $.each(_filters, function(idx, val){
              $('.view-list-filter-btn[filter-name=' + val + ']').addClass('selected');
              if (val == 'tags'){
                var tags = unescape(getUrlVars()['tags']);
                tags = tags.split(',');
                $.each(tags, function(idx, tag){
                  $('#id_tags').addTag(tag);
                });
              } else if(val == 'community'){
                var id = unescape(getUrlVars()[val]);
                $.get('/community/get_name_for/'+ id +'/', {}, function(data){
                  $('#id_community_autocomplete').val(data.name);
                  $('#id_community').val(id);
                });
              }else {
                var filter_val = unescape(getUrlVars()[val]);
                $('.view-list-filter-widget[widget-for=' + val + '] input').val(filter_val);
              }
            });
          }

          // auto-fill community
          var comm = {id: "%(comm_id)s", name: "%(comm_name)s"};
          if (comm.id){
            $('#id_community').val(comm.id);
            $('#id_community_autocomplete').val(comm.name);

            $('.view-list-visualization-options').show();
            $('.view-list-visualization-header i').removeClass('icon-chevron-right');
            $('.view-list-visualization-header i').addClass('icon-chevron-down');

            $('.view-list-filter-btn[filter-name=community]').addClass('selected');
            $('.view-list-filter-widget-wrapper[widget-for=community]').show();
          }

          // reset tagsinput styles
          $('.view-list-filter-widget .tagsinput').attr('style', '');

          // click on btn change classes.
          $('.view-list-sorter-btn').click(function(){
            var that = $(this);
            that.toggleClass('selected');
            if ( that.attr('sorter-name').indexOf('date') !== -1) {
              if (that.hasClass('selected')) {
                date_order = 'desc';
                $('.date-sorter-order div[order=desc] i').addClass('icon-active');
              } else {
                date_order = '';
                $('.date-sorter-order i').removeClass('icon-active');
              }
            }
          });
          $('.view-list-filter-btn').click(function(){
            var that = $(this);
            that.toggleClass('selected');
            var filter_name = that.attr('filter-name');
            $('.view-list-filter-widget-wrapper[widget-for=' + filter_name + ']').slideToggle();
          });

          // get filters
          window.getFilters = function(){

            var sorters = [],
                filters = [],
                filter_fields = '';

            $('.view-list-sorter-btn.selected').each(function(idx, val){
              var sorter_name = $(val).attr('sorter-name');
              sorters.push(sorter_name);
              if ( sorter_name.indexOf('date') != -1) {
                filter_fields += '&' + sorter_name + '=' + date_order;
              }
            });

            $('.view-list-filter-btn.selected').each(function(idx, val){
              var filter_name = $(val).attr('filter-name');
              filters.push(filter_name);
              filter_fields += '&' + filter_name + '=' +
                escape($('.view-list-filter-widget[widget-for=' + filter_name + '] input').val());
            });

            return 'sorters=' + sorters.join() + '&filters=' + filters.join() + filter_fields;
          };

          $('#doFilter').click(function(){
            window.location = location.pathname + '?' + getFilters();
          });

          $('.komoo-pagination a').click(function(evt){
            var that = $(evt.target);
            // if selectors are open
            if ($('.view-list-visualization-header i').hasClass('icon-chevron-down')){
              evt.preventDefault();
              window.location = that.attr('href') + '&' + getFilters();
            }
          });

          $('.date-sorter-order div').bind('click', function(){
            $('.date-sorter-order div .icon-active').removeClass('icon-active');
            $(this).find('i').toggleClass('icon-active');
            date_order = $(this).attr('order');
          });

      });
      </script>
    """ % {
      'comm_id': context['community'].id if context.get('community', None) else '',
      'comm_name': context['community'].name if context.get('community', None) else ''}


@register.inclusion_tag('main/templatetags/beautiful_list.html')
def beautiful_list(objects, arg1='', arg2=''):
    """Usage: """
    parsed_args = templatetag_args_parser(arg1, arg2)
    entity_type = parsed_args.get('entity_type').lower()
    item_template = parsed_args.get('item_template').lower()

    return dict(objects=objects, entity_type=entity_type,
                    item_template=item_template)
