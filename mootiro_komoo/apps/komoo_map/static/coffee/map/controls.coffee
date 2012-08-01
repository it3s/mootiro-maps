window.komoo ?= {}
window.komoo.event ?= google.maps.event

OVERLAY = {}
OVERLAY[komoo.geometries.types.POINT] = google.maps.drawing.OverlayType.MARKER
OVERLAY[komoo.geometries.types.MULTIPOINT] = google.maps.drawing.OverlayType.MARKER
OVERLAY[komoo.geometries.types.LINESTRING] = google.maps.drawing.OverlayType.POLYLINE
OVERLAY[komoo.geometries.types.MULTILINESTRING] = google.maps.drawing.OverlayType.POLYLINE
OVERLAY[komoo.geometries.types.POLYGON] = google.maps.drawing.OverlayType.POLYGON

EDIT = 'edit'
DELETE = 'delete'
NEW = 'new'
ADD = 'add'
CUTOUT = 'cutout'

class Box
    position: google.maps.ControlPosition.RIGHT_BOTTOM
    constructor: ->
        @box = $ "<div>"
        if @id? then @box.attr "id", @id

    setMap: (@map) ->
        @map.googleMap.controls[@position].push @box.get 0
        @handleMapEvents?()


class SupporterBox extends Box
    id: "map-supporters"

    constructor: ->
        super()
        @box.append $("#map-supporters-content").show()


class LicenseBox extends Box
    id: "map-license"
    position: google.maps.ControlPosition.BOTTOM_LEFT

    constructor: ->
        super()
        @box.html 'Este conteúdo é disponibilizado nos termos da licença <a href="http://creativecommons.org/licenses/by-sa/3.0/deed.pt_BR">Creative Commons - Atribuição - Partilha nos Mesmos Termos 3.0 Não Adaptada</a>; pode estar sujeito a condições adicionais. Para mais detalhes, consulte as Condições de Uso.'


class DrawingManager
    enabled: on

    defaultDrawingManagerOptions:
        drawingControl: false
        drawingMode: null

    componentOriginalStatus: {}

    constructor: (@options = {}) ->
        @options.drawingManagerOptions ?= @defaultDrawingManagerOptions
        if @options.map
            @setMap @options.map

    initManager: (options = @defaultDrawingManagerOptions) ->
        @manager = new google.maps.drawing.DrawingManager options
        @handleManagerEvents()

    setMap: (@map) ->
        @options.drawingManagerOptions.map = @map.googleMap
        @initManager @options.drawingManagerOptions
        @handleMapEvents()

    enable: -> @enabled = on
    disable: -> @enabled = off

    setMode: (@mode) ->
        @manager.setDrawingMode \
            if @mode in [ADD, NEW] or
                    (@mode is CUTOUT and
                     @feature.getGeometryType() is komoo.geometries.types.POLYGON)
                OVERLAY[@feature.getGeometryType()]
             else
                null
        if @mode is CUTOUT and
                @feature.getGeometryType() isnt komoo.geometries.types.POLYGON
            @mode = EDIT

    handleMapEvents: ->
        komoo.event.addListener @map, 'draw_feature', (geometryType, feature) =>
            @drawFeature(feature)

        komoo.event.addListener @map, 'edit_feature', (feature) =>
            @editFeature(feature)

        komoo.event.addListener @map, 'drawing_finished', (feature) =>
            @feature.setEditable off
            @feature.updateIcon()
            @setMode null

        komoo.event.addListener @map, 'finish_drawing', () =>
            komoo.event.trigger @map, 'drawing_finished', @feature, true

        komoo.event.addListener @map, 'cancel_drawing', () =>
            komoo.event.trigger @map, 'drawing_finished', @feature, false

        komoo.event.addListener @map, 'mode_changed', (mode) =>
            @setMode mode

    handleManagerEvents: ->
        komoo.event.addListener @manager, 'overlaycomplete', (e) =>
            path = e.overlay?.getPath?()
            if path and @mode in [ADD, NEW, CUTOUT] and e.overlay?.getPaths
                # Gets the overlays path orientation.
                paths = @feature.getGeometry().getPaths()
                if paths?.length > 0
                    # Gets the paths orientations.
                    sArea = google.maps.geometry.spherical.computeSignedArea path
                    sAreaAdded = google.maps.geometry.spherical.computeSignedArea paths.getAt(0)
                    orientation = sArea / Math.abs sArea
                    orientationAdded = sAreaAdded / Math.abs sAreaAdded
                    # Verify the paths orientation.
                    if (orientation is orientationAdded and @mode is CUTOUT) or
                            (orientation isnt orientationAdded and @mode in [ADD, NEW])
                        # Reverse path orientation to correspond to the action
                        path = new google.maps.MVCArray path.getArray().reverse()

                paths.push path
                @feature.getGeometry().setPaths paths
                # Remove the temporary overlay from map
                e.overlay.setMap null

            else if @mode in [ADD, NEW] and e.overlay.getPosition
                @feature.getGeometry().addMarker e.overlay
                @feature.updateIcon 100

            else if @mode in [ADD, NEW] and e.overlay.getPath
                @feature.getGeometry().addPolyline e.overlay, true

            @map.setMode EDIT
            @feature.setEditable on

    editFeature: (@feature) ->
        if @enabled is off then return

        @feature.setMap @map, geometry: on
        @feature.setEditable on
        options = {}
        options["#{OVERLAY[@feature.getGeometryType()]}Options"] = @feature.getGeometry().getOverlayOptions
            strokeWeight: 2.5
            zoom: 100  # Draw using the main icon
        @manager.setOptions options
        @map.setMode EDIT
        komoo.event.trigger @map, 'drawing_started', @feature

    drawFeature: (@feature) ->
        if @enabled is off then return

        @editFeature @feature
        @map.setMode NEW


