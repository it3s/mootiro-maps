require ['jquery', 'map/panel', 'map.jquery'], ($, Panel) ->
  $('#dinamic-form').hide()

  onDrawingFinished = (feature, gotoNextStep) ->
    if not feature.isNew()
      return

    context = $('#dinamic-form')
    $.ajaxSetup cache: true

    if gotoNextStep and feature
      featureType = feature.getFeatureType()
      geojson = feature.getGeometryCollectionGeoJson()
      url = featureType.formUrl
      $.ajax
        url: url
        cache: true
        context: context
        dataType: 'html'
        type: 'GET'
        success: (data, textStatus, jqXHR) ->
          $(this).html data
          $('#id_geometry').val JSON.stringify(geojson)
          $(this).show()
          $(window).resize()
          $('#main-map-container, #map-panel').slideUp 600
        error: (jqXHR, textStatus, errorThrown) ->
          # FIXME
          alert 'ERRO!!!11!'


  $el = $('#main-map-canvas')
  $el.komooMap
    type: 'main'
    geojson: KomooNS?.mainMapGeojson
    height: '100%'
    width: '100%'

  map = $el.data 'map'
  map.subscribe 'drawing_finished', onDrawingFinished

  panel = new Panel map

  # FIXME: Should not export global vars
  window.editor = map

