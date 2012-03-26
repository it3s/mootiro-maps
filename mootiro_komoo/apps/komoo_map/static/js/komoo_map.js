/**
 * View, create and edit regions on Google Maps.
 *
 * @name map.js
 * @fileOverview A simple way to use Google Maps.
 * @version 0.1.0a
 * @author Luiz Armesto
 * @copyright (c) 2012 it3s
 */

// TODO: Get from Django the static url to avoid hardcode some urls.

/** @namespace */
var komoo = {};

/**
 * Object that represents a item on 'Add' tab of main panel.
 *
 * @namespace
 * @property {String} type An internal identifier.
 * @property {String} title The text displayed to user as a menu item.
 * @property {String} tooltip The text displayed on mouse over.
 * @property {String} icon The icon url.
 * @property {Array[google.maps.drawing.OverlayType]} overlayTypes The geometry options displayed as submenu.
 * @property {String} formUrl The url used to load the form via ajax.
 *           This occurs when user click on 'Finish' button.
 *           Please use dutils.urls.resolve instead of hardcode the address.
 * @property {boolean} disabled
 */
komoo.RegionType = {};

/**
 * Array of {@link komoo.RegionType} objects to populate the 'Add' tab of main panel.
 *
 * @namespace
 */
komoo.RegionTypes = [
    {
        type: 'community',
        categories: [],
        title: gettext('Community'),
        tooltip: gettext('Add Community'),
        color: '#ff0',
        icon: '/static/img/need.png', // FIXME: Add the correct icon
        overlayTypes: [google.maps.drawing.OverlayType.POLYGON],
        formUrl: dutils.urls.resolve('new_community'),
        viewUrl: '',
        disabled: false
    },
    {
        type: 'need',
        categories: ['Education', 'Sport', 'Environment', 'Health', 'Housing',
                     'Local Economy', 'Social Service'], // FIXME: Hardcode is evil
        title: gettext('Needs'),
        tooltip: gettext('Add Need'),
        color: '#f00',
        icon: '/static/img/need.png',
        overlayTypes: [google.maps.drawing.OverlayType.POLYGON,
                       google.maps.drawing.OverlayType.POLYLINE,
                       google.maps.drawing.OverlayType.MARKER],
        formUrl: dutils.urls.resolve('new_need',
            {community_slug: 'community_slug'}),
        viewUrl: '',
        disabled: false
    },
    {
        type: 'organization',
        categories: [],
        title: gettext('Organization'),
        tooltip: gettext('Add Organization'),
        color: '#00f',
        icon: '/static/img/organization.png',
        overlayTypes: [google.maps.drawing.OverlayType.POLYGON],
        formUrl: dutils.urls.resolve('organization_edit',
            {community_slug: 'community_slug'}),
        viewUrl: '',
        disabled: false
    },
    {
        type: 'resource',
        categories: [],
        title: gettext('Resource'),
        tooltip: gettext('Add Resource'),
        color: '#fff',
        icon: '/static/img/resource.png',
        overlayTypes: [google.maps.drawing.OverlayType.POLYGON,
                       google.maps.drawing.OverlayType.POLYLINE,
                       google.maps.drawing.OverlayType.MARKER],
        formUrl: dutils.urls.resolve('resource_new',
            {community_slug: 'community_slug'}),
        viewUrl: '',
        disabled: false
    },
    {
        type: 'funder',
        categories: [],
        title: gettext('Funder'),
        tooltip: gettext('Add Funder'),
        color: '#000',
        icon: '/static/img/funder.png',
        overlayTypes: [google.maps.drawing.OverlayType.POLYGON],
        formUrl: '',
        viewUrl: '',
        disabled: true
    }
];

/**
 * Options object to {@link komoo.Map}.
 *
 * @namespace
 * @property {boolen} [editable=true]  Define if the drawing feature will be enabled.
 * @property {boolean} [useGeoLocation=false] Define if the HTML5 GeoLocation will be used to set the initial location.
 * @property {boolean} [defaultDrawingControl=false] If true the controls from Google Drawing library are used.
 * @property {Object} [regionTypes=komoo.RegionTypes]
 * @property {boolean} [autoSaveLocation=false] Determines if the current location is saved to be displayed the next time the map is loaded.
 * @property {boolean} [enableInfoWindow=true] Shows informations on mouse over.
 * @property {boolean} [enableCluster=false] Cluster some points together.
 * @property {Object} overlayOptions
 * @property {google.maps.MapOptions} googleMapOptions The Google Maps map options.
 */
komoo.MapOptions = {
    editable: true,
    useGeoLocation: false,
    defaultDrawingControl: false,
    regionTypes: komoo.RegionTypes,
    autoSaveLocation: false,
    enableInfoWindow: true,
    enableCluster: false,
    overlayOptions: {
        visible: true,
        fillColor: '#ff0',
        fillOpacity: 0.45,
        strokeColor: '#ff0',
        strokeWeight: 3,
        strokeOpacity: 1
    },
    googleMapOptions: {  // Our default options for Google Maps map object.
        center: new google.maps.LatLng(-23.55, -46.65),  // São Paulo, SP - Brasil
        zoom: 13,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        streetViewControl: false,
        scaleControl: true,
        panControlOptions: {position: google.maps.ControlPosition.RIGHT_TOP},
        zoomControlOptions: {position: google.maps.ControlPosition.RIGHT_TOP},
        scaleControlOptions: {position: google.maps.ControlPosition.RIGHT_BOTTOM,
                              style: google.maps.ScaleControlStyle.DEFAULT}
    }
};

/**
 * Object used to get overlays from server for each tile
 *
 * @class
 * @param {komoo.Map} komooMap
 * @property {komoo.Map} komooMap
 * @property {google.maps.Size} tileSize The tile size. Default: 256x256
 * @property {Number} [maxZoom=32]
 * @property {String} name
 * @property {String} alt
 */
komoo.ServerFetchMapType = function (komooMap) {
    var serverFetchMapType = this;
    serverFetchMapType.komooMap = komooMap;
    serverFetchMapType.tileSize = new google.maps.Size(256, 256);
    serverFetchMapType.maxZoom = 32;
    serverFetchMapType.name = 'Server Data';
    serverFetchMapType.alt  = 'Server Data Tile Map Type';
};

