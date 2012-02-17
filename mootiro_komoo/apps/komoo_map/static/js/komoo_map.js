/**
 * View, create and edit regions on Google Maps.
 *
 * @name map.js
 * @fileOverview A simple way to use Google Maps.
 * @version 0.1.0a
 * @author Luiz Armesto
 * @copyright (c) 2012 it3s
 */

/** @namespace */
var komoo = {};

/**
 * Array of Types to populate the 'Add' tab of main panel.
 */
komoo.OverlayTypes = [
    {
        type: 'community',
        title: 'Comunidade',
        color: '#ff0',
        icon: '',
        formURL: '/community/new' // TODO: Dont use hardcoded urls
    },
    {
        type: 'need',
        title: 'Necessidade',
        color: '#f00',
        icon: '',
        formUrl: '',
        disabled: true
    },
    {
        type: 'organization',
        title: 'Organização',
        color: '#00f',
        icon: '',
        formUrl: '',
        disabled: true
    },
    {
        type: 'resource',
        title: 'Recurso',
        color: '#fff',
        icon: '',
        formUrl: '',
        disabled: true
    },
    {
        type: 'financing',
        title: 'Financiamento',
        color: '#000',
        icon: '',
        formUrl: '',
        disabled: true
    }
];

/**
 * Options object to {@link komoo.Map}.
 *
 * @namespace
 * @property {boolen} [editable=true]
 *           Define if the drawing feature will be enabled.
 * @property {boolean} [useGeoLocation=false]
 *           Define if the HTML5 GeoLocation will be used to set the initial location.
 * @property {boolean} [defaultDrawingControl=false]
 *           If true the controls from Google Drawing library are used.
 * @property {Object} overlayOptions
 * @property {google.maps.MapOptions} googleMapOptions The Google Maps map options.
 */
komoo.MapOptions = {
    editable: true,
    useGeoLocation: false,
    defaultDrawingControl: false,
    overlayTypes: komoo.OverlayTypes,
    overlayOptions: {
        fillColor: '#ff0',
        fillOpacity: 0.45,
        strokeColor: '#ff0',
        strokeWeight: 3,
        strokeOpacity: 0.45
    },
    googleMapOptions: {
        center: new google.maps.LatLng(-23.55, -46.65),  // São Paulo, SP - Brasil
        zoom: 13,
        mapTypeId: google.maps.MapTypeId.SATELLITE,
        streetViewControl: false,
        panControlOptions: {position: google.maps.ControlPosition.RIGHT_TOP},
        zoomControlOptions: {position: google.maps.ControlPosition.RIGHT_TOP}
    }
};

/**
 * Wrapper for Google Maps map object with some helper methods.
 *
 * @class
 * @param {DOM} element The map canvas.
 * @param {komoo.MapOptions} options The options object.
 * @property {komoo.MapOptions} options
 *           The options object used to construct the komoo.Map object.
 * @property {google.maps.Polygon[]|google.maps.Polyline[]} overlays
 *           Array containing all overlays.
 * @property {google.maps.Polygon[]|google.maps.Polyline[]} newOverlays
 *           Array containing new overlays added by user.
 * @property {google.maps.Map} googleMap The Google Maps map object.
 * @property {google.maps.drawing.DrawingManager} drawingManager
 *           Drawing manager from Google Maps library.
 * @property {boolean} editable The status of the drawing feature.
 * @property {google.maps.Geocoder} geocoder
 *           Google service to get addresses locations.
 * @property {JQuery} editToolbar JQuery selector of edit toolbar.
 * @property {String} editMode The current mode of edit feature.
 *           Possible values are 'cutout', 'add' and 'delete'.
 * @property {JQuery} streetViewPanel JQuery selector of Street View panel.
 * @property {google.maps.StreetViewPanorama} streetView
 * @property {JQuery} event
 * @property {google.maps.Circle} radiusCircle
 * @property {Object} overlayOptions
 */
