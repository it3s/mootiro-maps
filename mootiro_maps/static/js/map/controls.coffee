define (require)->
    'use strict'

    googleMaps = require 'googlemaps'
    Component = require './component'
    common = require './common'
    geometries = require './geometries'
    utils = require './utils'
    InfoBox = require 'infobox'
    MarkerClusterer = require 'markerclusterer'

    window.komoo ?= {}
    window.komoo.event ?= googleMaps.event

    # Defining translatable strings here as constantes to prevent an mysterious issue
    _NEXT_STEP = gettext 'Next Step'
    _CANCEL = gettext 'Cancel'
    _CLOSE = gettext 'Close'
    _ADD_SHAPE = gettext 'Add shape'
    _ADD_LINE = gettext 'Add line'
    _ADD_POINT = gettext 'Add point'
    _SUM = gettext 'Sum'
    _CUT_OUT = gettext 'Cut out'
    _LOADING = gettext 'Loading...'

    EMPTY = common.geometries.types.EMPTY
    POINT = common.geometries.types.POINT
    MULTIPOINT = common.geometries.types.MULTIPOINT
    POLYGON = common.geometries.types.POLYGON
    POLYLINE = common.geometries.types.LINESTRING
    LINESTRING = common.geometries.types.LINESTRING
    MULTIPOLYLINE = common.geometries.types.MULTILINESTRING
    MULTILINESTRING = common.geometries.types.MULTILINESTRING

    # Associate our geometry types to google maps types
    OVERLAY = {}
    OVERLAY[POINT] = googleMaps.drawing.OverlayType.MARKER
    OVERLAY[MULTIPOINT] = googleMaps.drawing.OverlayType.MARKER
    OVERLAY[LINESTRING] = googleMaps.drawing.OverlayType.POLYLINE
    OVERLAY[MULTILINESTRING] = googleMaps.drawing.OverlayType.POLYLINE
    OVERLAY[POLYGON] = googleMaps.drawing.OverlayType.POLYGON

    # Drawing modes
    EDIT = 'edit'
    DELETE = 'delete'
    NEW = 'new'
    ADD = 'add'
    CUTOUT = 'cutout'

    PERIMETER_SELECTION = 'perimeter_selection'

    # Generic component to add control boxes to map.
    class Box extends Component
        position: googleMaps.ControlPosition.RIGHT_BOTTOM
        init: ->
            super()
            # Create the DOM element
            @box = $ "<div>"
            if @id? then @box.attr "id", @id
            if @class? then @box.addClass @class

            # Attach the DOM to google map.
            @map.addControl @position, @box.get 0
            @handleMapEvents?()

        hide: -> @box.hide()
        show: -> @box.show()

    # Display a "loading" message while a provider component is requesting
    # features.
    class LoadingBox extends Box
        position: googleMaps.ControlPosition.TOP_CENTER
        id: 'map-loading'

        init: ->
            super()
            @requestsTotal = 0
            @requestsWaiting = 0
            @repaint()

        getPercent: ->
            return 0 if @requestsTotal is 0
            Math.round(100 * ((@requestsTotal - @requestsWaiting) / @requestsTotal))

        repaint: ->
            @box.html "#{_LOADING} #{@getPercent()}%"

        handleMapEvents: ->
            # The provider component started the requests.
            @map.subscribe 'features_request_started', =>
                @displayTimer = setTimeout =>
                    @show()
                , 500

            # A new request was initialized.
            @map.subscribe 'features_request_queued', =>
                @requestsTotal++
                @requestsWaiting++
                @repaint()

            # A request was finished.
            @map.subscribe 'features_request_unqueued', =>
                @requestsWaiting--
                @repaint()

            # All requests were finished.
            @map.subscribe 'features_request_completed', =>
                @requestsTotal = 0
                @requestsWaiting = 0
                # Display "100%" before close the loading box
                clearTimeout @displayTimer
                setTimeout =>
                    @hide()
                , 200


    # A search box where user can insert coords or an address.
    # Dependencies:
    #  * Location
    class SearchBox extends Box
        position: googleMaps.ControlPosition.TOP_RIGHT
        id: 'map-searchbox'

        init: ->
            super()
            # Use backbone to render the form.
            require ['map/views'], (Views) =>
                @view = new Views.SearchBoxView()
                @box.append @view.render().el
                @handleViewEvents()

        handleViewEvents: ->
            @view.on 'search', (location) =>
                type = location.type
                position = location.position
                @map.publish 'goto', position, yes


    # Display some supporters logos.
    class SupporterBox extends Box
        id: "map-supporters"

        init: ->
            super()
            @box.append $("#map-supporters-content").show()


    # Display our license text inside the map.
    class LicenseBox extends Box
        id: "map-license"
        position: googleMaps.ControlPosition.BOTTOM_LEFT

        init: ->
            super()
            # TODO: Add "conditions of use" link
            # TODO: i18n
            @box.html 'Este conteúdo é disponibilizado nos termos da licença <a href="http://creativecommons.org/licenses/by-sa/3.0/deed.pt_BR">Creative Commons - Atribuição - Partilha nos Mesmos Termos 3.0 Não Adaptada</a>; pode estar sujeito a condições adicionais. Para mais detalhes, consulte as Condições de Uso.'


    # Control the drawing feature. This is a very important component.
    # See also:
    #  * DrawingControl
    #  * GeometrySelector
    class DrawingManager extends Component
        enabled: on

        defaultDrawingManagerOptions:
            drawingControl: false
            drawingMode: null

        componentOriginalStatus: {}

        init: (@options = {}) ->
            @options.drawingManagerOptions ?= @defaultDrawingManagerOptions
            @setMap @options.map if @options.map

        initManager: (options = @defaultDrawingManagerOptions) ->
            @manager = new googleMaps.drawing.DrawingManager options
            @handleManagerEvents()

        setMap: (@map) ->
            @options.drawingManagerOptions.map = @map.googleMap
            @initManager @options.drawingManagerOptions
            @handleMapEvents()

        enable: -> @enabled = on
        disable: -> @enabled = off

        setMode: (@mode) ->
            # Set the correct mode to google drawing manager according to our
            # internal mode and geometry type.
            @manager.setDrawingMode \
                if @mode in [ADD, NEW] or
                        (@mode is CUTOUT and
                         @feature.getGeometryType() is POLYGON)
                    OVERLAY[@feature.getGeometryType()]
                 else
                    null
            if @mode is CUTOUT and @feature.getGeometryType() isnt POLYGON
                @mode = EDIT

        handleMapEvents: ->
            @map.subscribe 'draw_feature', (geometryType, feature) =>
                @drawFeature(feature)

            @map.subscribe 'edit_feature', (feature) =>
                @editFeature(feature)

            @map.subscribe 'drawing_finished', (feature) =>
                @feature.setEditable off
                @feature.updateIcon()
                @setFeature null
                @setMode null

            @map.subscribe 'finish_drawing', =>
                @map.publish 'drawing_finished', @feature, true

            @map.subscribe 'cancel_drawing', =>
                @map.publish 'drawing_finished', @feature, false

            @map.subscribe 'mode_changed', (mode) =>
                @setMode mode

            @map.subscribe 'feature_rightclick', (e, feature) =>
                # Delete the vertex on right click.
                if not e.vertex? then return
                # Rightclick on vertex removes it
                overlay = feature.getGeometry().getOverlay()
                paths = overlay.getPaths?()
                path = paths?.getAt(e.path)
                path?.removeAt e.vertex
                # Removes the path is there is only one vertex
                if path?.getLength() is 1
                    paths.removeAt e.path

        handleManagerEvents: ->
            komoo.event.addListener @manager, 'overlaycomplete', (e) =>
                #
                # The user finished the draw.
                #
                path = e.overlay?.getPath?()

                # We got a polygon.
                if path and @mode in [ADD, NEW, CUTOUT] and e.overlay?.getPaths
                    # Gets the overlays path orientation.
                    # The orientation is used to add another path or add
                    # holes to polygons
                    paths = @feature.getGeometry().getPaths()
                    if @mode is NEW then paths.clear()
                    if paths?.length > 0
                        # Gets the paths orientations.
                        sArea = googleMaps.geometry.spherical.computeSignedArea path
                        sAreaAdded = googleMaps.geometry.spherical.computeSignedArea paths.getAt 0
                        orientation = sArea / Math.abs sArea
                        orientationAdded = sAreaAdded / Math.abs sAreaAdded
                        # Verify the paths orientation.
                        if (orientation is orientationAdded and @mode is CUTOUT) or
                                (orientation isnt orientationAdded and @mode in [ADD, NEW])
                            # Reverse path orientation to correspond to the action
                            path = new googleMaps.MVCArray path.getArray().reverse()

                    paths.push path
                    # Update the feature geometry.
                    @feature.getGeometry().setPaths paths
                    # Remove the temporary overlay from map
                    e.overlay.setMap null

                # We got a marker.
                else if @mode in [ADD, NEW] and e.overlay.getPosition
                    @feature.getGeometry().addMarker e.overlay
                    @feature.updateIcon 100

                # We got a line.
                else if @mode in [ADD, NEW] and e.overlay.getPath
                    @feature.getGeometry().addPolyline e.overlay, true

                @map.setMode EDIT
                @feature?.setEditable on

        setFeature: (@feature) ->
            komoo.event.removeListener @featureClickListener if @featureClickListener?

            return if not @feature?

            @feature.setMap @map, geometry: on
            @featureClickListener = komoo.event.addListener @feature, 'click', (e, o) =>
                # The user activated the "delete" mode than clicked on editable
                # elemente on the map.
                if @mode is DELETE
                    # Delete clicked stuff

                    # Delete the polygons path the user clicked on.
                    if @feature.getGeometryType() is POLYGON
                        paths = @feature.getGeometry().getPaths()
                        paths.forEach (path, index) =>
                            # Delete the correct path.
                            if utils.isPointInside e.latLng, path
                                paths.removeAt index

                    # Delete the marker the user clicked on.
                    else if o and @feature.getGeometryType() is MULTIPOINT
                        markers = @feature.getGeometry().getMarkers()
                        index = $.inArray o, markers.getArray()
                        if index > -1
                            marker = markers.removeAt index
                            marker.setMap null

                    # Delete the line the user clicked on.
                    else if o and @feature.getGeometryType() is MULTILINESTRING
                        polylines = @feature.getGeometry().getPolylines()
                        index = $.inArray o, polylines.getArray()
                        if index > -1
                            polyline = polylines.removeAt index
                            polyline.setMap null

                    @map.setMode EDIT

        editFeature: (feature) ->
            return if @enabled is off

            @setFeature feature

            # Ask user to select the geometry type if trying to edit an empty
            # feature.
            if @feature.getGeometryType() is 'Empty'
                @map.publish 'select_new_geometry', @feature
                return

            @feature.setEditable on

            # Set the correct options to google drawing manager to be consistent
            # with the type of the feature we are editing.
            options = {}
            options["#{OVERLAY[@feature.getGeometryType()]}Options"] = @feature.getGeometry().getOverlayOptions
                strokeWeight: 2.5
                zoom: 100  # Draw using the main icon
            @manager.setOptions options
            @map.setMode EDIT
            @map.publish 'drawing_started', @feature

        drawFeature: (@feature) ->
            return if @enabled is off

            @editFeature @feature
            @map.setMode NEW

    # Display a box with "close" button
    class CloseBox extends Box
        id: "map-drawing-box"
        class: "map-panel"
        position: googleMaps.ControlPosition.TOP_LEFT

        init: (opt = { title: '' }) ->
            super()
            title = opt.title ? ''
            @box.html """
            <div id="drawing-control">
              <div class="map-panel-title" id="drawing-control-title">#{title}</div>
              <div class="content" id="drawing-control-content"></div>
              <div class="map-panel-buttons">
                <div class="map-button" id="drawing-control-cancel">#{_CLOSE}</div>
              </div>
            </div>
            """
            @show()
            @handleButtonEvents()

        setTitle: (title = '') ->
            @box.find('#drawing-control-title').text title

        handleButtonEvents: ->
            $("#drawing-control-cancel", @box).click =>
                @map.publish 'close_clicked'


    # Display a box to user select the geometry type he want to draw.
    # This listen the "select_new_geometry" to open the box.
    # Designed to be used with `DrawingManager`
    class GeometrySelector extends Box
        id: "map-drawing-box"
        class: "map-panel"
        position: googleMaps.ControlPosition.TOP_LEFT

        init: ->
            super()
            @hide()
            #TODO: i18n
            @box.html """
            <div id="geometry-selector">
              <div class="map-panel-title" id="drawing-control-title"></div>
              <ul class="content" id="drawing-control-content">
                <li class="polygon btn" data-geometry-type="Polygon">
                  <i class="icon-polygon middle"></i><span class="middle">Adicionar área</span>
                </li>
                <li class="linestring btn" data-geometry-type="LineString">
                  <i class="icon-linestring middle"></i><span class="middle">Adicionar linha</span>
                </li>
                <li class="point btn" data-geometry-type="Point">
                  <i class="icon-point middle"></i><span class="middle">Adicionar ponto</span>
                </li>
              </ul>
              <div class="map-panel-buttons">
                <div class="map-button" id="drawing-control-cancel">#{_CANCEL}</div>
              </div>
            </div>
            """
            @handleBoxEvents()

        handleMapEvents: ->
            @map.subscribe 'select_new_geometry', (feature) =>
                @open feature

        handleBoxEvents: ->
            @box.find('li').each (i, element) =>
                $element = $(element)
                geometryType = $element.attr 'data-geometry-type'
                $element.click () =>
                    @close()
                    @map.editFeature @feature, geometryType

        handleButtonEvents: ->
            $("#drawing-control-cancel", @box).click =>
                @map.publish 'cancel_drawing'

        showContent: () ->
            @box.find('li').hide()
            for geometryType in @feature.getFeatureType()?.geometryTypes
                @box.find("li.#{geometryType.toLowerCase()}").show()

        open: (@feature) ->
            @showContent()
            $("#drawing-control-title", @box).html 'Selecione o tipo de objeto'
            @handleButtonEvents()
            @show()

        close: -> @hide()


    # Display the drawing controls whe the map enters the edit mode.
    # Designed to be used with `DrawingManager`
    class DrawingControl extends Box
        id: "map-drawing-box"
        class: "map-panel"
        position: googleMaps.ControlPosition.TOP_LEFT

        init: ->
            super()
            @hide()
            @box.html """
            <div id="drawing-control">
              <div class="map-panel-title" id="drawing-control-title"></div>
              <div class="content" id="drawing-control-content"></div>
              <div class="map-panel-buttons">
                <div class="map-button" id="drawing-control-finish">#{_NEXT_STEP}</div>
                <div class="map-button" id="drawing-control-cancel">#{_CANCEL}</div>
              </div>
            </div>
            """
            @handleBoxEvents()

        handleMapEvents: ->
            @map.subscribe 'drawing_started', (feature) =>
                @open feature

            @map.subscribe 'drawing_finished', (feature) =>
                @close()

            @map.subscribe 'mode_changed', (mode) =>
                @setMode mode

        handleBoxEvents: ->
            $("#drawing-control-finish", @box).click =>
                return if $("#drawing-control-finish", @box).hasClass 'disabled'

                @map.publish 'finish_drawing'

            $("#drawing-control-cancel", @box).click =>
                @map.publish 'cancel_drawing'

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
                $("#drawing-control-finish", @box).addClass 'disabled'
            else
                $("#drawing-control-content", @box).show()
                $("#drawing-control-finish", @box).removeClass 'disabled'
            $(".map-button.active", @box).removeClass "active"
            $("#drawing-control-#{@mode?.toLowerCase()}", @box).addClass "active"

        getTitle: ->
            if @feature.getGeometryType() is POLYGON
                geometry = 'polygon'
                title = _ADD_SHAPE
            else if @feature.getGeometryType() in [LINESTRING, MULTILINESTRING]
                geometry = 'linestring'
                title = _ADD_LINE
            else if @feature.getGeometryType() in [POINT, MULTIPOINT]
                geometry = 'point'
                title = _ADD_POINT
            """<i class="icon-#{geometry} middle"></i><span class="middle">#{title}</span>"""

        getContent: ->
            add = $("""<div class="map-button" id="drawing-control-add"><i class="icon-komoo-plus middle"></i><span class="middle">#{_SUM}</span></div>""")
            cutout = $("""<div class="map-button" id="drawing-control-cutout"><i class="icon-komoo-minus middle"></i><span class="middle">#{_CUT_OUT}</span></div>""")
            remove = $("""<div class="map-button" id="drawing-control-delete"><i class="icon-komoo-trash middle"></i></div>""")

            content = $("<div>").addClass @feature.getGeometryType().toLowerCase()
            content.append add if @feature.getGeometryType() isnt POINT
            content.append cutout if @feature.getGeometryType() is POLYGON
            content.append remove if @feature.getGeometryType() isnt POINT
            content


        open: (@feature) ->
            $("#drawing-control-title", @box).html @getTitle()
            $("#drawing-control-content", @box).html @getContent()
            @handleButtonEvents()
            @show()

        close: -> @hide()


    # Allows the selection of a center point and then draws a circle around it.
    class PerimeterSelector extends Component
        enabled: on

        init: ->
            super()
            @circle = new googleMaps.Circle
                visible: true
                radius: 100
                fillColor: "white"
                fillOpacity: 0.0
                strokeColor: "#ffbda8"
                zIndex: -1
            @marker = new googleMaps.Marker
                icon: '/static/img/marker.png'

            komoo.event.addListener @circle, 'click', (e) =>
                if @map.mode is PERIMETER_SELECTION then @selected e.latLng

        select: (@radius, @callback) ->
            if not @enabled then return
            @origMode = @map.mode
            @map.disableComponents 'infoWindow'
            @map.setMode PERIMETER_SELECTION

        selected: (latLng) ->
            @circle.setRadius @radius if typeof @radius is "number"
            @callback latLng, @circle if typeof @callback is "function"

            @circle.setCenter latLng
            @circle.setMap @map.googleMap

            @marker.setPosition latLng
            @marker.setMap @map.googleMap

            @map.publish 'perimeter_selected', latLng, @circle

            @map.setMode @origMode
            @map.enableComponents 'infoWindow'

        handleMapEvents: ->
            @map.subscribe 'select_perimeter', (radius, callback) =>
                @select radius, callback

            for eventName in ['click', 'feature_click']
                @map.subscribe eventName, (e) =>
                    if @map.mode is PERIMETER_SELECTION then @selected e.latLng

        setMap: (@map) ->
            @handleMapEvents()

        enable: -> @enabled = on

        disable: ->
            @hide()
            @enabled = off


    # Display a balloon with informations from a feature.
    class Balloon extends Component
        defaultWidth: "300px"
        enabled: on

        init: (@options = {}) ->
            super()
            @width = @options.width or @defaultWidth
            @createInfoBox @options
            if @options.map
                @setMap @options.map
            @customize()

        createInfoBox: (options) ->
            @setInfoBox new InfoBox
                pixelOffset: new googleMaps.Size(0, -20)
                enableEventPropagation: true
                closeBoxMargin: "10px"
                disableAutoPan: true
                boxStyle:
                    cursor: "pointer"
                    background: "url(/static/img/infowindow-arrow.png) no-repeat 0 10px"
                    width: @width

        handleMapEvents: ->
            @map.subscribe 'drawing_started', (feature) =>
                @disable()

            @map.subscribe 'drawing_finished', (feature) =>
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
            @setContent @options.content or \
                if @options.features
                    @createClusterContent @options
                else
                    @createFeatureContent @options
            @feature = @options.feature ? @options.features?.getAt 0
            position = @options.position ? @feature.getCenter()
            if position instanceof Array
                empty = new komoo.geometries.Empty()  # WTF?!!? TODO: Move getLatLngFromArray to utils
                position = empty.getLatLngFromArray position
            point = utils.latLngToPoint @map, position
            point.x += 5
            newPosition = utils.pointToLatLng @map, point
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
            googleMaps.event.addDomListener @infoBox, "domready", (e) =>
                div = @infoBox.div_
                googleMaps.event.addDomListener div, "click", (e) =>
                    e.cancelBubble = true
                    e.stopPropagation?()
                googleMaps.event.addDomListener div, "mouseout", (e) =>
                    @isMouseover = false


                komoo.event.trigger this, "domready"

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
                    feature.getProperty "name"
            title: title, url: "", body: ""


    # Extends the `Balloon` component, but get the feature informations from
    # the server.
    class AjaxBalloon extends Balloon
        createFeatureContent: (options = {}) ->
            feature = options.feature

            return if not feature
            return feature[@contentViewName] if feature[@contentViewName]
            return super options if not feature.getProperty("id")?

            url = dutils.urls.resolve @contentViewName,
                zoom: @map.getZoom()
                app_label: feature.featureType.appLabel
                model_name: feature.featureType.modelName
                obj_id: feature.getProperty "id"

            $.get url, (data) =>
                feature[@contentViewName] = data
                @setContent data

            _LOADING


    # A balloon with clickable areas and more detailed informations.
    class InfoWindow extends AjaxBalloon
        defaultWidth: "350px"
        contentViewName: "info_window"

        open: (options) ->
            @feature?.displayTooltip = on
            super options
            @feature?.displayTooltip = off

        close: (enableTooltip = true) ->
            @feature?.setHighlight off
            @feature?.displayTooltip = on
            @map.enableComponents 'tooltip' if enableTooltip
            super()

        customize: ->
            super()
            googleMaps.event.addDomListener @infoBox, "domready", (e) =>
                div = @content.get 0
                closeBox = @infoBox.div_.firstChild

                googleMaps.event.addDomListener div, "mousemove", (e) =>
                    @map.disableComponents 'tooltip'

                googleMaps.event.addDomListener div, "mouseout", (e) =>
                    closeBox = @infoBox.div_.firstChild
                    @map.enableComponents 'tooltip' if e.toElement isnt closeBox

                googleMaps.event.addDomListener closeBox, "click", (e) =>
                    @close()

        handleMapEvents: ->
            super()
            @map.subscribe 'feature_click', (e, feature) =>
                setTimeout =>
                    @open feature: feature, position: e.latLng
                , 200
            @map.subscribe 'feature_highlight_changed', (e, feature) =>
                if feature.isHighlighted()
                    @open feature: feature


    # A balloon displayed when the mouseover event is trigged.
    class Tooltip extends AjaxBalloon
        contentViewName: "tooltip"

        close: ->
            clearTimeout @timer
            super()

        customize: ->
            super()
            googleMaps.event.addDomListener @infoBox, "domready", (e) =>
                div = @infoBox.div_
                googleMaps.event.addDomListener div, "click", (e) =>
                    e.latLng = @infoBox.getPosition()
                    @map.publish 'feature_click', e, @feature
                closeBox = div.firstChild
                $(closeBox).hide()

        handleMapEvents: ->
            super()
            @map.subscribe 'feature_mousemove', (e, feature) =>
                clearTimeout @timer

                return if feature is @feature or not feature.displayTooltip

                delay = if feature.getType() is 'Community' then 400 else 10
                @timer = setTimeout =>
                    return if not feature.displayTooltip
                    @open feature: feature, position: e.latLng
                , delay

            @map.subscribe 'feature_mouseout', (e, feature) =>
                @close()

            @map.subscribe 'feature_click', (e, feature) =>
                @close()

            @map.subscribe 'cluster_mouseover',  (features, position) =>
                return if not features.getAt(0)?.displayTooltip
                @open features: features, position: position

            @map.subscribe 'cluster_mouseout', (e, feature) =>
                @close()

            @map.subscribe 'cluster_click', (e, feature) =>
                @close()


    # Create feature clusters.
    class FeatureClusterer extends Component
        enabled: on
        maxZoom: 9
        gridSize: 20
        minSize: 1
        imagePath: '/static/img/cluster/communities'
        imageSizes: [24, 29, 35, 41, 47]
        hooks:
            'before_feature_setVisible': 'beforeFeatureSetVisibleHook'

        beforeFeatureSetVisibleHook: (feature, visible) ->
            return [feature, visible] if @map.getProjectId()?
            [feature, visible and @map.getZoom() > @maxZoom]

        init: (@options = {}) ->
            @options.gridSize ?= @gridSize
            @options.maxZoom ?= @maxZoom
            @options.minimumClusterSize ?= @minSize
            @options.imagePath ?= @imagePath
            @options.imageSizes ?= @imageSizes
            @featureType = @options.featureType
            @features = []
            window.c = this

        initMarkerClusterer: (options = {}) ->
            map = @map?.googleMap or @map
            window.clusterer = @clusterer = new MarkerClusterer map, [], options

        initEvents: (object = @clusterer) ->
            if not object then return

            eventsNames = ['clusteringbegin', 'clusteringend']
            eventsNames.forEach (eventName) =>
                komoo.event.addListener object, eventName, (mc) =>
                    komoo.event.trigger this, eventName, this

            eventsNames = ['click', 'mouseout', 'mouseover']
            eventsNames.forEach (eventName) =>
                komoo.event.addListener object, eventName, (c) =>
                    features = komoo.collections.makeFeatureCollection \
                        features: (marker.feature for marker in c.getMarkers())
                    komoo.event.trigger this, eventName, features, c.getCenter()
                    @map.publish "cluster_#{eventName}", features, c.getCenter()

        setMap: (@map) ->
            @initMarkerClusterer @options
            @initEvents()
            @handleMapEvents()

        handleMapEvents: ->
            @map.subscribe 'feature_created', (feature) =>
                if @map.getZoom() <= @maxZoom and \
                   (not @featureType? or feature.getType() is @featureType)
                    @push feature

            @map.subscribe 'idle features_loaded', =>
                if @map.getZoom() <= @maxZoom
                    @addFeatures @map.getFeatures() if @length is 0
                    @repaint()

            @map.subscribe 'features_request_completed', =>
                if @map.getZoom() <= @maxZoom
                    features = @map.getFeatures()
                    @addFeatures features

            komoo.event.addListener this, 'clusteringend', (mc) =>
                if @map.getZoom() > @maxZoom
                    @map.features.forEach (feature) ->
                        feature.marker?.setMap null

        updateLength: -> @length = @features.length

        clear: ->
            @features = []
            @clusterer.clearMarkers()
            @updateLength()

        getAt: (index) -> @features[index]

        push: (feature) ->
            return if @map.getProjectId()?
            if feature.getMarker()
                @features.push feature
                feature.getMarker().setVisible true
                @clusterer.addMarker feature.getMarker().getOverlay().markers_.getAt(0), true
                @updateLength()

        pop: ->
            feature = @features.pop()
            @clusterer.removeMarker feature.getMarker().getOverlay().markers_.getAt(0)
            @updateLength()
            feature

        forEach: (callback, thisArg) ->
            for feature in @features
                callback.apply(thisArg, feature)

        repaint: -> @clusterer.repaint()

        getAverageCenter: -> @clusterer.getAverageCenter()

        addFeatures: (features) ->
            features?.forEach (feature) => @push(feature)
            @repaint()

    class CommunityClusterer extends FeatureClusterer
        push: (feature) ->
            if feature.featureType is @map.featureTypes['Community']
                super feature


    # Handle the location requests, including the user location and the
    # coords of a specific query, using google geocode service.
    class Location extends Component
        enabled: on

        init: ->
            @geocoder = new googleMaps.Geocoder()
            @marker = new googleMaps.Marker
                icon: '/static/img/marker.png'

        handleMapEvents: ->
            @map.subscribe 'goto', (position, marker) =>
                @goTo position, marker
            @map.subscribe 'goto_user_location', =>
                @goToUserLocation()

        goTo: (position, marker = false) ->
            _go = (latLng) =>
                if latLng
                    @map.googleMap.panTo latLng
                    if marker then @marker.setPosition latLng

            if typeof position is "string"  # Got an address
                request = {
                    address: position
                    region: this.region
                }
                @geocoder.geocode request, (result, status_) =>
                    if status_ is googleMaps.GeocoderStatus.OK
                        first_result = result[0]
                        latLng = first_result.geometry.location
                        _go latLng
            else
                latLng =
                    if position instanceof Array
                        if position.length is 2
                            new googleMaps.LatLng position[0], position[1]
                    else
                        position
                _go latLng

        goToUserLocation: ->
            clientLocation = google.loader.ClientLocation
            if clientLocation
                pos = new googleMaps.LatLng clientLocation.latitude,
                                             clientLocation.longitude
                @map.googleMap.setCenter pos
                console?.log 'Getting location from Google...'
            if navigator.geolocation
                navigator.geolocation.getCurrentPosition (position) =>
                    pos = new googleMaps.LatLng position.coords.latitude,
                                                 position.coords.longitude
                    @map.googleMap.setCenter pos
                    console?.log 'Getting location from navigator.geolocation...'
                , =>
                    console?.log 'User denied access to navigator.geolocation...'

        setMap: (@map) ->
            @marker.setMap @map.googleMap
            @handleMapEvents()

        enable: -> @enabled = on

        disable: ->
            @close(false)
            @enabled = off


    # Save the location displayed on map into a cookie to be possible display
    # the same location when the user come back later.
    class SaveLocation extends Location
        handleMapEvents: ->
            super()
            @map.subscribe 'save_location', (center, zoom) =>
                @saveLocation center, zoom
            @map.subscribe 'goto_saved_location', =>
                @goToSavedLocation()

        saveLocation: (center = @map.googleMap.getCenter(), zoom = @map.getZoom()) ->
            #console?.log 'Location saved:', center.toUrlValue()
            utils.createCookie 'lastLocation', center.toUrlValue(), 90
            utils.createCookie 'lastZoom', zoom, 90

        goToSavedLocation: ->
            lastLocation = utils.readCookie 'lastLocation'
            zoom = parseInt utils.readCookie('lastZoom'), 10
            if lastLocation and zoom
                console?.log 'Getting location from cookie...'
                @map.publish 'set_location', lastLocation
                @map.publish 'set_zoom', zoom


    # Saves the current location automatically.
    class AutosaveLocation extends SaveLocation
        handleMapEvents: ->
            super()
            @map.subscribe 'idle', =>
                @saveLocation()


    # Save the map type selected by the user.
    class SaveMapType extends Component
        setMap: (@map) ->
            @handleMapEvents()
            mapTypeId = @getSavedMapType()
            if mapTypeId in _.values googleMaps.MapTypeId
                @useSavedMapType()

        handleMapEvents: ->
            @map.subscribe 'maptype_loaded', (mapTypeId) =>
                @map.googleMap.setMapTypeId mapTypeId if mapTypeId is @getSavedMapType()
            @map.subscribe 'initialized', =>
                @useSavedMapType()

        saveMapType: (mapTypeId = @map.getMapTypeId()) ->
            #console?.log 'Maptype saved:', mapTypeId
            utils.createCookie 'mapTypeId', mapTypeId, googleMaps.MapTypeId.ROADMAP

        getSavedMapType: ->
            utils.readCookie 'mapTypeId' or googleMaps.MapTypeId.ROADMAP

        useSavedMapType: ->
            mapTypeId = @getSavedMapType()
            console?.log 'Getting map type from cookie...'
            @map.googleMap.setMapTypeId mapTypeId


    # Save the map type automatically.
    class AutosaveMapType extends SaveMapType
        handleMapEvents: ->
            super()
            @map.subscribe 'maptypeid_changed', =>
                @saveMapType()


    # Split the map canvas to display the street view and the map side by side.
    class StreetView extends Component
        enabled: on

        init: ->
            console?.log "Initializing StreetView support."
            @streetViewPanel = $("<div>").addClass "map-panel"
            @streetViewPanel.height("100%").width("50%")
            @streetViewPanel.hide()
            @createObject()

        setMap: (@map) ->
            @map.googleMap.controls[googleMaps.ControlPosition.TOP_LEFT].push(
                    this.streetViewPanel.get 0)
            if @streetView? then @map.googleMap.setStreetView @streetView

        createObject: ->
            options =
                enableCloseButton: true
                visible: false
            @streetView = new googleMaps.StreetViewPanorama \
                    this.streetViewPanel.get(0), options
            @map?.googleMap.setStreetView @streetView
            googleMaps.event.addListener @streetView, "visible_changed", =>
                if @streetView.getVisible()
                    @streetViewPanel.show()
                else
                    @streetViewPanel.hide()
                @map.refresh()


    class FeatureFilter extends Component
        hooks:
            'before_feature_setVisible': 'beforeFeatureSetVisibleHook'

        init: ->
            @handleMapEvents?()

        beforeFeatureSetVisibleHook: (feature, visible) ->
            [feature, visible]


    class FeatureZoomFilter extends FeatureFilter
        hooks:
            'before_feature_setVisible': 'beforeFeatureSetVisibleHook'

        beforeFeatureSetVisibleHook: (feature, visible) ->
            return [feature, visible] if @map.getProjectId()?
            zoom = @map.getZoom()
            visible_ = visible and (
                (feature.featureType.minZoomPoint <= zoom and
                 feature.featureType.maxZoomPoint >= zoom) or
                (feature.featureType.minZoomGeometry <= zoom and
                 feature.featureType.maxZoomGeometry >= zoom)
            )
            [feature, visible_]

    class FeatureTypeFilter extends FeatureFilter
        hooks:
            'before_feature_setVisible': 'beforeFeatureSetVisibleHook'

        init: ->
            super()
            @disabled = ['User']

        beforeFeatureSetVisibleHook: (feature, visible) ->
            visible_ = visible
            if visible and feature.featureType.type in @disabled
                visible_ = false
            [feature, visible_]

        handleMapEvents: ->
            @map.subscribe 'hide_features_by_type', (type, categories, strict) =>
                @disabled.push(type) if type not in @disabled

            @map.subscribe 'show_features_by_type', (type, categories, strict) =>
                if type in @disabled
                    index = _.indexOf(@disabled, type)
                    @disabled.splice(index, 1)

    window.komoo.controls =
        DrawingManager: DrawingManager
        DrawingControl: DrawingControl
        GeometrySelector: GeometrySelector
        Balloon: Balloon
        AjaxBalloon: AjaxBalloon
        InfoWindow: InfoWindow
        Tooltip: Tooltip
        FeatureClusterer: FeatureClusterer
        CommunityClusterer: CommunityClusterer
        CloseBox: CloseBox
        LoadingBox: LoadingBox
        SupporterBox: SupporterBox
        LicenseBox: LicenseBox
        SearchBox: SearchBox
        PerimeterSelector: PerimeterSelector
        Location: Location
        SaveLocation: SaveLocation
        AutosaveLocation: AutosaveLocation
        SaveMapType: SaveMapType
        AutosaveMapType: AutosaveMapType
        StreetView: StreetView
        FeatureFilter: FeatureFilter
        FeatureZoomFilter: FeatureZoomFilter
        FeatureTypeFilter: FeatureTypeFilter

    return window.komoo.controls