komoo.ServerFetchMapType.prototype = {
    releaseTile: function (tile) {
        var serverFetchMapType = this;
        var komooMap = serverFetchMapType.komooMap;
        if (komooMap.fetchedTiles[tile.tileKey]) {
            $.each(komooMap.fetchedTiles[tile.tileKey].overlays, function (key, overlay) {
                bounds = komooMap.googleMap.getBounds();
                if (overlay.bounds) {
                    if (!bounds.intersects(overlay.bounds)) {
                        overlay.setMap(null);
                    }
                } else if (overlay.getPosition) {
                    if (bounds.contains(overlay.getPosition())) {
                        overlay.setMap(null);
                    }
                }
            });
        }
    },

    getTile: function (coord, zoom, ownerDocument) {
        var serverFetchMapType = this;
        var komooMap = serverFetchMapType.komooMap;
        var div = ownerDocument.createElement('DIV');
        var addr = serverFetchMapType.getAddrLatLng(coord, zoom);
        div.tileKey = addr;
        $(div).css({
            'width': serverFetchMapType.tileSize.width + 'px',
            'height': serverFetchMapType.tileSize.height + 'px',
            //'border': 'solid 1px #AAAAAA',
            'overflow': 'hidden',
            'font-size': '9px'
        });

        // Verify if we already loaded this block.
        if (komooMap.fetchedTiles[addr]) {
            //div.innerHTML = serverFetchMapType.fetchedTiles[addr].geojson;
            $.each(komooMap.fetchedTiles[addr].overlays, function (key, overlay) {
                overlay.setMap(komooMap.googleMap);
            });
            return div;
        }
        $.ajax({
            url: "/get_geojson?" + addr,
            dataType: 'json',
            type: 'GET',
            success: function (data, textStatus, jqXHR) {
                var overlays_ = [];
                var overlays = komooMap.loadGeoJSON(JSON.parse(data), false);
                komooMap.fetchedTiles[addr] = {
                    geojson: data,
                    overlays: overlays
                };
                //div.innerHTML = data;
                //$(div).css('border', 'solid 1px #F00');
            },
            error: function (jqXHR, textStatus, errorThrown) {
                if (window.console) console.error(textStatus);
                alert('ERRO!!!22! - ' + this.url); // FIXME: Add an usefull message.
            }
        });
        return div;
    },

    /**
     * Converts tile coords to Latitude, Longitude and return a url params.
     *
     * @param {google.maps.Point} coord Tile coordinates (x, y).
     * @param {Number} zoom Zoom level.
     * @returns {String} The url params to get the data from server.
     */
    getAddrLatLng: function (coord, zoom) {
        var serverFetchMapType = this;
        var projection = serverFetchMapType.komooMap.googleMap.getProjection();
        var numTiles = 1 << zoom;
        var point1 = new google.maps.Point(
                (coord.x + 1) * serverFetchMapType.tileSize.width / numTiles,
                coord.y * serverFetchMapType.tileSize.width / numTiles);
        var point2 = new google.maps.Point(
                coord.x * serverFetchMapType.tileSize.width / numTiles,
                (coord.y + 1) * serverFetchMapType.tileSize.width / numTiles);
        var ne = projection.fromPointToLatLng(point1);
        var sw = projection.fromPointToLatLng(point2);
        return "bounds=" + ne.toUrlValue() + "," + sw.toUrlValue() + "&zoom=" + zoom;
    }
};

/**
 * Wrapper for Google Maps map object with some helper methods.
 *
 * @class
 * @param {DOM} element The map canvas.
 * @param {komoo.MapOptions} options The options object.
 * @property {komoo.MapOptions} options The options object used to construct the komoo.Map object.
 * @property {google.maps.MVCObject[]} overlays Array containing all overlays.
 * @property {google.maps.MVCObject[]} newOverlays Array containing new overlays added by user.
 * @property {google.maps.Map} googleMap The Google Maps map object.
 * @property {google.maps.drawing.DrawingManager} drawingManager Drawing manager from Google Maps library.
 * @property {boolean} editable The status of the drawing feature.
 * @property {google.maps.Geocoder} geocoder  Google service to get addresses locations.
 * @property {JQuery} editToolbar JQuery selector of edit toolbar.
 * @property {String} editMode The current mode of edit feature. Possible values are 'cutout', 'add' and 'delete'.
 * @property {JQuery} streetViewPanel JQuery selector of Street View panel.
 * @property {google.maps.StreetViewPanorama} streetView
 * @property {JQuery} event JQuery selector used to emit events.
 * @property {google.maps.Circle} radiusCircle
 * @property {Object} overlayOptions
 * @property {InfoBox | google.maps.InfoWindow} infoWindow
 * @property {undefined | MarkerClusterer} clusterer A MarkerClusterer object used to cluster markers.
 * @property {komoo.ServerFetchMapType} serverFetchMapType
 * @property {Object} fetchedTiles Cache the json and the overlays for each tile
 * @property {Object} loadedOverlays Cache all overlays
 * @property {String | null} mode Possible values are null, 'new', 'edit'
 */
komoo.Map = function (element, options) {
    var komooMap = this;
    // options should be an object.
    if (typeof options !== 'object') {
        options = {};
    }
    // Join default option with custom options.
    var googleMapOptions = $.extend(komoo.MapOptions.googleMapOptions,
                                    options.googleMapOptions);
    // TODO: init overlay options
    // Initializing some properties.
    komooMap.mode = null;
    komooMap.fetchedTiles = {};
    komooMap.loadedOverlays = {};
    komooMap.options = $.extend(komoo.MapOptions, options);
    komooMap.drawingManagerOptions = {};
    komooMap.overlayOptions = {};
    komooMap.overlays = [];
    komooMap.loadedOverlays = {};
    komooMap.overlaysByType = {};
    komooMap.initOverlaysByTypeObject();
    komooMap.newOverlays = [];
    // Creates a jquery selector to use the jquery events feature.
    komooMap.event = $('<div>');
    // Creates the Google Maps object.
    komooMap.googleMap = new google.maps.Map(element, googleMapOptions);
    // Uses Tiles to get data from server.
    komooMap.serverFetchMapType = new komoo.ServerFetchMapType(komooMap);
    komooMap.googleMap.overlayMapTypes.insertAt(0, komooMap.serverFetchMapType);
    komooMap.initMarkerClusterer();
    // Create the simple version of toolbar.
    komooMap.editToolbar = $('<div>').addClass('map-toolbar').css('margin', '5px');
    komooMap.initInfoWindow();
    komooMap.setEditable(komooMap.options.editable);
    komooMap.initCustomControl();
    komooMap.initStreetView();
    if (komooMap.options.useGeoLocation) {
        komooMap.goToUserLocation();
    }
    komooMap.useSavedMapType();
    komooMap.handleEvents();
    // Geocoder is used to search locations by name/address.
    komooMap.geocoder = new google.maps.Geocoder();
    if (komoo.onMapReady) {
        komoo.onMapReady(komooMap);
    }
};