komoo.Map = function (element, options) {
    var komooMap = this;

    if (typeof options !== 'object') options = {};
    var googleMapOptions = $.extend(
            komoo.MapOptions.googleMapOptions, options.googleMapOptions)
    // TODO: init overlay options
    options = $.extend(komoo.MapOptions, options);

    komooMap.options = options;
    komooMap.drawingManagerOptions = {};
    komooMap.overlayOptions = {};
    komooMap.overlays = [];
    komooMap.newOverlays = [];

    komooMap.event = $('<div>');

    /* Creates the Google Maps object */
    komooMap.googleMap = new google.maps.Map(element, googleMapOptions);

    komooMap.editToolbar = $('<div>').addClass('map-toolbar').css('margin', '5px');

    /* Adds drawing manager */
    komooMap.setEditable(options.editable);

    /* Draw our custom control */
    if (!options.defaultDrawingControl) {
        /* Adds new HTML element to the map */
        komooMap.mainPanel = komooMap._createMainPanel();
        komooMap.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
                komooMap.mainPanel.get(0));
        komooMap.addPanel = komooMap._createAddPanel();
        komooMap.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
                komooMap.addPanel.get(0));
        /* Adds editor toolbar */
        //komooMap.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
        //        komooMap.editToolbar.get(0));
    }

    komooMap.streetViewPanel = $('<div>').addClass('map-panel');
    komooMap.googleMap.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(
            komooMap.streetViewPanel.get(0));
    komooMap.streetViewPanel.hide();

    var controlSelector = $('<div>Komoo</div>').addClass('map-button');
    controlSelector.bind('click', function() {
        if (window.console) console.log('Clicked on "The Incredible Komoo" DIV');
        komooMap.setStreetView(true);
    });
    //komooMap.googleMap.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(
    //        controlSelector.get(0));

    /* Uses HTML5 Geo Location */
    if (options.useGeoLocation) komooMap.goToUserLocation();

    /* Listen Google Maps map events */
    google.maps.event.addListener(komooMap.googleMap, 'click', function(e) {
        if (komooMap.addPanel.is(':hidden')) {
            komooMap.setCurrentOverlay(null);  // Remove the overlay selection
        }
        komooMap._emit_mapclick(e)
    });

    /* Adds GeoCoder */
    komooMap.geocoder = new google.maps.Geocoder();

    if (komoo.onMapReady) komoo.onMapReady(komooMap);
}

