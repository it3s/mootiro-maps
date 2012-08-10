define ['map/maps'], ->
    (($) ->
        methods =
            init: (options) ->
                @each ->
                    $this = $(this)
                    opts = $.extend({element: $this.get(0)}, $.fn.komooMap.defaults, options)
                    if opts.width? then $this.width opts.width
                    if opts.height? then $this.height opts.height
                    map = komoo.maps.makeMap(opts)
                    $this.data 'map', map
                    if opts.mapType? then map.googleMap.setMapTypeId opts.mapType

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