komoo.Map.prototype = {
    /**
     * Prepares the infoWindow property. Should not be called externally
     * @returns {void}
     */
    initInfoWindow: function () {
        var komooMap = this;
        if (window.InfoBox) {  // Uses infoBox if available.
            komooMap.infoWindow = new InfoBox({
                pixelOffset: new google.maps.Size(0, -20),
                closeBoxMargin: '10px',
                boxStyle: {
                    background: 'url(/static/img/infowindow-arrow.png) no-repeat 0 10px', // TODO: Hardcode is evil
                    width: '200px'
                }
            });
            google.maps.event.addDomListener(komooMap.infoWindow, 'domready', function (e) {
                var closeBox = komooMap.infoWindow.div_.firstChild;
                $(closeBox).hide();  // Removes the close button.
                google.maps.event.addDomListener(closeBox, 'click', function (e) {
                    // Detach the overlay from infowindow when close it.
                    komooMap.infoWindow.overlay = undefined;
                });
            });
        } else {  // Otherwise uses the default InfoWindow.
            if (window.console) console.log('Using default info window.');
            komooMap.infoWindow = new google.maps.InfoWindow();
        }

        komooMap.infoWindow.title = $('<a>');
        komooMap.infoWindow.body = $('<div>');
        komooMap.infoWindow.content = $('<div>').addClass('map-infowindow-content');
        komooMap.infoWindow.content.append(komooMap.infoWindow.title);
        komooMap.infoWindow.content.append(komooMap.infoWindow.body);
        if (InfoBox) {
            komooMap.infoWindow.content.css({
                background: 'white',
                padding: '10px',
                margin: '0 0 0 15px'
            });
        }
        komooMap.infoWindow.content.hover(
            function (e) {
                clearTimeout(komooMap.infoWindow.timer);
                komooMap.infoWindow.isMouseover = true;
            },
            function (e) {
                clearTimeout(komooMap.infoWindow.timer);
                komooMap.infoWindow.isMouseover = false;
                komooMap.infoWindow.timer = setTimeout(function () {
                    if (!komooMap.infoWindow.isMouseover) {
                        komooMap.infoWindow.close();
                        komooMap.infoWindow.overlay = undefined;
                    }
                }, 200);
            }
        );
        komooMap.infoWindow.setContent(komooMap.infoWindow.content.get(0));

    },

    /*
     * Closes the information window.
     * @returns {void}
     */
    closeInfoWindow: function () {
        var komooMap = this;
        komooMap.infoWindow.close();
    },

    /**
     * Display the information window.
     * @param {google.maps.MVCObject} overlay
     * @param {google.maps.LatLng} latLng
     * @returns {void}
     */
    openInfoWindow: function (overlay, latLng) {
        var komooMap = this;
        komooMap.infoWindow.title.attr('href', '#');
        komooMap.infoWindow.title.text(overlay.properties.name);
        komooMap.infoWindow.body.html('');
        if (overlay.properties.type == 'community') {
            // FIXME: Move url to options object
            komooMap.infoWindow.title.attr('href', dutils.urls.resolve('view_community', {
                        community_slug: overlay.properties.community_slug
                    })
            );
            var msg = ngettext('%s resident', '%s residents', overlay.properties.population);
            komooMap.infoWindow.body.html('<ul><li>' + interpolate(msg, [overlay.properties.population]) + '</li></ul>');
        } else if (overlay.properties.type == 'resource') {
            komooMap.infoWindow.title.attr('href', dutils.urls.resolve('view_resource', {
                        community_slug: overlay.properties.community_slug,
                        id: overlay.properties.id
                    })
            );
        } /*else if (overlay.properties.type == 'organization') {
            komooMap.infoWindow.title.attr('href', dutils.urls.resolve('view_organization', {
                        community_slug: overlay.properties.community_slug,
                        organization_slug: overlay.properties.organization_slug
                    })
            );
        }*/ else {
            var slugname = overlay.properties.type + '_slug';
            var params = {'community_slug': overlay.properties.community_slug};
            params[slugname] = overlay.properties[slugname];
            komooMap.infoWindow.title.attr('href', dutils.urls.resolve('view_' + overlay.properties.type, params));
        }

        komooMap.infoWindow.overlay = overlay;
        komooMap.infoWindow.setPosition(latLng);
        komooMap.infoWindow.open(komooMap.googleMap);
    },

    /**
     * Prepares the CustomControl property. Should not be called externally
     * @returns {void}
     */
    initCustomControl: function () {
        var komooMap = this;
        // Draw our custom control.
        if (!komooMap.options.defaultDrawingControl) {
            komooMap.mainPanel = komooMap._createMainPanel();
            if (!komooMap.editable) {
                komooMap.mainPanel.hide();
            }
            //komooMap.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
            //        komooMap.mainPanel.get(0));
            komooMap.addPanel = komooMap._createAddPanel();
            komooMap.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
                    komooMap.addPanel.get(0));
            // Adds editor toolbar.
            //komooMap.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
            //        komooMap.editToolbar.get(0));
        }
    },

    /**
     * Prepares the markerClusterer property. Should not be called externally.
     * @returns {void}
     */
    initMarkerClusterer: function () {
        var komooMap = this;
        // Adds MarkerClusterer if available.
        if (window.MarkerClusterer && komooMap.options.enableCluster) {
            if (window.console) console.log('Initializing Marker Clusterer support.');
            komooMap.clusterer = new MarkerClusterer(komooMap.googleMap, [], {
                gridSize: 20
            });
        }
    },

    /**
     * Prepares the overlaysByType property. Should not be called externally.
     * @returns {void}
     */
    initOverlaysByTypeObject: function () {
        var komooMap = this;
        $.each(komooMap.options.regionTypes, function (i, type) {
            komooMap.overlaysByType[type.type] = {};
            komooMap.overlaysByType[type.type]['uncategorized'] = [];
            if (type.categories.length) {
                $.each(type.categories, function(j, category) {
                    komooMap.overlaysByType[type.type][category] = [];
                });
            }
        });
    },

    /**
     * Prepares the streetVies property. Should not be called externally.
     * @returns {void}
     */
    initStreetView: function () {
        var komooMap = this;
        if (window.console) console.log('Initializing StreetView support.');
        komooMap.streetViewPanel = $('<div>').addClass('map-panel');
        komooMap.googleMap.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(
                komooMap.streetViewPanel.get(0));
        komooMap.streetViewPanel.hide();
    },

    /**
     * Connects some important events. Should not be called externally.
     * @returns {void}
     */
    handleEvents: function () {
        var komooMap = this;
        if (window.console) console.log('Connecting map events.');
        // Listen Google Maps map events.
        google.maps.event.addListener(komooMap.googleMap, 'click', function(e) {
            if (komooMap.addPanel.is(':hidden')) {
                komooMap.setCurrentOverlay(null);  // Remove the overlay selection
            }
            if (komooMap.mode == 'selectcenter') {
                komooMap._emit_centerselected(e.latLng);
            }
            komooMap._emit_mapclick(e);
        });

        google.maps.event.addListener(komooMap.googleMap, 'idle', function () {
            if (komooMap.options.autoSaveLocation) {
                komooMap.saveLocation();
            }
        });

        google.maps.event.addListener(komooMap.googleMap, 'projection_changed', function () {
            komooMap.projection = komooMap.googleMap.getProjection();
            komooMap.overlayView = new google.maps.OverlayView();
            komooMap.overlayView.draw = function () { };
            komooMap.overlayView.onAdd = function (d) { };
            komooMap.overlayView.setMap(komooMap.googleMap);
        });

        google.maps.event.addListener(komooMap.googleMap, 'rightclick', function (e) {
            if (!komooMap.overlayView) {
                google.maps.event.trigger(komooMap.googleMap, 'projection_changed');
            }
            var overlay = komooMap.currentOverlay;
            if (overlay && overlay.properties &&
                    overlay.properties.userCanEdit) {
                komooMap.deleteNode(e, komooMap);
            }
        });

        google.maps.event.addListener(komooMap.googleMap, 'maptypeid_changed', function () {
            komooMap.saveMapType();
        });
    },

    getVisibleOverlays: function () {
        var komooMap = this;
        var bounds = komooMap.googleMap.getBounds();
        var overlays = [];
        $.each(komooMap.overlays, function (key, overlay) {
            if (!overlay.getVisible()) {
                // Dont verify the intersection if overlay is invisible.
                return;
            }
            if (overlay.bounds) {
                if (bounds.intersects(overlay.bounds)) {
                    overlays.push(overlay);
                }
            } else if (overlay.getPosition) {
                if (bounds.contains(overlay.getPosition())) {
                    overlays.push(overlay);
                }
            }
        });
        return overlays;
    },

    /**
     * Saves the map location to cookie
     * @property {google.maps.LatLng} center
     * @returns {void}
     */
    saveLocation: function (center) {
        var komooMap = this;
        if (!center) {
            center = komooMap.googleMap.getCenter();
        }
        var zoom = komooMap.googleMap.getZoom();
        komoo.createCookie('lastLocation', center.toUrlValue(), 90);
        komoo.createCookie('lastZoom', zoom, 90);
    },

    /**
     * Loads the location saved in a cookie and go to there.
     * @see komoo.Map.saveLocation
     * @returns {boolean}
     */
    goToSavedLocation: function () {
        var komooMap = this;
        var lastLocation = komoo.readCookie('lastLocation');
        var zoom = parseInt(komoo.readCookie('lastZoom'), 10);
        if (lastLocation && zoom) {
            lastLocation = lastLocation.split(',');
            var center = new google.maps.LatLng(lastLocation[0], lastLocation[1]);
            komooMap.googleMap.setCenter(center);
            komooMap.googleMap.setZoom(zoom);
            return true;
        }
        return false;
    },

    /**
     * Saves the map type to cookie
     * @property {google.maps.MapTypeId|String} mapType
     * @returns {void}
     */
    saveMapType: function (mapType) {
        var komooMap = this;
        if (!mapType) {
            mapType = komooMap.googleMap.getMapTypeId();
        }
        komoo.createCookie('mapType', mapType, 90);
    },

    /**
     * Use the map type saved in a cookie.
     * @see komoo.Map.saveMapType
     * @returns {boolean}
     */
    useSavedMapType: function () {
        var komooMap = this;
        var mapType = komoo.readCookie('mapType');
        if (mapType) {
            komooMap.googleMap.setMapTypeId(mapType);
            return true;
        }
        return false;
    },

    /**
     * Load the features from geoJSON into the map.
     * @param {json} geoJSON The json that will be loaded.
     * @param {boolean} panTo If true pan to the region where overlays are.
     * @returns {Array[google.maps.MVCObject]}
     */
    loadGeoJSON: function (geoJSON, panTo, optAttach) {
        // TODO: Use the correct color
        // TODO: Add a hidden marker for each polygon/polyline
        // TODO: Document the geoJSON properties:
        // - userCanEdit
        // - type (community, need...)
        var komooMap = this;
        var featureCollection;
        var overlays = [];

        if (optAttach === undefined) {
            optAttach = true;
        }

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
            if (n === null) {
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
            if (!geometry) { return; }
            var overlay;
            var paths = [];
            bounds = null;
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
                if (feature.properties.categories && feature.properties.categories[0]) {
                    overlay.setIcon('/static/' + feature.properties.categories[0].image);
                } else {
                    overlay.setIcon('/static/img/' + feature.properties.type + '.png'); // FIXME: Hardcode is evil
                }
                if (panTo) komooMap.googleMap.setCenter(latLng);
                // Adds to clusterer
                if (komooMap.clusterer) {
                    komooMap.clusterer.addMarker(overlay);
                }
            }
            // Dont attach or return the overlays already loaded
            if (overlay) {
                overlay.properties = feature.properties;
                overlay = komooMap.loadedOverlays[feature.properties.type + '_' + feature.properties.id] || overlay;
                if (!komooMap.loadedOverlays[overlay.properties.type + '_' + overlay.properties.id]) {
                    komooMap.overlays.push(overlay);
                    komooMap.loadedOverlays[overlay.properties.type + '_' + overlay.properties.id] = overlay;
                    komooMap._attachOverlayEvents(overlay);
                }
                overlays.push(overlay);
                if (optAttach) {
                    overlay.setMap(komooMap.googleMap);
                }
                var overlaysByType = komooMap.overlaysByType[overlay.properties.type];
                var categories = overlay.properties.categories;
                if (categories && categories.length) {
                    $.each(categories, function(i, category) {
                        if (overlaysByType[category.name]) {
                            overlaysByType[category.name].push(overlay);
                        }
                    });
                } else {
                    overlaysByType['uncategorized'].push(overlay);
                }
                if (bounds) {
                    overlay.bounds = new google.maps.LatLngBounds(
                            new google.maps.LatLng(bounds[1][0], bounds[0][1]),
                            new google.maps.LatLng(bounds[0][0], bounds[1][1])
                    );
                    n = null;
                    w = null;
                    s = null;
                    e = null;
                }
            }
        });
        if (panTo && bounds) {
            komooMap.googleMap.fitBounds(new google.maps.LatLngBounds(
                    new google.maps.LatLng(bounds[0][0], bounds[0][1]),
                    new google.maps.LatLng(bounds[1][0], bounds[1][1])
            ));
        }
        return overlays;
    },

    /**
     * Create a GeoJSON with the map's overlays.
     * @param {boolean} newOnly
     * @returns {json}
     */
    getGeoJSON: function (options) {
        // TODO: Create a default options object
        var komooMap = this;
        var geoJSON;
        var geoms = [];
        var list;
        if (!options) {
            options = {};
        }
        if (options.geometryCollection) {
            geoJSON = {
                'type': 'GeometryCollection',
                'geometries': geoms
            };
        } else {
            geoJSON = {
                'type': 'FeatureCollection',
                'features': []
            };
        }
        if (options.newOnly) {
            list = komooMap.newOverlays;
        } else if (options.currentOnly) {
            list = [komooMap.currentOverlay];
        } else {
            list = komooMap.overlays;
        }
        $.each(list, function (i, overlay) {
            var subCoords = [];
            var coords = [];
            var feature = {
                'type': 'Feature',
                'geometry': {
                    'type': '', // Add the correct type
                    'coordinates': coords
                }
            };
            // Gets coordinates.
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
            if (feature.geometry.coordinates.length)  {
                if (geoJSON.features) geoJSON.features.push(feature);
                if (geoJSON.geometries) geoJSON.geometries.push(feature.geometry);
            }
        });
        return geoJSON;
    },

    /**
     * Gets a list of overlays of specific type.
     * @property {String} type
     * @property {Array} optCategories
     * @property {boolean} optStrict
     * @returns {Array} Overlays that matches the parameters.
     */
    getOverlaysByType: function (type, optCategories, optStrict) {
        var komooMap = this;
        var overlays = [];
        var categories = optCategories;
        if (!komooMap.overlaysByType[type]) {
            return false;
        }
        if (!categories) {
            categories = [];
            $.each(komooMap.overlaysByType[type], function (category, overlays) {
                categories.push(category);
            });
        } else if (categories.length === 0) {
            categories = ['uncategorized'];
        }
        $.each(categories, function (key, category) {
            if (komooMap.overlaysByType[type][category]) {
                $.each(komooMap.overlaysByType[type][category], function (key, overlay) {
                    if (!optStrict || !overlay.properties.categories || overlay.properties.categories.length == 1) {
                        overlays.push(overlay);
                    }
                });
            }
        });
        return overlays;
    },

    /**
     * Hides some overlays.
     * @property {Array} overlays
     * @returns {Number} How many overlays were hidden.
     */
    hideOverlays: function (overlays) {
        var komooMap = this;
        var ret = 0;
        $.each(overlays, function (key, overlay) {
            overlay.setVisible(false);
            ret++;
        });
        return ret;
    },

    /**
     * Hides overlays of specific type.
     * @property {String} type
     * @property {Array} optCategories
     * @property {boolean} optStrict
     * @returns {Number} How many overlays were hidden.
     */
    hideOverlaysByType: function (type, optCategories, optStrict) {
        var komooMap = this;
        var overlays = komooMap.getOverlaysByType(type, optCategories, optStrict);
        return komooMap.hideOverlays(overlays);
    },

    /**
     * Hides all overlays.
     * @returns {Number} How many overlays were hidden.
     */
    hideAllOverlays: function () {
        var komooMap = this;
        return komooMap.hideOverlays(komooMap.overlays);
    },

    /**
     * Makes visible some overlays.
     * @property {Array} overlays
     * @returns {Number} How many overlays were displayed.
     */
    showOverlays: function (overlays) {
        var komooMap = this;
        var ret = 0;
        $.each(overlays, function (key, overlay) {
            overlay.setVisible(true);
            ret++;
        });
        return ret;
    },

    /**
     * Makes visible overlays of specific type.
     * @property {String} type
     * @property {Array} optCategories
     * @property {boolean} optStrict
     * @returns {Number} How many overlays were displayed.
     */
    showOverlaysByType: function (type, optCategories, optStrict) {
        var komooMap = this;
        var overlays = komooMap.getOverlaysByType(type, optCategories, optStrict);
        return komooMap.showOverlays(overlays);
    },

    /**
     * Makes visible all overlays.
     * @returns {Number} How many overlays were displayed.
     */
    showAllOverlays: function () {
        var komooMap = this;
        return komooMap.showOverlays(komooMap.overlays);
    },

    /**
     * Remove all overlays from map.
     * @returns {void}
     */
    clear: function () {
        var komooMap = this;
        komooMap.initOverlaysByTypeObject();
        delete komooMap.loadedOverlays;
        delete komooMap.fetchedTiles;
        komooMap.loadedOverlays = {};
        komooMap.fetchedTiles = {};
        $.each(komooMap.overlays, function (key, overlay) {
            overlay.setMap(null);
            delete overlay;
        });
        if (komooMap.clusterer) {
            komooMap.clusterer.clearMarkers();
        }
        delete komooMap.overlays;
        komooMap.overlays = [];
    },

    deleteNode: function (e, komooMap) {
        var nodeWidth = 6;
        var proj = komooMap.googleMap.getProjection();
        var clickPoint = proj.fromLatLngToPoint(e.latLng);
        var poly = komooMap.currentOverlay;
        var minDist = 512;
        var selectedIndex = -1;
        var pathIndex = -1;
        var paths;
        if (poly.getPaths) {
            paths = poly.getPaths();
        } else if (poly.getPath) {
            paths = new google.maps.MVCArray([poly.getPath()]);
        } else {
            return false;
        }
        var nodeToDelete;
        var pathWithNode;
        paths.forEach(function (path, i) {
            for (var n = 0 ; n < path.getLength() ; n++) {
                var nodePoint = proj.fromLatLngToPoint(path.getAt(n));
                var dist = Math.sqrt(Math.pow(Math.abs(clickPoint.x - nodePoint.x), 2) + Math.pow(Math.abs(clickPoint.y - nodePoint.y), 2));
                if (dist < minDist) {
                    minDist = dist;
                    selectedIndex = n;
                    pathIndex = i;
                    nodeToDelete = path.getAt(n);
                    pathWithNode = path;
                }
            }
        });
        // Check if we're clicking inside the node
        var ovProj = komooMap.overlayView.getProjection();
        var clickPx = ovProj.fromLatLngToContainerPixel(e.latLng);
        var nodePx = ovProj.fromLatLngToContainerPixel(nodeToDelete);
        var xDist = Math.abs(nodePx.x - clickPx.x);
        var yDist = Math.abs(nodePx.y - clickPx.y);
        if (xDist < nodeWidth && yDist < nodeWidth) {
            pathWithNode.removeAt(selectedIndex);
            if (pathWithNode.getLength() == 0) {
                paths.removeAt(pathIndex);
            }
            return true;
        }
        return false;
    },

    /**
     * Set the current overlay and display the edit controls.
     * @param {google.maps.Polygon|google.maps.Polyline|null} overlay
     *        The overlay to be set as current or null to remove the selection.
     * @returns {void}
     */
    setCurrentOverlay: function (overlay) {
        var komooMap = this;
        // Marks only the current overlay as editable.
        if (this.currentOverlay && this.currentOverlay.setEditable) {
            this.currentOverlay.setEditable(false);
        }
        $('#komoo-map-add-button, #komoo-map-cut-out-button, #komoo-map-delete-button').hide();
        this.currentOverlay = overlay;
        if (this.currentOverlay && this.currentOverlay.setEditable &&
                this.currentOverlay.properties &&
                this.currentOverlay.properties.userCanEdit) {
            this.currentOverlay.setEditable(true);
            if (komooMap.currentOverlay.getPaths) {
                $('#komoo-map-add-button, #komoo-map-cut-out-button').show();
            }
        }
        if (this.currentOverlay) $('#komoo-map-delete-button').show();
    },

    /**
     * Enable or disable the drawing feature.
     * @param {boolean} editable
     *        true to enable the drawing feature and false to disable.
     * @returns {void}
     */
    setEditable: function (editable) {
        var komooMap = this;
        var options;
        komooMap.editable = editable;
        if (!komooMap.drawingManager) {
            komooMap._initDrawingManager();
        }
        if (editable) {  // Enable
            komooMap.drawingManagerOptions.drawingMode = null;
            if (komooMap.options.defaultDrawingControl) {
                komooMap.drawingManagerOptions.drawingControl = true;
            }
            komooMap.setCurrentOverlay(komooMap.currentOverlay);
            if (komooMap.editToolbar) {
                komooMap.editToolbar.show();
            }
            if (komooMap.mainPanel) {
                komooMap.mainPanel.show();
            }
        } else {  // Disable
            komooMap.drawingManagerOptions.drawingMode = null;
            if (komooMap.options.defaultDrawingControl) {
                komooMap.drawingManagerOptions.drawingControl = false;
            }
            if (komooMap.currentOverlay && komooMap.currentOverlay.setEditable) {
                komooMap.currentOverlay.setEditable(false);
            }
            if (komooMap.editToolbar) {
                komooMap.editToolbar.hide();
            }
            if (komooMap.mainPanel) {
                komooMap.mainPanel.hide();
            }
            komooMap.setEditMode(null);
        }
        if (komooMap.drawingManager) {
            komooMap.drawingManager.setOptions(komooMap.drawingManagerOptions);
        }
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
        var komooMap = this;
        if (!komooMap.streetView) {
            // Creates the StreetView object only when needed.
            komooMap._createStreetViewObject();
        }
        if (!position) {
            position = komooMap.googleMap.getCenter();
        }
        komooMap.streetView.setPosition(position);
        if (flag) {
            komooMap.streetViewPanel.show();
        } else {
            komooMap.streetViewPanel.hide();
        }
        komooMap.streetView.setVisible(flag);
    },

    /**
     * Use the HTML5 GeoLocation to set the user location as the map center.
     * @returns {void}
     */
    goToUserLocation: function () {
        var komooMap = this;
        var pos;
        if (google.loader.ClientLocation) { // Gets from google service
            pos = new google.maps.LatLng(google.loader.ClientLocation.latitude,
                                             google.loader.ClientLocation.longitude);
        }
        if (navigator.geolocation) { // Uses "HTML5"
            navigator.geolocation.getCurrentPosition(function(position) {
                pos = new google.maps.LatLng(position.coords.latitude,
                                                 position.coords.longitude);
                komooMap.googleMap.setCenter(pos);
            }, function () { // User denied the "HTML5" access so use the info from google
                if (pos) {
                    komooMap.googleMap.setCenter(pos);
                }
            });
        } else { // Dont support "HTML5" so use info from google
            if (pos) {
                komooMap.googleMap.setCenter(pos);
            }
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

    editOverlay: function (overlay) {
        var komooMap = this;
        if (!overlay.properties.userCanEdit) {
            return false;
        }
        if (overlay.setEditable) {
            overlay.setEditable(true);
        } else if (overlay.setDraggable) {
            overlay.setDraggable(true);
        }
        $('.map-panel-title', komooMap.addPanel).text(gettext('Edit'));
        komooMap.addPanel.css({'margin-top': '33px'});
        komooMap.addPanel.show();
        komooMap.setCurrentOverlay(overlay);
        return true;
    },

    /**
     * Attach some events to overlay.
     * @param {google.maps.Polygon|google.maps.Polyline} overlay
     * @returns {void}
     */
    _attachOverlayEvents: function (overlay) {
        // FIXME: InfoWindow configuration should not be done here because this is called n times (n = number of overlays loaded)
        var komooMap = this;
        if (overlay.getPaths) {
            // Removes stroke from polygons.
            overlay.setOptions({strokeOpacity: 0});
        }

        google.maps.event.addListener(overlay, 'rightclick', function (e) {
            if (this.properties && this.properties.userCanEdit &&
                    this == komooMap.currentOverlay) {
                if (!komooMap.overlayView) {
                    google.maps.event.trigger(komooMap.googleMap, 'projection_changed');
                }
                komooMap.deleteNode(e, komooMap);
            }
        });

        google.maps.event.addListener(overlay, 'click', function (e) {
            if (window.console) console.log('Clicked on overlay');
            if (komooMap.mode == 'selectcenter') {
                komooMap._emit_centerselected(e.latLng);
                return;
            }
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
                    var paths = this.getPaths();
                    l = paths.getLength();
                    paths.forEach(function (path, i) {
                        // Delete the correct path.
                        if (komoo.isPointInside(e.latLng, path)) {
                            paths.removeAt(i);
                            l--;
                        }
                    });
                }
                if (l === 0) {  // We had only one path, or the overlay wasnt a polygon.
                    this.setMap(null);
                } else {
                    komooMap.setCurrentOverlay(this);
                }
                // TODO: (IMPORTANT) Remove the overlay from komooMap.overlays
                komooMap.setEditMode(null);
                komooMap._emit_changed();
            } else {
                komooMap.setEditMode(null);
                komooMap.setCurrentOverlay(this);  // Select the clicked overlay
            }
        });

        google.maps.event.addListener(overlay, 'mousemove', function (e) {
            if (overlay.getPaths) {
                overlay.setOptions({strokeOpacity: 0.8});
            }

            if (komooMap.infoWindow.overlay == overlay || komooMap.addPanel.is(':visible') ||
                    !komooMap.options.enableInfoWindow) {
                return;
            }
            clearTimeout(komooMap.infoWindow.timer);
            komooMap.infoWindow.timer = setTimeout(function () {
                if (komooMap.infoWindow.isMouseover || komooMap.addPanel.is(':visible') || komooMap.mode == 'selectcenter') {
                    return;
                }
                komooMap.openInfoWindow(overlay, e.latLng);
            }, overlay.getPaths ? 800 : 200);
        });

        google.maps.event.addListener(overlay, 'mouseout', function (e) {
            if (overlay.getPaths) {
                overlay.setOptions({strokeOpacity: 0});
            }
            clearTimeout(komooMap.infoWindow.timer);
            if (!komooMap.infoWindow.isMouseover) {
                komooMap.infoWindow.timer = setTimeout(function () {
                    if (!komooMap.infoWindow.isMouseover) {
                        komooMap.infoWindow.close();
                        komooMap.infoWindow.overlay = undefined;
                    }
                }, 200);
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
                type: komooMap.type,
                name: 'Sem nome'
            };

            // Switch back to non-drawing mode after drawing a shape.
            komooMap.drawingManager.setDrawingMode(null);

            // Sets the custom image.
            if (e.overlay.setIcon) e.overlay.setIcon('/static/img/' + komooMap.type + '.png'); // FIXME: Hardcode is evil

            var path;
            if (e.overlay.getPath) path = e.overlay.getPath();

            if (e.type == google.maps.drawing.OverlayType.CIRCLE) {
                komooMap.radiusCircle = e.overlay;
            } else if ((komooMap.editMode == 'cutout' || komooMap.editMode == 'add') &&
                        e.overlay.getPaths) {
                // Gets the overlays path orientation.
                var paths = komooMap.currentOverlay.getPaths();
                // Gets the paths orientations.
                var sArea = google.maps.geometry.spherical.computeSignedArea(path);
                var sAreaAdded = google.maps.geometry.spherical.computeSignedArea(
                        paths.getAt(0));
                var orientation = sArea / Math.abs(sArea);
                var orientationAdded = sAreaAdded / Math.abs(sAreaAdded);
                // Verify the paths orientation.
                if ((orientation == orientationAdded && komooMap.editMode == 'cutout') ||
                        orientation != orientationAdded && komooMap.editMode == 'add') {
                    /* Reverse path orientation to correspond to the action  */
                    path = new google.maps.MVCArray(path.getArray().reverse());
                }
                paths.push(path);
                komooMap.currentOverlay.setPaths(paths);
                e.overlay.setMap(null);
                komooMap.setEditMode('draw');
            } else {
                komooMap.overlays.push(e.overlay);
                komooMap.newOverlays.push(e.overlay);
                // Listen events from drawn overlay.
                komooMap._attachOverlayEvents(e.overlay);
                komooMap.setCurrentOverlay(e.overlay);
            }
            if (path) {
                // Emit changed event when edit paths.
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
            // Adds new HTML elements to the map.
            var radiusButton = komoo.createMapButton('Radius', '', function (e) {
                komooMap.setEditMode('draw');
                if (komooMap.radiusCircle) komooMap.radiusCircle.setMap(null);
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.CIRCLE);
            });

            var polygonButton = komoo.createMapButton(gettext('Add shape'), gettext('Draw a shape'), function (e) {
                komooMap.setEditMode('draw');
                komooMap.setCurrentOverlay(null);  // Remove the overlay selection
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.POLYGON);
                if (komooMap.overlayOptions[komooMap.type]) {
                    var color = komooMap.overlayOptions[komooMap.type].color;
                    komooMap.drawingManagerOptions.polygonOptions.fillColor = color;
                    komooMap.drawingManagerOptions.polygonOptions.strokeColor = color;
                }
            }).attr('id', 'map-add-' + google.maps.drawing.OverlayType.POLYGON);

            var lineButton = komoo.createMapButton(gettext('Add line'), gettext('Draw a line'), function (e) {
                komooMap.setEditMode('draw');
                komooMap.setCurrentOverlay(null);  // Remove the overlay selection
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.POLYLINE);
                if (komooMap.overlayOptions[komooMap.type]) {
                    var color = komooMap.overlayOptions[komooMap.type].color;
                    komooMap.drawingManagerOptions.polylineOptions.strokeColor = color;
                }
            }).attr('id', 'map-add-' + google.maps.drawing.OverlayType.POLYLINE);

            var markerButton = komoo.createMapButton(gettext('Add point'), gettext('Add a marker'), function (e) {
                komooMap.setEditMode('draw');
                komooMap.setCurrentOverlay(null);  // Remove the overlay selection
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.MARKER);
            }).attr('id', 'map-add-' + google.maps.drawing.OverlayType.MARKER);

            var addMenu = komoo.createMapMenu(gettext('Add new...'), [polygonButton, lineButton, markerButton]);
            //komooMap.editToolbar.append(addMenu);
            komooMap.addItems = $('.map-container', addMenu);

            var addButton = komoo.createMapButton(gettext('Add'), gettext('Add another region'), function (e) {
                if (komooMap.editMode == 'add') {
                    komooMap.setEditMode('draw');
                } else {
                    komooMap.setEditMode('add');
                }
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.POLYGON);
            });
            addButton.hide();
            addButton.attr('id', 'komoo-map-add-button');
            komooMap.editToolbar.append(addButton);

            var cutOutButton = komoo.createMapButton(gettext('Cut out'), gettext('Cut out a hole from a region'), function (e) {
                if (komooMap.editMode == 'cutout') {
                    komooMap.setEditMode('draw');
                } else {
                    komooMap.setEditMode('cutout');
                }
                komooMap.drawingManager.setDrawingMode(
                        google.maps.drawing.OverlayType.POLYGON);
            });
            cutOutButton.hide();
            cutOutButton.attr('id', 'komoo-map-cut-out-button');
            komooMap.editToolbar.append(cutOutButton);

            var deleteButton = komoo.createMapButton(gettext('Delete'), gettext('Delete a region'), function (e) {
                if (komooMap.editMode == 'delete') {
                    komooMap.setEditMode('draw');
                } else {
                    komooMap.setEditMode('delete');
                }
                komooMap.drawingManagerOptions.drawingMode = null;
                komooMap.drawingManager.setOptions(komooMap.drawingManagerOptions);
            });
            deleteButton.hide();
            deleteButton.attr('id', 'komoo-map-delete-button');
            komooMap.editToolbar.append(deleteButton);

            komooMap.event.bind('editmode_changed', function(e, mode) {
                komooMap.infoWindow.close(); // Close the popup window
                // Set the correct button style when editMode was changed.
                addButton.removeClass('active');
                cutOutButton.removeClass('active');
                deleteButton.removeClass('active');
                if (mode == 'add') {
                    addButton.addClass('active');
                } else if (mode == 'cutout') {
                    cutOutButton.addClass('active');
                } else if (mode == 'delete') {
                    deleteButton.addClass('active');
                }
            });
        }
    },

    /**
     * @param {String} mode
     * @returns {void}
     */
    setMode: function (mode) {
        this.mode = mode;
        this.event.trigger('mmode_changed', mode);
    },

    /**
     * @param {String} mode
     * @returns {void}
     */
    setEditMode: function (mode) {
        this.editMode = mode;
        this.event.trigger('editmode_changed', mode);
    },

    /**
     * Initialize the Google Street View.
     * @returns {void}
     */
    _createStreetViewObject: function () {
        var options = {};
        this.streetView = new google.maps.StreetViewPanorama(
                this.streetViewPanel.get(0), options);
    },

    /**
     * @returns {JQuery}
     */
    _createMainPanel: function () {
        var komooMap = this;
        var panel = $('<div>').addClass('map-panel');
        var addMenu = $('<ul>').addClass('map-menu');

        var tabs = komoo.createMapTab([
            {title: gettext('Filter')},
            {title: gettext('Add')/*, content: addMenu*/}
        ]);

        // Only logged in users can add new items.
        if (!isAuthenticated) {
            var submenuItem = addMenu.append($('<li>').addClass('map-menuitem').text('Please log in.'));
            submenuItem.bind('click', function (){
                window.location = '/user/login'; // FIXME: Hardcode is evil
            });
            $.each(komooMap.options.regionTypes, function (i, type) {
                komooMap.overlayOptions[type.type] = type;
            });
        } else {
            $.each(komooMap.options.regionTypes, function (i, type) {
                komooMap.overlayOptions[type.type] = type;
                var item = $('<li>').addClass('map-menuitem');
                if (type.icon) {
                    var icon = $('<img>').attr({src: type.icon}).css('float', 'left');
                    if (type.disabled) icon.css('opacity', '0.3');
                    item.append(icon);
                }
                item.append($('<div>').text(type.title).attr('title', type.tooltip).css('padding-left', '30px'));
                var submenu = komooMap.addItems.clone(true).addClass('map-submenu');
                var submenuItems = $('div', submenu);
                submenuItems.removeClass('map-button').addClass('map-menuitem').hide(); // Change the class
                submenuItems.bind('click', function () {
                    $('.map-submenu', addMenu).hide();
                    $('.map-panel-title', komooMap.addPanel).text($(this).text());
                    $('.map-menuitem.selected', komooMap.mainPanel).removeClass('selected');
                    item.addClass('selected');
                    $('.map-menuitem:not(.selected)', komooMap.mainPanel).addClass('frozen');
                });
                if (type.disabled) item.addClass('disabled');
                item.css({
                    'position': 'relative'
                });
                submenu.css({
                    //'position': 'absolute',
                    'top': '0',
                    'z-index': '999999'
                });
                item.append(submenu);
                item.click(
                    function () { // Over
                        // Menu should not work if 'add' panel is visible.
                        if (komooMap.addPanel.is(':hidden') && !$(this).hasClass('disabled')) {
                            komooMap.type = type.type;
                            submenu.css({'left': item.outerWidth() + 'px'});
                            $.each(type.overlayTypes, function (key, overlayType) {
                                $('#map-add-' + overlayType, submenu).show();
                            });
                            submenu.toggle();
                        }
                    });
                addMenu.append(item);
                type.selector = item;
            });
        }

        panel.css({
            'margin': '10px 5px 10px 10px',
            'width': '180px'
        });

        panel.append(tabs.selector);

        google.maps.event.addListener(komooMap.drawingManager, 'drawingmode_changed',
            function (e){
                if (komooMap.drawingManager.drawingMode) {
                    komooMap.addPanel.show();
                }
            });


        komooMap.addMenu = addMenu;
        return panel;
    },

    /**
     * @returns {JQuery}
     */
    _createAddPanel: function () {
        var komooMap = this;
        var panel = $('<div>').addClass('map-panel');
        var content = $('<div>').addClass('content');
        var title = $('<div>').text(gettext('Title')).addClass('map-panel-title');
        var buttons = $('<div>').addClass('map-panel-buttons');
        var finishButton = $('<div>').text(gettext('Finish')).addClass('map-button');
        var cancelButton = $('<div>').text(gettext('Cancel')).addClass('map-button');

        function button_click () {
            $('.map-menuitem.selected', komooMap.addMenu).removeClass('selected');
            $('.frozen', komooMap.mainPanel).removeClass('frozen');
            komooMap.drawingManager.setDrawingMode(null);
            panel.hide();
        }
        cancelButton.bind('click', function () {
            button_click();
            if (komooMap.newOverlays) { // User drew a overlay, so remove it.
                $.each(komooMap.newOverlays, function (key, item) {
                    var overlay = komooMap.overlays.pop(); // The newly created overlay should be the last at array.
                    overlay.setMap(null);
                });
                komooMap.newOverlays = [];
            }
            komooMap.event.trigger('cancel_click');
            komooMap.type = null;
            komooMap.setEditMode(undefined);
        });
        finishButton.bind('click', function () {
            button_click();
            komooMap.event.trigger('finish_click', komooMap.overlayOptions[komooMap.type]);
            komooMap.type = null;
            komooMap.setEditMode(undefined);
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
            'margin': '10px',
            'width': '220px'
        });

        return panel.hide();
    },

    /**
     * Sets to the 'selectcenter' mode to user select the center point of radius filter.
     * Emits 'centerselected' event when done.
     * @param {function} optCallBack optional callback function. The callback parameters are 'latLng' and 'circle'.
     *                   'latLng' receives a google.maps.LatLng object. 'circle' receives google.maps.Circle object.
     * @returns {void}
     */
    selectCenter: function (optCallBack) {
        var komooMap = this;
        this.setMode('selectcenter');
        if (typeof optCallBack == 'function') {
            var handler = function (e, latLng, circle) {
                optCallBack(latLng, circle);
                komooMap.event.unbind('centerselected', handler);
            };
            komooMap.event.bind('centerselected', handler);
        }
    },

    /**
     * @returns {void}
     */
    _emit_mapclick: function (e) {
        this.event.trigger('mapclick', e);
    },

    /**
     * @returns {void}
     */
    _emit_overlayclick: function (e) {
        this.event.trigger('overlayclick', e);
    },

    /**
     * @returns {void}
     */
    _emit_centerselected: function (latLng) {
        var komooMap = this;
        if (!komooMap.radiusCircle) {
            komooMap.radiusCircle = new google.maps.Circle({
                    visible: true,
                    radius: 100,
                    fillColor: 'none',
                    strokeColor: '#ffbda8',
                    zIndex: 99999999999999999999
            });
            komooMap.radiusCircle.setMap(komooMap.googleMap);
        }
        if (!komooMap.centerMarker) {
            komooMap.centerMarker = new google.maps.Marker({visible: true});
            komooMap.centerMarker.setMap(komooMap.googleMap);
        }
        komooMap.centerMarker.setPosition(latLng);
        komooMap.radiusCircle.setCenter(latLng);
        komooMap.event.trigger('centerselected', [latLng, komooMap.radiusCircle]);
        komooMap.setMode(null);
    },

    /**
     * @returns {void}
     */
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
 * @returns {JQuery}
 */
