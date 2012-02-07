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
 * Options object to {@link komoo.Map}.
 *
 * @namespace
 * @property {boolen} [editable=true]
 *           Define if the drawing feature will be enabled.
 * @property {boolean} [useGeoLocation=false]
 *           Define if the HTML5 GeoLocation will be used to set the initial location.
 * @property {Object} overlayOptions
 * @property {google.maps.MapOptions} googleMapOptions The Google Maps map options.
 */
komoo.MapOptions = {
    editable: true,
    useGeoLocation: false,
    overlayOptions: {
        fillColor: '#000',
        strokeColor: '#000'
    },
    googleMapOptions: {
        center: new google.maps.LatLng(-23.55, -46.65),  // São Paulo, SP - Brasil
        zoom: 15,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        streetViewControl: false
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

    /* Creates the Google Maps object */
    komooMap.googleMap = new google.maps.Map(element, googleMapOptions);

    /* Adds new HTML element to the map */
    /* Adds editor toolbar */
    komooMap.editToolbar = $('<div>').addClass('map-toolbar');
    komooMap.googleMap.controls[google.maps.ControlPosition.TOP_CENTER].push(
            komooMap.editToolbar.get(0));

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
    google.maps.event.addListener(komooMap.googleMap, 'click', function() {
        komooMap.setCurrentOverlay(null);  // Remove the overlay selection
    });

    /* Adds drawing manager */
    komooMap.setEditable(options.editable);

    /* Adds GeoCoder */
    komooMap.geocoder = new google.maps.Geocoder();
}

komoo.Map.prototype = {
    /**
     * Load the features from geoJSON into the map.
     * @param {json} geoJSON The json that will be loaded.
     * @returns {void}
     */
    loadGeoJSON: function (geoJSON) {
        var komooMap = this;
        var featureCollection;

        if (geoJSON.type == 'FeatureCollection') {
            featureCollection = geoJSON.features;
        }
        $.each(featureCollection, function (i, feature) {
            var geometry = feature.geometry;
            var overlay;
            var paths = [];
            if (geometry.type == 'Polygon') {
                overlay = new google.maps.Polygon();
                $.each(geometry.coordinates, function (j, coord) {
                    var path = [];
                    $.each(coord, function (k, pos) {
                        var latLng = new google.maps.LatLng(pos[0], pos[1]);
                        path.push(latLng);
                    });
                    paths.push(path);
                });
                overlay.setPaths(paths);
            } else if (geometry.type == 'LineString') {
                overlay = new google.maps.Polyline();
                var path = [];
                $.each(geometry.coordinates, function (k, pos) {
                    var latLng = new google.maps.LatLng(pos[0], pos[1]);
                    path.push(latLng);
                });
                overlay.setPath(path);
            }  // TODO: Load points
            if (overlay) {
                overlay.setMap(komooMap.googleMap);
                komooMap._attachOverlayEvents(overlay);
                komooMap.overlays.push(overlay);
            }
        });
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
        }
        this.currentOverlay = overlay;
        if (this.currentOverlay && this.currentOverlay.setEditable) {
            this.currentOverlay.setEditable(true);
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
            this.drawingManagerOptions.drawingControl = true;
            if (this.currentOverlay && this.currentOverlay.setEditable) {
                this.currentOverlay.setEditable(true);
            }
            this.editToolbar.show();
        } else {  // Disable
            this.drawingManagerOptions.drawingMode = null;
            this.drawingManagerOptions.drawingControl = false;
            if (this.currentOverlay && this.currentOverlay.setEditable) {
                this.currentOverlay.setEditable(false);
            }
            this.editToolbar.hide();
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
        google.maps.event.addListener(overlay, 'click', function () {
            if (window.console) console.log('Clicked on overlay');
            if (komooMap.editMode == 'delete') {
                if (this == komooMap.currentOverlay) {
                    // FIXME: Should delete only the clicked path
                    komooMap.setCurrentOverlay(null);
                }
                this.setMap(null);
                // TODO: (IMPORTANT) Remove the overlay from komooMap.overlays
                komooMap.editMode = null;
            } else if (komooMap.editable){
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
        var controlsPosition = google.maps.ControlPosition.TOP_CENTER;

        komooMap.drawingManagerOptions = {
            map: komooMap.googleMap,
            drawingControl: true,
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
            drawingMode: google.maps.drawing.OverlayType.POLYGON
        };
        komooMap.drawingManager = new google.maps.drawing.DrawingManager(
                komooMap.drawingManagerOptions);
        google.maps.event.addListener(komooMap.drawingManager,
                'overlaycomplete', function (e) {
            if ((komooMap.editMode == 'cutout' || komooMap.editMode == 'add') &&
                        e.overlay.getPaths) {
                /* Get the overlay orientation */
                var path = e.overlay.getPath();
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
            return false;
        });

        /* Adds new HTML element to the map */
        var addSelector = $('<button>Add</button>').addClass('map-button');
        addSelector.bind('click', function() {
            komooMap.editMode = 'add';
        });
        komooMap.editToolbar.append(addSelector);

        var cutOutSelector = $('<button>Cut out</button>').addClass('map-button');
        cutOutSelector.bind('click', function() {
            komooMap.editMode = 'cutout';
        });
        komooMap.editToolbar.append(cutOutSelector);

        var deleteSelector = $('<button>Delete</button>').addClass('map-button');
        deleteSelector.bind('click', function() {
            komooMap.editMode = 'delete';
            komooMap.drawingManagerOptions.drawingMode = null;
            komooMap.drawingManager.setOptions(komooMap.drawingManagerOptions);
        });
        komooMap.editToolbar.append(deleteSelector);
    },

    /**
     * Initialize the Google Street View.
     * @returns {void}
     */
    _initStreetView: function () {
        var options = {};
        this.streetView = new google.maps.StreetViewPanorama(
                this.streetViewPanel.get(0), options);
    }
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