komoo.Map.prototype = {
    /**
     * Load the features from geoJSON into the map.
     * @param {json} geoJSON The json that will be loaded.
     * @param {boolean} panTo If true pan to the region where overlays are.
     * @returns {void}
     */
    loadGeoJSON: function (geoJSON, panTo) {
        // TODO: Use the correct color
        // TODO: Document the geoJSON properties:
        // - userCanEdit
        // - type (community, need...)
        var komooMap = this;
        var featureCollection;

        var polygonOptions = $.extend({
            clickable: true,
            editable: false,
            zIndex: 1
        }, komooMap.options.overlayOptions);
        var polylineOptions = $.extend({
            clickable: true,
            editable: false
        }, komooMap.options.overlayOptions);
        var markerOptions = {};

        if (!geoJSON.type) return; // geoJSON is invalid.

        if (geoJSON.type == 'FeatureCollection') {
            featureCollection = geoJSON.features;
        }
        var n = null;
        var w = null;
        var s = null;
        var e = null;
        function getBounds(pos) {
            if (n == null) {
                n = s = pos[0];
                w = e = pos[1];
            }
            n = pos[0] < n ? pos[0] : n;
            s = pos[0] > s ? pos[0] : s;
            w = pos[1] < w ? pos[1] : w;
            e = pos[1] > e ? pos[1] : e;
            return [[s, w], [n, e]];
        }
        var bounds;
        $.each(featureCollection, function (i, feature) {
            var geometry = feature.geometry;
            var overlay;
            var paths = [];
            if (feature.properties.type && komooMap.overlayOptions[feature.properties.type]) {
                var color = komooMap.overlayOptions[feature.properties.type].color;
                polygonOptions.fillColor = color;
                polygonOptions.strokeColor = color;
                polylineOptions.strokeColor = color;
            } else {
                // TODO: set a default color
            }
            if (geometry.type == 'Polygon') {
                overlay = new google.maps.Polygon(polygonOptions);
                $.each(geometry.coordinates, function (j, coord) {
                    var path = [];
                    $.each(coord, function (k, pos) {
                        var latLng = new google.maps.LatLng(pos[0], pos[1]);
                        path.push(latLng);
                        bounds = getBounds(pos);
                    });
                    path.pop(); // Removes the last point that closes the loop
                    paths.push(path);
                });
                overlay.setPaths(paths);
            } else if (geometry.type == 'LineString') {
                overlay = new google.maps.Polyline(polylineOptions);
                var path = [];
                $.each(geometry.coordinates, function (k, pos) {
                    var latLng = new google.maps.LatLng(pos[0], pos[1]);
                    path.push(latLng);
                    bounds = getBounds(pos);
                });
                overlay.setPath(path);
            }  else if (geometry.type == 'Point') {
                overlay = new google.maps.Marker(markerOptions);
                var pos = geometry.coordinates;
                var latLng = new google.maps.LatLng(pos[0], pos[1]);
                overlay.setPosition(latLng);
            }
            if (overlay) {
                overlay.setMap(komooMap.googleMap);
                overlay.properties = feature.properties;
                komooMap._attachOverlayEvents(overlay);
                komooMap.overlays.push(overlay);
            }
        });
        if (panTo && bounds) {
            komooMap.googleMap.fitBounds(new google.maps.LatLngBounds(
                        new google.maps.LatLng(bounds[0][0], bounds[0][1]),
                        new google.maps.LatLng(bounds[1][0], bounds[1][1])
                    ));
        }
    },

    /**
     * Create a GeoJSON with the map's overlays.
     * @param {boolean} newOnly
     * @returns {json}
     */
    getGeoJSON: function (newOnly) {
        var geoJSON = {
            'type': 'FeatureCollection',
            'features': []
        };
        var list = newOnly ? this.newOverlays : this.overlays;
        $.each(list, function (i, overlay) {
            var coords = [];
            var subCoords = [];
            var feature = {
                'type': 'Feature',
                'geometry': {
                    'type': '', // Add the correct type
                    'coordinates': coords
                }
            };
            /* Gets coordinates */
            if (overlay.getPaths) { // Overlay have multiple paths
                overlay.getPaths().forEach(function (path, j) {
                    subCoords = [];
                    path.forEach(function (pos, j) {
                        subCoords.push([pos.lat(), pos.lng()]);
                    });
                    subCoords.push(subCoords[0]);  // Copy the first point as the last one to close the loop
                    coords.push(subCoords);
                    feature.geometry.type = 'Polygon';
                });
            } else if (overlay.getPath) { // Overlay have only one path
                overlay.getPath().forEach(function (pos, j) {
                    coords.push([pos.lat(), pos.lng()]);
                });
                if (overlay instanceof google.maps.Polyline){
                    feature.geometry.type = 'LineString';
                }
            } else if (overlay.getPosition) { // Overlay is a point
                var pos = overlay.getPosition();
                feature.geometry.type = 'Point';
                coords.push(pos.lat());
                coords.push(pos.lng());
            }
            feature.properties = overlay.properties;
            if (feature.geometry.coordinates.length) geoJSON['features'].push(feature);
        });
        return geoJSON;
    },

    /**
     * Remove all overlays from map.
     * @returns {void}
     */
    clear: function () {
        var komooMap = this;
        $.each(komooMap.overlays, function (key, overlay) {
            overlay.setMap(null);
            delete overlay;
        });
        komooMap.overlays = [];
    },

    /**
     * Set the current overlay and display the edit controls.
     * @param {google.maps.Polygon|google.maps.Polyline|null} overlay
     *        The overlay to be set as current or null to remove the selection.
     * @returns {void}
     */
    setCurrentOverlay: function (overlay) {
        var komooMap = this;
        /* Marks only the current overlay as editable */
        if (this.currentOverlay && this.currentOverlay.setEditable) {
            this.currentOverlay.setEditable(false);
            $('#komoo-map-add-button, #komoo-map-cut-out-button, #komoo-map-delete-button').hide();
        }
        this.currentOverlay = overlay;
        //console.log(this.currentOverlay.properties);
        if (this.currentOverlay && this.currentOverlay.setEditable &&
                this.currentOverlay.properties &&
                this.currentOverlay.properties.userCanEdit) {
            this.currentOverlay.setEditable(true);
            if (komooMap.currentOverlay.getPaths) {
                $('#komoo-map-add-button, #komoo-map-cut-out-button').show();
            }
            $('#komoo-map-delete-button').show();
        }
    },

    /**
     * Enable or disable the drawing feature.
     * @param {boolean} editable
     *        true to enable the drawing feature and false to disable.
     * @returns {void}
     */
    setEditable: function (editable) {
        var options;
        if (editable) {  // Enable
            if (!this.drawingManager) this._initDrawingManager();
            this.drawingManagerOptions.drawingMode = null;
            if (this.options.defaultDrawingControl)
                this.drawingManagerOptions.drawingControl = true;
            this.setCurrentOverlay(this.currentOverlay);
            if (this.editToolbar) this.editToolbar.show();
        } else {  // Disable
            this.drawingManagerOptions.drawingMode = null;
            if (this.options.defaultDrawingControl)
                this.drawingManagerOptions.drawingControl = false;
            if (this.currentOverlay && this.currentOverlay.setEditable) {
                this.currentOverlay.setEditable(false);
            }
            if (this.editToolbar) this.editToolbar.hide();
            this.editMode = null;
        }
        if (this.drawingManager) {
            this.drawingManager.setOptions(this.drawingManagerOptions);
        }
        this.editable = editable;
    },

    /**
     * Show a box containing the Google Street View layer.
     * @param {boolean} flag
     *        Sets to 'true' to make Street View visible or 'false' to hide.
     * @param {google.maps.LatLng} position
     * @returns {void}
     */
    setStreetView: function (flag, position) {
        // FIXME: Add close button to the Street View panel
        // TODO: Define the panel position and size
        if (!this.streetView) this._initStreetView();
        if (!position) position = this.googleMap.getCenter();
        this.streetView.setPosition(position);
        if (flag) this.streetViewPanel.show(); else this.streetViewPanel.hide();
        this.streetView.setVisible(flag);
    },

    /**
     * Use the HTML5 GeoLocation to set the user location as the map center.
     * @returns {void}
     */
    goToUserLocation: function () {
        var komooMap = this;
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var pos = new google.maps.LatLng(position.coords.latitude,
                                                 position.coords.longitude);
                komooMap.googleMap.setCenter(pos);
            });
        }
    },

    /**
     * Go to an address or to latitude, longitude position.
     * @param {String|google.maps.LatLng|Number[]} position
     *        An address or a pair latitude, longitude.
     * @returns {void}
     */
    goTo: function (position) {
        var komooMap = this;
        var latLng;
        function _go (latLng) {
            if (latLng) {
                komooMap.googleMap.panTo(latLng);
                if (! komooMap.searchMarker) {
                    komooMap.searchMarker = new google.maps.Marker();
                    komooMap.searchMarker.setMap(komooMap.googleMap);
                }
                komooMap.searchMarker.setPosition(latLng);
            }
            console.log(komooMap.searchMarker);
        }
        if (typeof position == 'string') { // Got address
            var request = {
                address: position,
                region: komooMap.region
            };
            this.geocoder.geocode(request, function (result, status_) {
                if (status_ == google.maps.GeocoderStatus.OK) {
                    var first_result = result[0];
                    latLng = first_result.geometry.location;
                    _go(latLng);
                }
            });
        } else {
            if (position instanceof Array) {
                latLng = new google.maps.LatLng(position[0], position[1]);
            } else {
                latLng = position;
            }
            _go(latLng);
        }
    },

    /**
     * Alias to {@link komoo.Map.goTo}.
     * @see komoo.Map.goTo
     */
    panTo: function (position) {
        return this.goTo(position);
    },

    /**
     * Attach some events to overlay.
     * @param {google.maps.Polygon|google.maps.Polyline} overlay
     * @returns {void}
     */
    _attachOverlayEvents: function (overlay) {
        var komooMap = this;
        google.maps.event.addListener(overlay, 'click', function (e) {
            if (window.console) console.log('Clicked on overlay');
            if (komooMap.addPanel.is(':visible') && this != komooMap.currentOverlay) {
                if (window.console) console.log('Clicked on unselected overlay');
                return;
            }
            if (komooMap.editMode == 'delete' && this.properties &&
                    this.properties.userCanEdit) {
                if (this == komooMap.currentOverlay) {
                    komooMap.setCurrentOverlay(null);
                }
                var l = 0;
                if (this.getPaths) {  // Clicked on polygon.
                    /* Delete only the path clicked */
                    var paths = this.getPaths();
                    l = paths.getLength();
                    paths.forEach(function (path, i) {
                        if (komoo.isPointInside(e.latLng, path)) {
                            paths.removeAt(i);
                            l--;
                        }
                    });
                }
                if (l == 0) {  // We had only one path, or the overlay wasn't a polygon.
                    this.setMap(null);
                } else {
                    komooMap.setCurrentOverlay(this);
                }
                // TODO: (IMPORTANT) Remove the overlay from komooMap.overlays
                komooMap.editMode = null;
                komooMap._emit_changed();
            } else {
                komooMap.editMode = null;
                komooMap.setCurrentOverlay(this);  // Select the clicked overlay
            }
        });
    },

    /**
     * Initialize the Google Maps Drawing Manager.
     * @returns {void}
     */
    _initDrawingManager: function () {
        var komooMap = this;
        var controlsPosition = google.maps.ControlPosition.TOP_LEFT;

        komooMap.drawingManagerOptions = {
            map: komooMap.googleMap,
            drawingControl: false,
            drawingControlOptions: {
                position: controlsPosition,
                drawingModes: [
                    google.maps.drawing.OverlayType.POLYGON,
                    google.maps.drawing.OverlayType.POLYLINE,
                    google.maps.drawing.OverlayType.CIRCLE,
                    google.maps.drawing.OverlayType.MARKER
                ]
            },
            polygonOptions: $.extend({
                clickable: true,
                editable: false,
                zIndex: 1
            }, komooMap.options.overlayOptions),
            polylineOptions: $.extend({
                clickable: true,
                editable: false
            }, komooMap.options.overlayOptions),
            circleOptions: {
                fillColor: 'white',
                fillOpacity: 0.15,
                editable: true,
                zIndex: -99999999999999
            },
            drawingMode: google.maps.drawing.OverlayType.POLYGON
        };
        komooMap.drawingManager = new google.maps.drawing.DrawingManager(
                komooMap.drawingManagerOptions);
        google.maps.event.addListener(komooMap.drawingManager,
                'overlaycomplete', function (e) {

            e.overlay.properties = {
                userCanEdit: true,
                type: komooMap.type
            };
            if (e.type != google.maps.drawing.OverlayType.MARKER) {
                // Switch back to non-drawing mode after drawing a shape.
                komooMap.drawingManager.setDrawingMode(null);
            }

            var path;
            if (e.overlay.getPath) path = e.overlay.getPath();

            if (e.type == google.maps.drawing.OverlayType.CIRCLE) {
                komooMap.radiusCircle = e.overlay;
            } else if ((komooMap.editMode == 'cutout' || komooMap.editMode == 'add') &&
                        e.overlay.getPaths) {
                /* Get the overlay orientation */
                var paths = komooMap.currentOverlay.getPaths();
                /* Get the paths orientations */
                var sArea = google.maps.geometry.spherical.computeSignedArea(path);
                var sAreaAdded = google.maps.geometry.spherical.computeSignedArea(
                        paths.getAt(0));
                var orientation = sArea / Math.abs(sArea);
                var orientationAdded = sAreaAdded / Math.abs(sAreaAdded);
                /* Verify the paths orientation */
                if ((orientation == orientationAdded && komooMap.editMode == 'cutout') ||
                        orientation != orientationAdded && komooMap.editMode == 'add') {
                    /* Reverse path orientation to correspond to the action  */
                    path = new google.maps.MVCArray(path.getArray().reverse());
                }
                paths.push(path);
                komooMap.currentOverlay.setPaths(paths);
                e.overlay.setMap(null);
                komooMap.editMode = null;
            } else {
                komooMap.overlays.push(e.overlay);
                komooMap.newOverlays.push(e.overlay);
                /* Listen events from drawn overlay */
                komooMap._attachOverlayEvents(e.overlay);
                komooMap.setCurrentOverlay(e.overlay);
            }
            if (path) {
                /* Emit changed event when edit paths */
                google.maps.event.addListener(path, 'set_at', function() {
                    komooMap._emit_changed();
                });
                google.maps.event.addListener(path, 'insert_at', function() {
                    komooMap._emit_changed();
                });
            }
            komooMap._emit_changed();
            return true;
        });

        if (!komooMap.options.defaultDrawingControl) {
            /* Adds new HTML element to the map */
            var radiusButton = komoo.createMapButton('Radius', '', function (e) {
                komooMap.editMode = null;
                if (komooMap.radiusCircle) komooMap.radiusCircle.setMap(null);
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.CIRCLE);
            });
            //komooMap.editToolbar.append(radiusButton);

            var polygonButton = komoo.createMapButton('Adicionar área', 'Draw a shape', function (e) {
                komooMap.editMode = null;
                komooMap.setCurrentOverlay(null);  // Remove the overlay selection
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.POLYGON);
                if (komooMap.overlayOptions[komooMap.type]) {
                    var color = komooMap.overlayOptions[komooMap.type].color;
                    komooMap.drawingManagerOptions.polygonOptions.fillColor = color;
                    komooMap.drawingManagerOptions.polygonOptions.strokeColor = color;
                }
            });
            //komooMap.editToolbar.append(polygonButton);

            var lineButton = komoo.createMapButton('Adicionar linha', 'Draw a line', function (e) {
                komooMap.editMode = null;
                komooMap.setCurrentOverlay(null);  // Remove the overlay selection
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.POLYLINE);
                if (komooMap.overlayOptions[komooMap.type]) {
                    var color = komooMap.overlayOptions[komooMap.type].color;
                    komooMap.drawingManagerOptions.polylineOptions.strokeColor = color;
                }
            });
            //komooMap.editToolbar.append(lineButton);

            var markerButton = komoo.createMapButton('Adicionar ponto', 'Add a marker', function (e) {
                komooMap.editMode = null;
                komooMap.setCurrentOverlay(null);  // Remove the overlay selection
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.MARKER);
            });
            //komooMap.editToolbar.append(markerButton);

            var addMenu = komoo.createMapMenu('Add new...', [polygonButton, lineButton, markerButton]);
            //komooMap.editToolbar.append(addMenu);
            komooMap.addItems = $('.map-container', addMenu);

            var addButton = komoo.createMapButton('Adicionar', 'Add another region', function (e) {
                komooMap.editMode = 'add';
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.POLYGON);
            });
            addButton.hide();
            addButton.attr('id', 'komoo-map-add-button');
            komooMap.editToolbar.append(addButton);

            var cutOutButton = komoo.createMapButton('Cortar', 'Cut out a hole from a region', function (e) {
                komooMap.editMode = 'cutout';
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.POLYGON);
            });
            cutOutButton.hide();
            cutOutButton.attr('id', 'komoo-map-cut-out-button');
            komooMap.editToolbar.append(cutOutButton);

            var deleteButton = komoo.createMapButton('Apagar', 'Delete a region', function (e) {
                komooMap.editMode = 'delete';
                komooMap.drawingManagerOptions.drawingMode = null;
                komooMap.drawingManager.setOptions(komooMap.drawingManagerOptions);
            });
            deleteButton.hide();
            deleteButton.attr('id', 'komoo-map-delete-button');
            komooMap.editToolbar.append(deleteButton);

        }

    },

    /**
     * Initialize the Google Street View.
     * @returns {void}
     */
    _initStreetView: function () {
        var options = {};
        this.streetView = new google.maps.StreetViewPanorama(
                this.streetViewPanel.get(0), options);
    },

    _createMainPanel: function () {
        var komooMap = this;
        var panel = $('<div>').addClass('map-panel');
        var addMenu = $('<ul>').addClass('map-menu');

        var tabs = komoo.createMapTab([
            {title: 'Filtrar'},
            {title: 'Adicionar', content: addMenu}
        ]);

        $.each(komooMap.options.overlayTypes, function (i, type) {
            komooMap.overlayOptions[type.type] = type;
            var item = $('<li>').addClass('map-menuitem').append($('<span>').text(type.title));
            var submenu = komooMap.addItems.clone(true);
            var submenuItems = $('div', submenu);
            submenuItems.removeClass('map-button').addClass('map-menuitem'); // Change the class
            submenuItems.bind('click', function (){
                submenu.hide();
                $('.map-panel-title', komooMap.addPanel).text($(this).text())
                $('.map-menuitem.selected', komooMap.mainPanel).removeClass('selected');
                item.addClass('selected');
                $('.map-menuitem:not(.selected)', komooMap.mainPanel).addClass('frozen');
            });
            if (type.disabled) item.addClass('disabled');
            item.css({
                'position': 'relative'
            });
            submenu.css({
                'position': 'absolute',
                'top': '0',
                'z-index': '999999'
            });
            item.append(submenu);
            item.hover(
                function () { // Over
                    if (komooMap.addPanel.is(':hidden') && !$(this).hasClass('disabled')) {
                        komooMap.type = type.type;
                        submenu.css({'left': item.outerWidth() + 'px'});
                        submenu.show();
                    }
                },
                function () { // Out
                    submenu.hide();
                });
            addMenu.append(item);
            type.selector = item;
        });

        panel.css({
            'margin': '10px 5px 10px 10px',
            'width': '180px',
        });

        panel.append(tabs.selector);

        google.maps.event.addListener(komooMap.drawingManager, 'drawingmode_changed',
            function (e){
                if (komooMap.drawingManager.drawingMode) {
                    komooMap.addPanel.show();
                }
            });

        return panel;
    },

    _createAddPanel: function () {
        var komooMap = this;
        var panel = $('<div>').addClass('map-panel');
        var content = $('<div>').addClass('content');
        var title = $('<div>').text('Título').addClass('map-panel-title');
        var buttons = $('<div>').addClass('map-panel-buttons');
        var finishButton = $('<div>').text('Concluir').addClass('map-button');
        var cancelButton = $('<div>').text('Cancelar').addClass('map-button');

        function button_click () {
            $('.map-menuitem.selected', komooMap.mainPanel).removeClass('selected');
            $('.frozen', komooMap.mainPanel).removeClass('frozen');
            komooMap.drawingManager.setDrawingMode(null);
            panel.hide();
        }
        cancelButton.bind('click', function () {
            var before = komooMap.overlays.length;
            button_click();
            var after = komooMap.overlays.length;
            if (before != after) { // User drew a overlay, so remove it.
                var overlay = komooMap.overlays.pop();
                overlay.setMap(null);
            }
            komooMap.event.trigger('cancel_click');
            komooMap.type = null;
        });
        finishButton.bind('click', function () {
            button_click();
            console.log('finish_click', komooMap.overlayOptions[komooMap.type]);
            komooMap.event.trigger('finish_click', komooMap.overlayOptions[komooMap.type]);
            komooMap.type = null;
        });

        content.css({'clear': 'both'});
        buttons.css({'clear': 'both'});
        content.append(komooMap.editToolbar);
        panel.append(title);
        panel.append(content);
        panel.append(buttons);
        buttons.append(finishButton);
        buttons.append(cancelButton);

        panel.css({
            'margin': '10px 10px 10px 0',
            'width': '220px'
        });

        return panel.hide();
    },

    _emit_mapclick: function (e) {
        this.event.trigger('mapclick', e);
    },

    _emit_overlayclick: function (e) {
        this.event.trigger('overlayclick', e);
    },

    _emit_changed: function (e) {
        this.event.trigger('changed', e);
    }
};

