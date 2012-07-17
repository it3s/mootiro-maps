window.komoo ?= {}
window.komoo.event ?= google.maps.event

class Balloon
    defaultWidth: "300px"

    constructor: (@options = {}) ->
        @width = options.width or @defaultWidth
        console.log @width
        @createInfoBox @options
        @setMap @options.map
        @customize()

    createInfoBox: (options) ->
        @setInfoBox new InfoBox
            pixelOffset: new google.maps.Size(0, -20)
            enableEventPropagation: true
            closeBoxMargin: "10px"
            disableAutoPan: true
            boxStyle:
                cursor: "pointer"
                background: "url(/static/img/infowindow-arrow.png) no-repeat 0 10px"
                width: @width

    setInfoBox: (@infoBox) ->

    setMap: (@map) ->

    open: (options = {}) ->
        if @map?.mode isnt komoo.Mode.NAVIGATE
            return
        @setContent options.content or \
            if options.features
                @createClusterContent options
            else
                @createFeatureContent options
        @feature = options.feature or options.features?[0]
        position = options.position or @feature.getCenter()
        point = komoo.utils.latLngToPoint @map, position
        point.x += 5
        newPosition = komoo.utils.pointToLatLng @map, point
        @infoBox.setPosition newPosition
        @infoBox.open(@map.googleMap or  @map)

    setContent: (content = title: "", body: "") ->
        if typeof content is "string"
            content =
                title: ""
                url: ""
                body: content
        @title.html \
            if content.url
                "<a href=\"#{content.url}\">#{content.title}</a>"
            else
                content.title
        @body.html content.body

    close: ->
        @infoBox.close()
        if @feature?.isHighlighted
            @feature.setHighlight off
        @feature = null
        @isMouseover = false

    customize: ->
        that = @
        google.maps.event.addDomListener @infoBox, "domread", (e) ->
            div = that.infoBox.div_
            google.maps.event.addDomListener div, "click", (e) ->
                e.cancelBubble = true
                e.stopPropagation?()
            google.maps.event.addDomListener div, "mouseout", (e) ->
                that.isMouseover = false

            closeBox = div.firstChild
            google.maps.event.addDomListener closeBox, "click", (e) ->
                that.close()
            google.maps.event.addDomListener closeBox, "mouseover", (e) ->
                that.isMouseover = true

            komoo.event.trigger that, "domready"

        @initDomElements()

    initDomElements: ->
        that = @
        @title = $("<div>")
        @body = $("<div>")
        @content = $("<div>").addClass "map-infowindow-content"
        @content.append @title
        @content.append @body
        @content.css {
            background: "white"
            padding: "10px"
            margin: "0 0 0 15px"
        }
        @content.hover \
            (e) -> that.isMouseover = true,
            (e) -> that.isMouseover = false
        @infoBox.setContent @content.get(0)

    createClusterContent: (options = {}) ->
        features = options.features or []
        msg = ngettext "%s Community", "%s Communities", features.length
        title = "<strong>#{interpolate msg, [features.length]}</strong>"
        body = for feature in features[0..10]
            "<li>#{feature.getProperty 'name'}</li>"
        body = "<ul>#{body.join()}</ul>"
        title: title, url: "", body: body

    createFeatureContent: (options = {}) ->
        title = ""
        feature = options.feature
        if feature
            title =
                if feature.getProperty("type") is "OrganizationBranch"
                    feature.getProperty("organization_name") + \
                        " - " + feature.getProperty("name")
                else
                    feature.getProperty "name"
        title: title, url: "", body: ""


class AjaxBalloon extends Balloon
    createFeatureContent: (options = {}) ->
        that = @
        feature = options.feature or {}

        if not feature then return
        if feature[@contentViewName] then return feature[@contentViewName]

        url = dutils.urls.resolve @contentViewName,
            zoom: @map.getZoom()
            app_label: feature.featureType.appLabel
            model_name: feature.featureType.modelName
            obj_id: feature.getProperty "id"

        $.get url, (data) ->
            feature[that.contentViewName] = data
            that.setContent data

        gettext "Loading..."


class InfoWindow extends AjaxBalloon
    defaultWidth: "350px"
    contentViewName: "info_window"

    customize: ->
        super()
        that = @
        google.maps.event.addDomListener @infoBox, "domready", (e) ->
            div = that.infoBox.div_
            google.maps.event.addDomListener div, "mousemove", (e) ->
                that.isMouseover = e.offsetX > 10 or e.toElement isnt div
                if that.isMouseover
                    e.cancelBubble = true
                    e.preventDefault?()
                    e.stopPropagation?()
                    that.map.closeTooltip()


class Tooltip extends AjaxBalloon
    contentViewName: "tooltip"

    customize: ->
        super()
        that = @
        google.maps.event.addDomListener @infoBox, "domready", (e) ->
            div = that.infoBox.div_
            google.maps.event.addDomListener div, "click", (e) ->
                that.map.openInfoWindow that.options
            closeBox = div.firstChild
            $(closeBox).hide()


window.komoo.controls =
    Balloon: Balloon
    AjaxBalloon: AjaxBalloon
    InfoWindow: InfoWindow
    Tooltip: Tooltip
    makeInfoWindow: (options) -> new InfoWindow options
    makeTooltip: (options) -> new Tooltip options
