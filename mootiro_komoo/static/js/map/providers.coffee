define (require) ->
    'use strict'

    googleMaps = require 'googlemaps'
    Component = require './component'

    window.komoo ?= {}
    window.komoo.event ?= googleMaps.event

    class GenericProvider extends Component
        name: 'Generic Provider'
        alt: 'Generic Data Provider'
        tileSize: new googleMaps.Size 256, 256
        maxZoom: 32
        expiration: 600000  # 10 minutes in ms

        enabled: on

        init: (@options) ->
            @addrLatLngCache = {}
            @fetchedTiles = {}

        setMap: (@map) ->
            @map.googleMap.overlayMapTypes.insertAt(0, @)
            @handleMapEvents?()

        enable: -> @enabled = on
        disable: -> @enabled = off

        getUrl: (coord, zoom) ->
            addr = @getAddrLatLng coord, zoom
            @fetchUrl + addr


        getAddrLatLng: (coord, zoom) ->
            key = "x=#{coord.x},y=#{coord.y},z=#{zoom}"
            if @addrLatLngCache[key]
                return @addrLatLngCache[key]

            numTiles = 1 << zoom
            projection = @map.googleMap.getProjection()
            point1 = new googleMaps.Point \
                (coord.x + 1) * @tileSize.width / numTiles,
                coord.y * @tileSize.height / numTiles
            point2 = new googleMaps.Point \
                coord.x * @tileSize.width / numTiles,
                (coord.y + 1) * @tileSize.height / numTiles
            ne = projection.fromPointToLatLng point1
            sw = projection.fromPointToLatLng point2
            @addrLatLngCache[key] = \
                "bounds=#{ne.toUrlValue()},#{sw.toUrlValue()}&zoom=#{zoom}"


    class FeatureProvider extends GenericProvider
        name: 'Feature Provider'
        alt: 'Feature Provider'
        fetchUrl: '/get_geojson?'

        init: (options) ->
            super options
            @keptFeatures = komoo.collections.makeFeatureCollection()
            @openConnections = 0
            @_addrs = []
            @_requestQueue = {}

        handleMapEvents: ->
            @map.subscribe 'idle', =>
                return if @enabled is off

                bounds = @map.googleMap.getBounds()
                @keptFeatures.forEach (feature) =>
                    if not bounds.intersects feature.getBounds()
                        feature.setMap null
                @keptFeatures.clear()

            @map.subscribe 'zoom_changed', =>
                # Aborting ajax requests when zoom changes
                for addr, xhr of @_requestQueue
                    xhr.abort()


        releaseTile: (tile) ->
            return if @enabled is off

            if @fetchedTiles[tile.addr]
                bounds = @map.getBounds()
                @map.data.when @fetchedTiles[tile.addr].features, (features) ->
                    features.forEach (feature) =>
                        if feature.getBounds
                            if not bounds.intersects feature.getBounds()
                                feature.setMap null
                            else if not bounds.contains feature.getBounds().getNorthEast() or \
                                    not bounds.contains feature.getBounds().getSouthWest()
                                @keptFeatures.push feature
                                feature.setMap @map
                        else if feature.getPosition
                            if not bounds.contains feature.getPosition()
                                feature.setVisible false
                                feature.setMap null

        getTile: (coord, zoom, ownerDocument) ->

            div = ownerDocument.createElement('DIV')
            addr = @getAddrLatLng coord, zoom
            div.addr = addr

            return div if @enabled is off

            # Verifies if we already loaded this block
            d = new Date()
            if @fetchedTiles[addr] and
                    (d - @fetchedTiles[addr].date <= @expiration)
                @fetchedTiles[addr].features.setMap @map
                return div
            if @openConnections is 0
                @map.publish 'features_request_started'
            @openConnections++
            @map.publish 'features_request_queued'
            @_requestQueue[addr] = $.ajax
                url: @getUrl coord, zoom
                dataType: 'json'
                type: 'GET'
                success: (data) =>
                    dfd = @map.data.deferred()
                    console?.log "Getting tile #{addr}..."
                    @_addrs.push addr
                    @fetchedTiles[addr] =
                        geojson: data
                        features: dfd.promise()
                        date: new Date()
                error: (jqXHR, textStatus) =>
                    return if textStatus is 'abort'
                    # TODO: Use Spock
                    console?.error "[provider - ajax error] #{textStatus}"
                    serverErrorContainer = $('#server-error')
                    if serverErrorContainer.parent().length is 0
                        serverErrorContainer = $('<div>').attr('id', 'server-error')
                        $('body').append serverErrorContainer
                    errorContainer = $('<div>').html jqXHR.responseText
                    serverErrorContainer.append errorContainer
                complete: =>
                    @map.publish 'features_request_unqueued'
                    @openConnections--
                    if @openConnections is 0
                        @map.publish 'features_request_completed'
                        while @_addrs.length > 0
                            addr = @_addrs.pop()
                            data = @fetchedTiles[addr].geojson
                            features = @map.loadGeoJSON JSON.parse(data), false, true, true
                            @fetchedTiles[addr].features.resolve?(features)
                            @fetchedTiles[addr].features = features
                        delete @_requestQueue[addr]
                        @map.publish 'features_loaded', @map.getFeatures()
            return div


    class ZoomFilteredFeatureProvider extends FeatureProvider
        getUrl: (coord, zoom) ->
            baseUrl = super coord, zoom
            models = []
            for featureTypeName, featureType of @map.featureTypes
                if featureTypeName is 'Community' or  # should always display communities
                  (featureType.minZoomPoint <= zoom and featureType.maxZoomPoint >= zoom) or
                  (featureType.minZoomGeometry <= zoom and featureType.maxZoomGeometry >= zoom)
                    models.push "#{featureType.appLabel}.#{featureType.modelName}"
            baseUrl += '&models=' + models.join(',')



    window.komoo.providers =
        GenericProvider: GenericProvider
        FeatureProvider: FeatureProvider
        ZoomFilteredFeatureProvider: ZoomFilteredFeatureProvider
        makeFeatureProvider: (options) -> new FeatureProvider options

    return window.komoo.providers
