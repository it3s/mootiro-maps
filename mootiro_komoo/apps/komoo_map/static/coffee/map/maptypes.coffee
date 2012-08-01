window.komoo ?= {}
window.komoo.event ?= google.maps.event

class CleanMapType
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

    setMap: (@map) -> @map.googleMap.mapTypes.set @id, @mapType


window.komoo.maptypes =
    CleanMapType: CleanMapType

    makeCleanMapType: -> new CleanMapType()
