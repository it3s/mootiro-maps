define ['map/maps'], ->
    (($) ->
        fixMapSize = (e) ->
            map = e.data.map
            fixMapHeight map
            fixMapWidth map
            map.refresh()

        fixMapHeight = (map, mapPanel = $('#map-panel')) ->
            height = $('body').innerHeight() - $('#top').innerHeight() - $('.mootiro_bar').innerHeight() - 5
            $(map.element).height height
            mapPanel.height height
            $('.panel', mapPanel).height(height - (window.community_slug ? 170 : 146))

        fixMapWidth = (map, mapPanel = $('#map-panel')) ->
            panelWidth = mapPanel.innerWidth()
            try
                panelLeft = mapPanel.position().left
            catch err
                panelLeft = 0

            $(map.element).css marginLeft: panelWidth + panelLeft, width: 'auto'

        methods =
            init: (options) ->
                @each ->
                    $this = $(this)
                    $this.addClass 'komoo-map-googlemap'  # Reverts bootstraps css rules
                    opts = $.extend {element: $this.get(0)}, $.fn.komooMap.defaults, options
                    if opts.width? then $this.width opts.width
                    if opts.height? then $this.height opts.height
                    map = komoo.maps.makeMap opts
                    $this.data 'map', map
                    if opts.mapType? then map.googleMap.setMapTypeId opts.mapType
                    if opts.height is '100%'
                        $(window).resize map: map, fixMapSize
                        $(window).resize()

            edit: (feature) ->
                $(this).data('map').editFeature feature
                $(this)

            geojson: (geojson) ->
                if not geojson?
                    $(this).data('map').getGeoJson()
                else
                    $(this).data('map').loadGeoJson geojson

            goTo: (opts) ->
                $(this).data('map').goTo opts.position ? opts.address, opts.displayMarker
                $(this)

            resize: ->
                $(window).resize()

        $.fn.komooMap = (method) ->
            if methods[method]
                methods[method].apply this, Array.prototype.slice.call(arguments, 1)
            else if typeof method is 'object' or not method
                methods.init.apply this, arguments
            else
                $.error "Method #{method} does not exist on jQuery.komooMap"

        $.fn.komooMap.defaults =
            type: 'editor'
    )(jQuery)
