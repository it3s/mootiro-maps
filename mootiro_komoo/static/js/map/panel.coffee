define ['jquery', 'map_filter', 'utils'], ($) ->
  # TODO: Use Backbone to create the panel

  class Panel
    constructor: (map) ->
      @tabs = new Tabs '.panel-tab', '.panel'

      onHashChange = () ->
        hash = window.location.hash
        $(hash + '-tab').click()
      onHashChange()
      window.onhashchange = onHashChange

      @menu = $("#map-add-menu")
      @connect map


    onDrawingStarted: (feature) ->
      @menu.find('.item').removeClass 'selected'
      @menu.find('.sublist').hide()
      @menu.find('.collapser i.icon-chevron-down').toggleClass 'icon-chevron-right icon-chevron-down'
      menuItem = @menu.find('.' + feature.getType().toLowerCase() + ' .item')
      menuItem.addClass 'selected'
      @menu.addClass 'frozen'


    onDrawingFinished: (feature) ->
      @menu.find('.item').removeClass 'selected'
      @menu.removeClass 'frozen'


    connect: (map) ->
      console?.log 'Connecting panel'

      that = this
      @menu.find('.item, .sublist li > div').click (e) ->
        if that.menu.hasClass 'frozen'
          return false

        item = $(this)
        if item.attr 'data-geometry-type'
          map.drawNewFeature item.attr('data-geometry-type'), item.attr('data-feature-type')
        else
          $('.collapser', item.parent()).click()

      $('#collapse-panel').click (ev) ->
        $parent = $("#main-map-panel").parent()
        $parent.toggleClass "collapsed"
        map?.refresh()
        interval = setInterval (() -> map?.refresh()), 500
        setTimeout (() -> clearInterval(interval)), 1000

      map.subscribe 'drawing_started', @onDrawingStarte, this
      map.subscribe 'drawing_finished', @onDrawingFinished, this

      $('#map-panel').show()
      $(window).resize()


  return Panel