komoo.createMapButton = function (name, title, onClick) {
    var selector = $('<div>').text(name).addClass('map-button');
    selector.attr('title', title);
    selector.bind('click', onClick);
    return selector;
};

/**
 * @returns {JQuery}
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
    selector.hover(function () { container.show(); },
                   function () { container.hide(); });
    return selector;
};

/**
 * @returns {JQuery}
 */
komoo.createMapTab = function (items) {
    var tabs = {
        items: {},
        selector: $('<div>'),
        tabsSelector: $('<div>').addClass('map-tabs'),
        containersSelector: $('<div>').addClass('map-container')
    };
    tabs.selector.append(tabs.tabsSelector, tabs.containersSelector);
    $.each(items, function (i, item) {
        var tab = {
            tabSelector: $('<div>').text(item.title).addClass('map-tab').css({'border': '0px'}),
            containerSelector: $('<div>').addClass('map-tab-container').hide()
        };
        if (item.content) tab.containerSelector.append(item.content);
        tab.tabSelector.click(function () {
            if (tabs.current && tabs.current != tab) {
                tabs.current.tabSelector.removeClass('selected');
                tabs.current.containerSelector.hide();
            }
            tabs.current = tab;
            tab.tabSelector.toggleClass('selected');
            tab.containerSelector.toggle();
        });

        tabs.items[item.title] = tab;
        tab.tabSelector.css({'width': 100 / items.length + '%'});
        tabs.tabsSelector.append(tab.tabSelector);
        tabs.containersSelector.append(tab.containerSelector);
    });
    return tabs;
};

/**
 * Creates a cookie and save it.
 * @param {String} name
 * @param {String | Number} value
 * @param {Number} days
 * @returns {void}
 */
komoo.createCookie = function (name, value, days) {
    var expires;
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    }
    else {
        expires = "";
    }
    document.cookie = name + "=" + value + expires + "; path=/";
};

/**
 * Reads a cookie.
 * @param {String} name
 * @returns {String}
 */
komoo.readCookie = function (name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1, c.length);
        }
        if (c.indexOf(nameEQ) === 0) {
            return c.substring(nameEQ.length, c.length);
        }
    }
    return null;
};

/**
 * Removes a cookie.
 * @param {String} name
 * @returns {void}
 */
komoo.eraseCookie = function (name) {
    createCookie(name, "", -1);
};
