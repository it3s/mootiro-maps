define ['map/component'], (Component) ->
    'use strict'

    window.komoo ?= {}
    window.komoo.event ?= google.maps.event

    class CleanMapType extends Component
        id: 'clean'
        constructor: ->
            @mapType = new google.maps.StyledMapType [
                {
                    featureType: 'poi'
                    elementType: 'all'
                    stylers: [ visibility: "off" ]
                },
                {
                    featureType: 'road'
                    elementType: 'all'
                    stylers: [ lightness: 70 ]
                },
                {
                    featureType: 'transit'
                    elementType: 'all'
                    stylers: [ lightness: 50 ]
                },
                {
                    featureType: 'water'
                    elementType: 'all'
                    stylers: [ lightness: 50 ]
                },
                {
                    featureType: 'administrative'
                    elementType: 'labels'
                    stylers: [ lightness: 30 ]
                }
                ], name: gettext 'Clean'

        setMap: (@map) ->
            @map.googleMap.mapTypes.set @id, @mapType
            options = @map.googleMap.mapTypeControlOptions
            options.mapTypeIds.push @id
            @map.googleMap.setOptions mapTypeControlOptions: options
            @map.googleMap.setMapTypeId @id


    window.komoo.maptypes =
        CleanMapType: CleanMapType

    return window.komoo.maptypes
