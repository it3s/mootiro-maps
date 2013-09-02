# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

class MapButtonWidget(forms.Widget):
    """Map button widget"""

    def render_js(self, field_id, button_id, container_id):
        js = u"""
            $('#%(button_id)s').click(function () {
                $('#main-content').hide();
                if (!window.editor) {
                  window.editor = initialize_map_editor();
                  komoo.event.addListener(window.editor, 'features_loaded', function (features) {
                    var feature = window.editor.getFeatures().getAt(0);
                    if (feature.getGeometryType() == komoo.geometries.types.EMPTY) {
                        window.editor.editFeature(feature, feature.featureType.geometryTypes[0]);
                        window.editor.goToUserLocation();
                    } else {
                        window.editor.editFeature(feature);
                    }
                  });
                  komoo.event.addListener(window.editor, 'drawing_finished', function (feature, gotoNextStep) {
                    if (gotoNextStep) {
                      $('#%(field_id)s').val(JSON.stringify(feature.getGeometryCollectionGeoJson()));
                    } else {
                    }
                    $('#%(container_id)s').slideUp(600);
                    $('#main-content').show();
                  });
                  window.editor.loadGeoJSON(geojson_editor, true);
                  $('#%(field_id)s').val(JSON.stringify(window.editor.getGeoJson({geometryCollection: true})));
                } else {
                    window.editor.editFeature();
                }
                $('#%(container_id)s').show();
                google.maps.event.trigger(window.editor.googleMap, 'resize');

                return false;
            });
        """ % {
                'field_id': field_id,
                'button_id': button_id,
                'container_id': container_id,
            }
        return js

    def render(self, name, value=None, attrs=None):
        field_id = 'id_{}'.format(name)
        button_id = '{}_button'.format(field_id)
        container_id = attrs.get('container_id', 'map-container-editor')
        html = u"""
            <div>
                <input type="hidden" value="%(value)s" id="%(field_id)s" name="%(name)s" >
                <a href="#" class="button" id="%(button_id)s">%(button_title)s</a>
            </div>
            <script type="text/javascript"><!--//
                %(js)s
            //--></script>
        """ % {
                'name': name,
                'value': value,
                'field_id': field_id,
                'button_id': button_id,
                'button_title': _('Open the map editor'),
                'js': self.render_js(field_id, button_id, container_id),
            }
        return html
