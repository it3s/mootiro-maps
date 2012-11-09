(function() {

  require(['jquery', 'map/panel', 'map.jquery'], function($, Panel) {
    var $el, map, onDrawingFinished, panel;
    $('#dinamic-form').hide();
    onDrawingFinished = function(feature, gotoNextStep) {
      var context, featureType, geojson, url;
      if (!feature.isNew()) return;
      context = $('#dinamic-form');
      $.ajaxSetup({
        cache: true
      });
      if (gotoNextStep && feature) {
        featureType = feature.getFeatureType();
        geojson = feature.getGeometryCollectionGeoJson();
        url = featureType.formUrl;
        return $.ajax({
          url: url,
          cache: true,
          context: context,
          dataType: 'html',
          type: 'GET',
          success: function(data, textStatus, jqXHR) {
            $(this).html(data);
            $('#id_geometry').val(JSON.stringify(geojson));
            $(this).show();
            $(window).resize();
            return $('#main-map-container, #map-panel').slideUp(600);
          },
          error: function(jqXHR, textStatus, errorThrown) {
            return alert('ERRO!!!11!');
          }
        });
      }
    };
    $el = $('#main-map-canvas');
    $el.komooMap({
      type: 'main',
      geojson: typeof KomooNS !== "undefined" && KomooNS !== null ? KomooNS.mainMapGeojson : void 0,
      height: '100%',
      width: '100%'
    });
    map = $el.data('map');
    map.subscribe('drawing_finished', onDrawingFinished);
    panel = new Panel(map);
    return window.editor = map;
  });

}).call(this);
