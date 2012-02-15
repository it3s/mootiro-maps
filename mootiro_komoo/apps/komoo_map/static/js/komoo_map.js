/**
 * View, create and edit regions on Google Maps.
 *
 * @name map.js
 * @fileOverview A simple way to use Google Maps.
 * @version 0.1.0a
 * @author Luiz Armesto
 * @copyright (c) 2012 it3s
 */

//TODO: Emit events

/** @namespace */
var komoo = {};

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
    overlayOptions: {
        fillColor: '#ff0',
        fillOpacity: 0.4,
        strokeColor: '#ff0',
        strokeWeight: 3,
        strokeOpacity: 0.4
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
    komooMap.overlays = [];

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
        komooMap.setCurrentOverlay(null);  // Remove the overlay selection
        komooMap._emit_mapclick(e)
    });

    /* Adds GeoCoder */
    komooMap.geocoder = new google.maps.Geocoder();
}

komoo.Map.prototype = {
    /**
     * Load the features from geoJSON into the map.
     * @param {json} geoJSON The json that will be loaded.
     * @param {boolean} panTo If true pan to the region where overlays are.
     * @returns {void}
     */
    loadGeoJSON: function (geoJSON, panTo) {
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

        if (!geoJSON.type) return; // geoJSON is invalid.

        if (geoJSON.type == 'FeatureCollection') {
            featureCollection = geoJSON.features;
        }
        var n = null;
        var w = null;
        var s = null;
        var e = null;
        function getCenter(pos) {
            if (n == null) {
                n = s = pos[0];
                w = e = pos[1];
            }
            n = pos[0] < n ? pos[0] : n;
            s = pos[0] > s ? pos[0] : s;
            w = pos[1] < w ? pos[1] : w;
            e = pos[1] > e ? pos[1] : e;
            return [(s + n)/2, (w + e)/2];
        }
        var center;
        $.each(featureCollection, function (i, feature) {
            var geometry = feature.geometry;
            var overlay;
            var paths = [];
            if (geometry.type == 'Polygon') {
                overlay = new google.maps.Polygon(polygonOptions);
                $.each(geometry.coordinates, function (j, coord) {
                    var path = [];
                    $.each(coord, function (k, pos) {
                        var latLng = new google.maps.LatLng(pos[0], pos[1]);
                        path.push(latLng);
                        center = getCenter(pos);
                    });
                    paths.push(path);
                });
                overlay.setPaths(paths);
            } else if (geometry.type == 'LineString') {
                overlay = new google.maps.Polyline(polylineOptions);
                var path = [];
                $.each(geometry.coordinates, function (k, pos) {
                    var latLng = new google.maps.LatLng(pos[0], pos[1]);
                    path.push(latLng);
                    center = getCenter(pos);
                });
                overlay.setPath(path);
            }  // TODO: Load points
            if (overlay) {
                overlay.setMap(komooMap.googleMap);
                overlay.properties = feature.properties;
                komooMap._attachOverlayEvents(overlay);
                komooMap.overlays.push(overlay);
            }
        });
        if (panTo && center) {
            komooMap.panTo(new google.maps.LatLng(center[0], center[1]));
        }
    },

    /**
     * Create a GeoJSON with the map's overlays.
     * @returns {json}
     */
    getGeoJSON: function () {
        var geoJSON = {
            'type': 'FeatureCollection',
            'features': []
        };
        $.each(this.overlays, function (i, overlay) {
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
            geoJSON['features'].push(feature);
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
        /* Marks only the current overlay as editable */
        if (this.currentOverlay && this.currentOverlay.setEditable) {
            this.currentOverlay.setEditable(false);
            $('#komoo-map-add-button, #komoo-map-cut-out-button').hide();
        }
        this.currentOverlay = overlay;
        //console.log(this.currentOverlay.properties);
        if (this.currentOverlay && this.currentOverlay.setEditable &&
                this.currentOverlay.properties &&
                this.currentOverlay.properties.userCanEdit) {
            this.currentOverlay.setEditable(true);
            $('#komoo-map-add-button, #komoo-map-cut-out-button').show();
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
        if (typeof position == 'string') { // Got address
            var request = {
                address: position,
                region: komooMap.region
            };
            this.geocoder.geocode(request, function (result, status_) {
                if (status_ == google.maps.GeocoderStatus.OK) {
                    var first_result = result[0];
                    var latLng = first_result.geometry.location;
                    komooMap.googleMap.panTo(latLng);
                }
            });
        } else {
            var latLng;
            if (position instanceof Array) {
                latLng = new google.maps.LatLng(position[0], position[1]);
            } else {
                latLng = position;
            }
            komooMap.googleMap.panTo(latLng);
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
            komooMap.editToolbar.append(radiusButton);

            var polygonButton = komoo.createMapButton('Adicionar área', 'Draw a shape', function (e) {
                komooMap.editMode = null;
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.POLYGON);
            });
            //komooMap.editToolbar.append(polygonButton);

            var lineButton = komoo.createMapButton('Adicionar linha', 'Draw a line', function (e) {
                komooMap.editMode = null;
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.POLYLINE);
            });
            //komooMap.editToolbar.append(lineButton);

            var markerButton = komoo.createMapButton('Adicionar ponto', 'Add a marker', function (e) {
                komooMap.editMode = null;
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.MARKER);
            });
            //komooMap.editToolbar.append(markerButton);

            var addMenu = komoo.createMapMenu('Add new...', [polygonButton, lineButton, markerButton]);
            komooMap.editToolbar.append(addMenu);
            komooMap.addItems = $('.map-container', addMenu);

            var deleteButton = komoo.createMapButton('Delete', 'Delete a region', function (e) {
                komooMap.editMode = 'delete';
                komooMap.drawingManagerOptions.drawingMode = null;
                komooMap.drawingManager.setOptions(komooMap.drawingManagerOptions);
            });
            komooMap.editToolbar.append(deleteButton);

            var addButton = komoo.createMapButton('Add', 'Add another region', function (e) {
                komooMap.editMode = 'add';
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.POLYGON);
            });
            addButton.hide();
            addButton.attr('id', 'komoo-map-add-button');
            komooMap.editToolbar.append(addButton);

            var cutOutButton = komoo.createMapButton('Cut out', 'Cut out a hole from a region', function (e) {
                komooMap.editMode = 'cutout';
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.POLYGON);
            });
            cutOutButton.hide();
            cutOutButton.attr('id', 'komoo-map-cut-out-button');
            komooMap.editToolbar.append(cutOutButton);
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
        // TODO: improve
        var komooMap = this;
        var panel = $('<div>').addClass('map-panel');
        var menu = $('<ul>').addClass('map-menu');
        var types = ['Comunidades', 'Necessidades', 'Organizações', 'Recursos', 'Financiamentos'];

        var tabs = komoo.createMapTab([
            {title: 'Filtrar'},
            {title: 'Adicionar', content: menu}
        ]);

        $.each(types, function (i, type) {
            var item = $('<li><span>' +  type + '</span></li>').addClass('map-menuitem');
            var submenu = komooMap.addItems.clone(true);
            var submenuItems = $('div', submenu);
            submenuItems.attr({'style': ''}); // Clear the css style
            submenuItems.addClass('map-menuitem').removeClass('map-button'); // Change the class
            submenuItems.bind('click', function (){
                submenu.hide();
                $('.map-panel-title', komooMap.addPanel).text($(this).text())
            });
            submenuItems.each(function () { komoo._setMenuItemStyle($(this)); }); // Set the correct style
            item.css({
                'position': 'relative'
            });
            submenu.css({
                'position': 'absolute',
                'top': '0',
                'z-index': '999999'
            });
            item.append(submenu);
            komoo._setMenuItemStyle(item);
            item.hover(
                function () { // Over
                    komooMap.type = type;
                    submenu.css({'left': item.outerWidth() + 'px'});
                    submenu.show();
                },
                function () { // Out
                    submenu.hide();
                });
            menu.append(item);
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
                } else {
                    // FIXME: Change to edit panel
                    komooMap.addPanel.hide();
                }
            });

        return panel;
    },

    _createAddPanel: function () {
        // TODO: improve
        var komooMap = this;
        var panel = $('<div>').addClass('map-panel');
        var content = $('<div>').addClass('content');
        var title = $('<div>Título</div>').addClass('map-panel-title');
        var buttons = $('<div>').addClass('map-panel-buttons');
        var finishButton = $('<div>Concluir</div>').addClass('map-button');
        var cancelButton = $('<div>Cancelar</div>').addClass('map-button');

        function button_click () {
            komooMap.drawingManager.setDrawingMode(null);
            komooMap.type = null;
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
        });
        finishButton.bind('click', function () {
            button_click();
            komooMap.event.trigger('finish_click');
        });

        panel.append(title);
        panel.append(content);
        panel.append(buttons);
        buttons.append(finishButton);
        buttons.append(cancelButton);

        panel.css({
            'margin': '10px 10px 10px 0',
            'width': '180px'
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
    var selector = $('<div>' + name + '</div>');
    selector.addClass('map-button');
    selector.addClass('gmnoprint');
    komoo._setButtonStyle(selector);
    selector.attr('title', title);
    selector.bind('click', onClick);
    return selector;
};

/**
 *
 */
komoo.createMapMenu = function (name, items) {
    // TODO: Create the menu widget.
    var selector = $('<div>' + name + '</div>');
    selector.addClass('map-menu');
    selector.addClass('gmnoprint');
    komoo._setButtonStyle(selector);
    var container = $('<div>').addClass('map-container').hide();
    $.each(items, function (i, item) {
        container.append(item);
        item.css('clear', 'both');
        item.css('float', 'none');
        item.bind('click', function () { container.hide(); });
    });
    selector.append(container);
    selector.hover(
            function () { container.show(); },
            function () { container.hide(); });
    return selector;
};

komoo.createMapTab = function (items) {
    var tabs = {};
    tabs.items = {};
    tabs.selector = $('<div>');
    tabs.tabsSelector = $('<div>').addClass('map-tabs');
    tabs.containersSelector = $('<div>').addClass('map-container');
    tabs.selector.append(tabs.tabsSelector);
    tabs.selector.append(tabs.containersSelector);
    $.each(items, function (i, item) {
        var tab = {};
        tab.tabSelector = $('<div>' + item.title + '</div>').addClass('map-tab');
        komoo._setTabStyle(tab.tabSelector);
        tab.containerSelector = $('<div>').addClass('map-tab-container').hide();
        if (item.content) tab.containerSelector.append(item.content);
        komoo._setContainerStyle(tab.containerSelector);
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
        var size = 100 / items.length - 1;
        tab.tabSelector.css({'width': size + '%'});
        tabs.tabsSelector.append(tab.tabSelector);
        tabs.containersSelector.append(tab.containerSelector);
    });
    return tabs;
}

/**
 *
 */
komoo._setButtonStyle = function (selector) {
    selector.css({
        'cursor': 'default',
        'margin-right': '2px',
        'float': 'left',
        'direction': 'ltr',
        'overflow': 'hidden',
        'position': 'relative',
        //'font': '13px Arial, sans-serif',
        'padding': '4px',
        'border': '1px solid rgb(113, 123, 135)',
        'box-shadow': 'rgba(0, 0, 0, 0.398438) 0px 2px 4px',
        'background': '-webkit-gradient(linear, 0% 0%, 0% 100%, from(rgb(255, 255, 255)), to(rgb(230, 230, 230)))',
        'color': '#000'
    });
    selector.css({'background': '-moz-linear-gradient(center top , #FFFFFF, #E6E6E6) repeat scroll 0 0 transparent'});
};


komoo._setTabStyle = function (selector) {
    selector.css({
        //'font': '13px Arial, sans-serif',
        'text-align': 'center',
        'padding': '5px 0px',
        'float': 'left',
        'background': '#dceff4'
    });
};

komoo._setContainerStyle = function (selector) {
    selector.css({
        'clear': 'both',
        'background': '#dceff4'
    });
};

komoo._setMenuItemStyle = function (selector) {
    selector.css({
        'cursor': 'default',
        'margin-right': '2px',
        'direction': 'ltr',
        //'overflow': 'hidden',
        'position': 'relative',
        //'font': '13px Arial, sans-serif',
        'padding': '10px',
        //'box-shadow': 'rgba(0, 0, 0, 0.398438) 0px 2px 4px',
        'background': '#dceff4',
        'color': '#000',
        'white-space': 'nowrap'
    });

    selector.hover(function () {
        selector.css({
            'background': '#39b9c0',
            'color': '#fff'
        });
    }, function () {
        selector.css({
            'background': '#dceff4',
            'color': '#000'
        });
    });
};

/*$(function () {
    var myOptions = {
        useGeoLocation: true,
        googleMapOptions: {
            zoom: 16
        }
    };
    map = new komoo.Map(document.getElementById('map-canvas'), myOptions);
});*/