class DrawingControl extends Box
    id: "map-drawing-box"
    position: google.maps.ControlPosition.TOP_LEFT

    constructor: ->
        super()
        @box.hide()
        @box.html """
        <div class="map-panel" id="drawing-control">
          <div class="map-panel-title" id="drawing-control-title"></div>
          <div class="content" id="drawing-control-content"></div>
          <div class="map-panel-buttons">
            <div class="map-button" id="drawing-control-finish">Concluir</div>
            <div class="map-button" id="drawing-control-cancel">Cancelar</div>
          </div>
        </div>
        """
        @handleBoxEvents()

    handleMapEvents: ->
        komoo.event.addListener @map, 'drawing_started', (feature) =>
            @open feature

        komoo.event.addListener @map, 'drawing_finished', (feature) =>
            @close()

        komoo.event.addListener @map, 'mode_changed', (mode) =>
            @setMode mode

    handleBoxEvents: ->
        $("#drawing-control-finish", @box).click =>
            komoo.event.trigger @map, 'finish_drawing'

        $("#drawing-control-cancel", @box).click =>
            komoo.event.trigger @map, 'cancel_drawing'

    handleButtonEvents: ->
        $("#drawing-control-add", @box).click =>
            @map.setMode if @mode isnt ADD then ADD else EDIT

        $("#drawing-control-cutout", @box).click =>
            @map.setMode if @mode isnt CUTOUT then CUTOUT else EDIT

        $("#drawing-control-delete", @box).click =>
            @map.setMode if @mode isnt DELETE then DELETE else EDIT

    setMode: (@mode) ->
        if @mode is NEW
            $("#drawing-control-content", @box).hide()
        else
            $("#drawing-control-content", @box).show()
        $(".map-button.active", @box).removeClass "active"
        $("#drawing-control-#{@mode.toLowerCase()}", @box).addClass "active"

    getTitle: ->
        if @feature.getGeometryType() is komoo.geometries.types.POLYGON
            geometry = 'polygon'
            title = gettext 'Add shape'
        else if @feature.getGeometryType() in [komoo.geometries.types.LINESTRING,
                                               komoo.geometries.types.MULTILINESTRING]
            geometry = 'linestring'
            title = gettext 'Add line'
        else if @feature.getGeometryType() in [komoo.geometries.types.POINT,

                                               komoo.geometries.types.MULTIPOINT]
            geometry = 'point'
            title = gettext 'Add point'
        """<i class="icon-#{geometry} middle"></i><span class="middle">#{title}</span>"""

    getContent: ->
        add = """<div class="map-button" id="drawing-control-add"><i class="icon-komoo-plus middle"></i><span class="middle">#{gettext 'Sum'}</span></div>"""
        cutout = """<div class="map-button" id="drawing-control-cutout"><i class="icon-komoo-minus middle"></i><span class="middle">#{gettext 'Cutout'}</span></div>"""
        remove = """<div class="map-button" id="drawing-control-delete"><i class="icon-komoo-trash middle"></i></div>"""

        content = add
        if @feature.getGeometryType() is komoo.geometries.types.POLYGON
            content += cutout
        content += remove
        content


    open: (@feature) ->
        $("#drawing-control-title", @box).html @getTitle()
        $("#drawing-control-content", @box).html @getContent()
        @handleButtonEvents()
        @box.show()

    close: -> @box.hide()