/**
 * Verify if a point is inside a closed path.
 * @param {google.maps.LatLng} point
 * @param {google.maps.MVCArray.<google.maps.LatLng>} path
 * @returns {boolean}
 */
komoo.isPointInside = function (point, path) {
    /* http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html */
    if (!path) return false;
    var ret = false;
    var l = path.getLength();
    for(var i=-1, j=l-1; ++i < l; j=i) {
        ((path.getAt(i).lng() <= point.lng() && point.lng() < path.getAt(j).lng()) ||
                (path.getAt(j).lng() <= point.lng() && point.lng() < path.getAt(i).lng()))
        && (point.lat() < (path.getAt(j).lat() - path.getAt(i).lat()) *
                          (point.lng() - path.getAt(i).lng()) /
                          (path.getAt(j).lng() - path.getAt(i).lng()) +
                          path.getAt(i).lat())
        && (ret = !ret);
    }
    return ret;
};

/**
 *
 */
komoo.createMapButton = function (name, title, onClick) {
    var selector = $('<div>').text(name).addClass('map-button');
    selector.attr('title', title);
    selector.bind('click', onClick);
    return selector;
};

/**
 *
 */
komoo.createMapMenu = function (name, items) {
    var selector = $('<div>').text(name).addClass('map-menu');
    var container = $('<div>').addClass('map-container').hide();
    $.each(items, function (i, item) {
        container.append(item);
        item.css({'clear': 'both', 'float': 'none'});
        item.bind('click', function () { container.hide(); });
    });
    selector.append(container);
    selector.hover(
            function () { container.show(); },
            function () { container.hide(); });
    return selector;
};

/**
 *
 */
komoo.createMapTab = function (items) {
    var tabs = {
        items: {},
        selector: $('<div>'),
        tabsSelector: $('<div>').addClass('map-tabs'),
        containersSelector: $('<div>').addClass('map-container'),
    };
    tabs.selector.append(tabs.tabsSelector, tabs.containersSelector);
    $.each(items, function (i, item) {
        var tab = {
            tabSelector: $('<div>').text(item.title).addClass('map-tab').css({'border': '0px'}),
            containerSelector: $('<div>').addClass('map-tab-container').hide()
        };
        if (item.content) tab.containerSelector.append(item.content);
        tab.tabSelector.click(
            function () {
                if (tabs.current && tabs.current != tab) {
                    tabs.current.tabSelector.removeClass('selected');
                    tabs.current.containerSelector.hide();
                }
                tabs.current = tab;
                tab.tabSelector.toggleClass('selected');
                tab.containerSelector.toggle();
            }
        );

        tabs.items[item.title] = tab;
        tab.tabSelector.css({'width': 100 / items.length + '%'});
        tabs.tabsSelector.append(tab.tabSelector);
        tabs.containersSelector.append(tab.containerSelector);
    });
    return tabs;
}