class Balloon
    defaultWidth: "300px"
    enabled: on

    constructor: (@options = {}) ->
        @width = @options.width or @defaultWidth
        @createInfoBox @options
        if @options.map
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

    handleMapEvents: ->
        komoo.event.addListener @map, 'drawing_started', (feature) =>
            @disable()

        komoo.event.addListener @map, 'drawing_finished', (feature) =>
            @enable()

    setInfoBox: (@infoBox) ->

    setMap: (@map) ->
        @handleMapEvents()

    enable: -> @enabled = on

    disable: ->
        @close(false)
        @enabled = off

    open: (@options = {}) ->
        if not @enabled then return
        @setContent options.content or \
            if options.features
                @createClusterContent options
            else
                @createFeatureContent options
        @feature = options.feature ? options.features?.getAt 0
        position = options.position ? @feature.getCenter()
        point = komoo.utils.latLngToPoint @map, position
        point.x += 5
        newPosition = komoo.utils.pointToLatLng @map, point
        @infoBox.setPosition newPosition
        @infoBox.open(@map.googleMap ? @map)

    setContent: (content = title: "", body: "") ->
        if typeof content is "string"
            content =
                title: ""
                url: ""
                body: content
        @title.html \
            if content.url
                """<a href="#{content.url}'">#{content.title}</a>"""
            else
                content.title
        @body.html content.body

    close: ->
        @isMouseover = false
        @infoBox.close()
        if @feature?.isHighlighted()
            @feature.setHighlight off
        @feature = null

    customize: ->
        google.maps.event.addDomListener @infoBox, "domread", (e) =>
            div = @infoBox.div_
            google.maps.event.addDomListener div, "click", (e) =>
                e.cancelBubble = true
                e.stopPropagation?()
            google.maps.event.addDomListener div, "mouseout", (e) =>
                @isMouseover = false


            komoo.event.trigger @, "domready"

        @initDomElements()

    initDomElements: ->
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
            (e) => @isMouseover = true,
            (e) => @isMouseover = false
        @infoBox.setContent @content.get(0)

    createClusterContent: (options = {}) ->
        features = options.features or []
        msg = ngettext "%s Community", "%s Communities", features.length
        title = "<strong>#{interpolate msg, [features.length]}</strong>"
        body = for feature in features[0..10]
            "<li>#{feature.getProperty 'name'}</li>"
        body = "<ul>#{body.join('')}</ul>"
        title: title, url: "", body: body

    createFeatureContent: (options = {}) ->
        title = ""
        feature = options.feature
        if feature
            title =
                if feature.getProperty "type" is "OrganizationBranch" \
                        and feature.getProperty "organization_name"
                    feature.getProperty("organization_name") + " - " + \
                    feature.getProperty "name"
                else
                    feature.getProperty "name"
        title: title, url: "", body: ""


class AjaxBalloon extends Balloon
    createFeatureContent: (options = {}) ->
        feature = options.feature

        if not feature then return
        if feature[@contentViewName] then return feature[@contentViewName]
        if not feature.getProperty("id")? then return super options

        url = dutils.urls.resolve @contentViewName,
            zoom: @map.getZoom()
            app_label: feature.featureType.appLabel
            model_name: feature.featureType.modelName
            obj_id: feature.getProperty "id"

        $.get url, (data) =>
            feature[@contentViewName] = data
            @setContent data

        gettext "Loading..."


class InfoWindow extends AjaxBalloon
    defaultWidth: "350px"
    contentViewName: "info_window"

    open: (options) ->
        @feature?.displayTooltip = on
        super options
        @feature?.displayTooltip = off

    close: (enableTooltip = true) ->
        @feature?.displayTooltip = on
        if enableTooltip
            @map.enableComponents 'tooltip'
        super()

    customize: ->
        super()
        google.maps.event.addDomListener @infoBox, "domready", (e) =>
            div = @content.get 0
            closeBox = @infoBox.div_.firstChild

            google.maps.event.addDomListener div, "mousemove", (e) =>
                @map.disableComponents 'tooltip'

            google.maps.event.addDomListener div, "mouseout", (e) =>
                closeBox = @infoBox.div_.firstChild
                if e.toElement isnt closeBox
                    @map.enableComponents 'tooltip'

            google.maps.event.addDomListener closeBox, "click", (e) =>
                @close()

    handleMapEvents: ->
        super()
        komoo.event.addListener @map, 'feature_click', (e, feature) =>
            setTimeout =>
                @open feature: feature, position: e.latLng
            , 200


class Tooltip extends AjaxBalloon
    contentViewName: "tooltip"

    close: ->
        clearTimeout @timer
        super()

    customize: ->
        super()
        google.maps.event.addDomListener @infoBox, "domready", (e) =>
            div = @infoBox.div_
            google.maps.event.addDomListener div, "click", (e) =>
                e.latLng = @infoBox.getPosition()
                komoo.event.trigger @map, 'feature_click', e, @feature
            closeBox = div.firstChild
            $(closeBox).hide()

    handleMapEvents: ->
        super()
        komoo.event.addListener @map, 'feature_mousemove', (e, feature) =>
            clearTimeout @timer

            if feature is @feature or not feature.displayTooltip then return

            delay = if feature.getType() is 'Community' then 400 else 10
            @timer = setTimeout =>
                if not feature.displayTooltip then return
                @open feature: feature, position: e.latLng
            , delay

        komoo.event.addListener @map, 'feature_mouseout', (e, feature) =>
            @close()

        komoo.event.addListener @map, 'feature_click', (e, feature) =>
            @close()

        komoo.event.addListener @map, 'cluster_mouseover',  (features, position) =>
            if not features.getAt(0).displayTooltip then return
            @open features: features, position: position

        komoo.event.addListener @map, 'cluster_mouseout', (e, feature) =>
            @close()

        komoo.event.addListener @map, 'cluster_click', (e, feature) =>
            @close()


class FeatureClusterer
    maxZoom: 9
    gridSize: 20
    minSize: 1
    imagePath: '/static/img/cluster/communities'
    imageSizes: [24, 29, 35, 41, 47]

    constructor: (@options = {}) ->
        @options.gridSize ?= @gridSize
        @options.maxZoom ?= @maxZoom
        @options.minimumClusterSize ?= @minSize
        @options.imagePath ?= @imagePath
        @options.imageSizes ?= @imageSizes
        @featureType = @options.featureType
        @features = []
        if @options.map
            @setMap @options.map

    initMarkerClusterer: (options = {}) ->
        map = @map?.googleMap or @map
        @clusterer = new MarkerClusterer map, [], options

    initEvents: (object = @clusterer) ->
        if not object then return

        eventsNames = ['clusteringbegin', 'clusteringend']
        eventsNames.forEach (eventName) =>
            komoo.event.addListener object, eventName, (mc) =>
                komoo.event.trigger @, eventName, @

        eventsNames = ['click', 'mouseout', 'mouseover']
        eventsNames.forEach (eventName) =>
            komoo.event.addListener object, eventName, (c) =>
                features = komoo.collections.makeFeatureCollection \
                    features: (marker.feature for marker in c.getMarkers())
                komoo.event.trigger @, eventName, features, c.getCenter()
                komoo.event.trigger @map, "cluster_#{eventName}", features, c.getCenter()

    setMap: (@map) ->
        @initMarkerClusterer @options
        @initEvents()
        @addFeatures @map.getFeatures()
        @handleMapEvents()

    handleMapEvents: ->
        komoo.event.addListener @map, 'feature_created', (feature) =>
            if feature.getType() is @featureType
                @push feature

    updateLength: -> @length = @features.length

    clear: ->
        @features = []
        @clusterer.clearMarkers()
        @updateLength()

    getAt: (index) -> @features[index]

    push: (element) ->
        if element.getMarker()
            @features.push element
            element.getMarker().setVisible off
            @clusterer.addMarker element.getMarker().getOverlay()
            @updateLength()

    pop: ->
        element = @features.pop()
        @clusterer.removeMarker element.getMarker()
        @updateLength()
        element

    forEach: (callback, thisArg) ->
        @features.forEach callback, thisArg

    repaint: -> @clusterer.repaint()

    getAverageCenter: -> @clusterer.getAverageCenter()

    addFeatures: (features) ->
        features?.forEach (feature) => @push(feature)


window.komoo.controls =
    DrawingManager: DrawingManager
    Balloon: Balloon
    AjaxBalloon: AjaxBalloon
    InfoWindow: InfoWindow
    Tooltip: Tooltip
    FeatureClusterer: FeatureClusterer
    SupporterBox: SupporterBox
    LicenseBox: LicenseBox
    makeDrawingManager: (options) -> new DrawingManager options
    makeDrawingControl: (options) -> new DrawingControl options
    makeInfoWindow: (options) -> new InfoWindow options
    makeTooltip: (options) -> new Tooltip options
    makeFeatureClusterer: (options) -> new FeatureClusterer options
    makeSupporterBox: (options) -> new SupporterBox options
    makeLicenseBox: (options) -> new LicenseBox options
