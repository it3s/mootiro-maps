/**
 * View, create and edit regions on Google Maps.
 *
 * @name map.js
 * @fileOverview A simple way to use Google Maps.
 * @version 0.1.0b
 * @author Luiz Armesto
 * @copyright (c) 2012 it3s
 */

// TODO: Get from Django the static url to avoid hardcode some urls.
// TODO: Create a generic function to attach events to open/close info window.

/** @namespace */
var komoo = {};




/**
 * @name komoo.RegionType
 * @class Object that represents a item on 'Add' tab of main panel.
 * @property {String} type An internal identifier.
 * @property {String[]} categories
 * @property {String} title The text displayed to user as a menu item.
 * @property {String} tooltip The text displayed on mouse over.
 * @property {String} color
 * @property {String} icon The icon url.
 * @property {google.maps.drawing.OverlayType[]} overlayTypes The geometry options displayed as submenu.
 * @property {String} formUrl The url used to load the form via ajax.
 *           This occurs when user click on 'Finish' button.
 *           Please use dutils.urls.resolve instead of hardcode the address.
 * @property {boolean} disabled
 */

/**
 * Array of {@link komoo.RegionType} objects to populate the 'Add' tab of main panel.
 */
komoo.RegionTypes = [
    {
        type: 'community',
        categories: [],
        title: gettext('Community'),
        tooltip: gettext('Add Community'),
        color: '#ffdd22',
        icon: '/static/img/community.png',
        overlayTypes: [google.maps.drawing.OverlayType.POLYGON],
        formUrl: dutils.urls.resolve('new_community'),
        disabled: false
    },
    {
        type: 'need',
        categories: ['Education', 'Sport', 'Environment', 'Health', 'Housing',
                     'Local Economy', 'Social Service'], // FIXME: Hardcode is evil
        title: gettext('Needs'),
        tooltip: gettext('Add Need'),
        color: '#f42c5e',
        icon: '/static/img/need.png',
        overlayTypes: [google.maps.drawing.OverlayType.POLYGON,
                       google.maps.drawing.OverlayType.POLYLINE,
                       google.maps.drawing.OverlayType.MARKER],
        formUrl: dutils.urls.resolve('new_need',
            {community_slug: 'community_slug'}),
        disabled: false
    },
    {
        type: 'organizationbranch',
        categories: [],
        title: gettext('Organization'),
        tooltip: gettext('Add Organization'),
        color: '#3a61d6',
        icon: '/static/img/organization.png',
        overlayTypes: [google.maps.drawing.OverlayType.POLYGON],
        formUrl: dutils.urls.resolve('organization_new',
            {community_slug: 'community_slug'}),
        disabled: false
    },
    {
        type: 'resource',
        categories: [],
        title: gettext('Resource'),
        tooltip: gettext('Add Resource'),
        color: '#009fe3',
        icon: '/static/img/resource.png',
        overlayTypes: [google.maps.drawing.OverlayType.POLYGON,
                       google.maps.drawing.OverlayType.POLYLINE,
                       google.maps.drawing.OverlayType.MARKER],
        formUrl: dutils.urls.resolve('resource_new',
            {community_slug: 'community_slug'}),
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
        disabled: true
    }
];




/**
 * Options object to {@link komoo.Map}.
 *
 * @class
 * @property {boolen} [editable=true]  Define if the drawing feature will be enabled.
 * @property {boolean} [useGeoLocation=false] Define if the HTML5 GeoLocation will be used to set the initial location.
 * @property {boolean} [defaultDrawingControl=false] If true the controls from Google Drawing library are used.
 * @property {komoo.RegionType[]} [regionTypes=komoo.RegionTypes]
 * @property {boolean} [autoSaveLocation=false] Determines if the current location is saved to be displayed the next time the map is loaded.
 * @property {boolean} [enableInfoWindow=true] Shows informations on mouse over.
 * @property {boolean} [enableCluster=false] Cluster some points together.
 * @property {boolean} [debug=false]
 * @property {Object} [overlayOptions]
 * @property {google.maps.MapOptions} [googleMapOptions] The Google Maps map options.
 */
komoo.MapOptions = {
    editable: true,
    useGeoLocation: false,
    defaultDrawingControl: false,
    regionTypes: komoo.RegionTypes,
    autoSaveLocation: false,
    enableInfoWindow: true,
    enableCluster: true,
    fetchOverlays: true,
    debug: false,
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
        disableDefaultUI: false,
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
 * @class Object used to get overlays from server for each tile
 *
 * @param {komoo.Map} komooMap
 * @property {komoo.Map} komooMap
 * @property {google.maps.Size} tileSize The tile size. Default: 256x256
 * @property {number} [maxZoom=32]
 * @property {String} name
 * @property {String} alt
 */
komoo.ServerFetchMapType = function (komooMap) {
    this.komooMap = komooMap;
    this.tileSize = new google.maps.Size(256, 256);
    this.maxZoom = 32;
    this.name = 'Server Data';
    this.alt  = 'Server Data Tile Map Type';
};


komoo.ServerFetchMapType.prototype.releaseTile = function (tile) {
    var serverFetchMapType = this;
    if (this.komooMap.fetchedTiles[tile.tileKey]) {
        $.each(this.komooMap.fetchedTiles[tile.tileKey].overlays, function (key, overlay) {
            bounds = serverFetchMapType.komooMap.googleMap.getBounds();
            if (overlay.bounds) {
                if (!bounds.intersects(overlay.bounds)) {
                    overlay.setMap(null);
                } else {
                    serverFetchMapType.komooMap.keptOverlays.push(overlay);
                }
            } else if (overlay.getPosition) {
                if (bounds.contains(overlay.getPosition())) {
                    overlay.setMap(null);
                }
            }
        });
    }
};


komoo.ServerFetchMapType.prototype.getTile = function (coord, zoom, ownerDocument) {
    var me = this;
    var div = ownerDocument.createElement('DIV');
    var addr = this.getAddrLatLng(coord, zoom);
    div.tileKey = addr;
    if (this.komooMap.options.debug) {
        // Display debug info.
        $(div).css({
            'width': this.tileSize.width + 'px',
            'height': this.tileSize.height + 'px',
            'border': 'solid 1px #AAAAAA',
            'overflow': 'hidden',
            'font-size': '9px'
        });
    }

    // Verify if we already loaded this block.
    if (this.komooMap.fetchedTiles[addr]) {
        if (this.komooMap.options.debug) {
            // Display debug info.
            div.innerHTML = this.komooMap.fetchedTiles[addr].geojson;
        }
        $.each(this.komooMap.fetchedTiles[addr].overlays, function (key, overlay) {
            overlay.setMap(me.komooMap.googleMap);
            if (overlay.setIcon) {
                overlay.setIcon(me.komooMap.getOverlayIcon(overlay));
            }
            if (overlay.marker) {
                if (zoom < 13) {
                    overlay.setMap(null);
                } else {
                    overlay.setMap(me.komooMap.googleMap);
                }
            }
        });
        return div;
    }
    if (this.komooMap.options.fetchOverlays != false) {
        $.ajax({
            url: "/get_geojson?" + addr,
            dataType: 'json',
            type: 'GET',
            success: function (data, textStatus, jqXHR) {
                var overlays_ = [];
                var overlays = me.komooMap.loadGeoJSON(JSON.parse(data), false);
                me.komooMap.fetchedTiles[addr] = {
                    geojson: data,
                    overlays: overlays
                };
                if (me.komooMap.options.debug) {
                    // Display debug info.
                    div.innerHTML = data;
                    $(div).css('border', 'solid 1px #F00');
                }
                $.each(overlays, function (key, overlay) {
                    overlay.setMap(me.komooMap.googleMap);
                    if (overlay.setIcon) {
                        overlay.setIcon(me.komooMap.getOverlayIcon(overlay));
                    }
                    if (overlay.marker) {
                        if (zoom < 13) {
                            overlay.setMap(null);
                        } else {
                            overlay.setMap(me.komooMap.googleMap);
                        }
                    }
                });
            },
            error: function (jqXHR, textStatus, errorThrown) {
                if (window.console) console.error(textStatus);
                var serverError = $('#server-error');
                if (serverError.parent().length == 0) {
                    serverError = $('<div>').attr('id', 'server-error');
                    $('body').append(serverError);
                    var error = $('<div>').html(jqXHR.responseText)
                    serverError.append(error); // FIXME: This is not user friendly
                }
            }
        });
    }
    return div;
};


/**
 * Converts tile coords to LatLng and returns a url params.
 *
 * @param {google.maps.Point} coord Tile coordinates (x, y).
 * @param {number} zoom Zoom level.
 * @returns {String} The url params to get the data from server.
 */
komoo.ServerFetchMapType.prototype.getAddrLatLng = function (coord, zoom) {
    var serverFetchMapType = this;
    var numTiles = 1 << zoom;
    var projection = this.komooMap.googleMap.getProjection();
    var point1 = new google.maps.Point(
            (coord.x + 1) * this.tileSize.width / numTiles,
            coord.y * this.tileSize.width / numTiles);
    var point2 = new google.maps.Point(
            coord.x * this.tileSize.width / numTiles,
            (coord.y + 1) * this.tileSize.width / numTiles);
    var ne = projection.fromPointToLatLng(point1);
    var sw = projection.fromPointToLatLng(point2);
    return "bounds=" + ne.toUrlValue() + "," + sw.toUrlValue() + "&zoom=" + zoom;
};




/**
 * @name komoo.MultiMarkerOptions
 * @class
 * @property {google.maps.Marker[]} [markers]
 * @property {google.maps.LatLng[]} [positions]
 * @property {google.maps.Map} [map]
 * @property {boolean} [visible]
 * @property {boolean} [clickable]
 * @property {boolean} [draggable]
 * @property {string | google.maps.MarkerImage} [icon]
 * @property {number} [zIndex]
 */

/**
 * @class
 * @param {komoo.MultiMarkerOptions} [opt_options]
 */
komoo.MultiMarker = function (opt_options) {
    opt_options = opt_options || {};
    this.markers_ = new google.maps.MVCArray(opt_options.markers || []);
    this.positions_ = new google.maps.MVCArray(opt_options.positions || []);
    this.map_ = opt_options.map;
    this.visible_ = opt_options.visible;
    this.clickable_ = opt_options.clickable;
    this.draggable_ = opt_options.draggable;
    this.icon_ = opt_options.icon;
    this.zIndex = opt_options.zIndex || 0;
};


/**
 * @return {google.maps.LatLng[]}
 */
komoo.MultiMarker.prototype.getPositions = function () {
    this.positions_.clear();
    for (var i=0; i<this.markers_.getLength(); i++) {
        this.positions_.push(this.markers_.getAt(i).getPosition());
    }
    return this.positions_
};


/**
 * @param {google.maps.LatLng[]} positions The positions
 */
komoo.MultiMarker.prototype.setPositions = function (positions) {
    if (positions.length != this.markers_.getLength()) {
        // FIXME: Use a constant as exception.
        throw "Invalid length.";
    }
    this.positions_.clear();
    for (var i=0; i<this.markers_.getLength(); i++) {
        this.markers_.getAt(i).setPosition(positions[i]);
        this.positions_.push(positions[i]);
    }
};


/**
 * @param {google.maps.Marker} marker
 * @param {boolean} [opt_keep=false]
 */
komoo.MultiMarker.prototype.addMarker = function (marker, opt_keep) {
    var me = this;
    // TODO: verify if we already have added this marker.
    this.markers_.push(marker);
    if (!opt_keep) {
        // TODO: set the marker options;
        if (this.icon_) {
            marker.setIcon(this.icon_);
        }
    }
    /**
     * @name komoo.MultiMarker#click
     * @event
     */
    google.maps.event.addListener(marker, 'click', function (e) {
        google.maps.event.trigger(me, 'click', e, marker);
        });
    /**
     * @name komoo.MultiMarker#mouseover
     * @event
     */
    google.maps.event.addListener(marker, 'mouseover', function (e) {
        google.maps.event.trigger(me, 'mouseover', e, marker);
    });
    /**
     * @name komoo.MultiMarker#mouseout
     * @event
     */
    google.maps.event.addListener(marker, 'mouseout', function (e) {
        google.maps.event.trigger(me, 'mouseout', e, marker);
    });
    /**
     * @name komoo.MultiMarker#mousemove
     * @event
     */
    google.maps.event.addListener(marker, 'mousemove', function (e) {
        google.maps.event.trigger(me, 'mousemove', e, marker);
    });
};


/**
 * @param {google.maps.Marker[]} markers
 * @param {boolean} [opt_keep=false]
 */
komoo.MultiMarker.prototype.addMarkers = function (markers, opt_keep) {
    for (var i=0; i<markers.length; i++) {
        this.addMarker(markers[i], opt_keep);
    }
};


/**
 * @returns {google.maps.Marker[]}
 */
komoo.MultiMarker.prototype.getMarkers = function () {
    return this.markers_;
};


/**
 * @param {boolean} flag
 */
komoo.MultiMarker.prototype.setDraggable = function (flag) {
    for (var i=0; i<this.markers_.getLength(); i++) {
        this.markers_.getAt(i).setDraggable(flag);
    }
    this.draggable_ = flag;
};


/**
 * @returns {boolean}
 */
komoo.MultiMarker.prototype.getDraggable = function () {
    return this.draggable_;
};


/**
 * @param {google.maps.Map} map
 */
komoo.MultiMarker.prototype.setMap = function (map) {
    for (var i=0; i<this.markers_.getLength(); i++) {
        this.markers_.getAt(i).setMap(map);
    }
    this.map_ = map;
};


/**
 * @returns {google.maps.Map}
 */
komoo.MultiMarker.prototype.getMap = function () {
    return this.map_;
};


/**
 * @param {string | google.maps.MarkerIcon} icon
 */
komoo.MultiMarker.prototype.setIcon = function (icon) {
    for (var i=0; i<this.markers_.getLength(); i++) {
        this.markers_.getAt(i).setIcon(icon);
    }
    this.icon_ = icon;
};


/**
 * @returns {string | google.maps.MarkerIcon}
 */
komoo.MultiMarker.prototype.getIcon = function () {
    return this.icon_;
};




/** @namespace */
komoo.Mode = {};
/***/ komoo.Mode.NAVIGATE = 'navigate';
/***/ komoo.Mode.SELECT_CENTER = 'select_center';
/***/ komoo.Mode.DRAW = 'draw';




/** @namespace */
komoo.EditMode = {};
/***/ komoo.EditMode.NONE = null;
/***/ komoo.EditMode.DRAW = 'draw';
/***/ komoo.EditMode.ADD = 'add';
/***/ komoo.EditMode.CUTOUT = 'cutout';
/***/ komoo.EditMode.DELETE = 'delete';




/**
 * Wrapper for Google Maps map object with some helper methods.
 *
 * @class
 * @param {DOM} element The map canvas.
 * @param {komoo.MapOptions} options The options object.
 * @property {undefined | MarkerClusterer} clusterer A MarkerClusterer object used to cluster markers.
 * @property {google.maps.drawing.DrawingManager} drawingManager Drawing manager from Google Maps library.
 * @property {boolean} editable The status of the drawing feature.
 * @property {komoo.EditMode} editMode The current mode of edit feature. Possible values are 'cutout', 'add' and 'delete'.
 * @property {JQuery} editToolbar JQuery selector of edit toolbar.
 * @property {JQuery} event JQuery selector used to emit events.
 * @property {Object} fetchedTiles Cache the json and the overlays for each tile
 * @property {google.maps.Geocoder} geocoder  Google service to get addresses locations.
 * @property {google.maps.Map} googleMap The Google Maps map object.
 * @property {InfoBox | google.maps.InfoWindow} infoWindow
 * @property {Object} loadedOverlays Cache all overlays
 * @property {komoo.Mode} mode Possible values are null, 'new', 'edit'
 * @property {google.maps.MVCObject[]} newOverlays Array containing new overlays added by user.
 * @property {komoo.MapOptions} options The options object used to construct the komoo.Map object.
 * @property {Object} overlayOptions
 * @property {google.maps.MVCObject[]} overlays Array containing all overlays.
 * @property {google.maps.Circle} radiusCircle
 * @property {komoo.ServerFetchMapType} serverFetchMapType
 * @property {google.maps.StreetViewPanorama} streetView
 * @property {JQuery} streetViewPanel JQuery selector of Street View panel.
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
    this.mode = null;
    this.fetchedTiles = {};
    this.keptOverlays = [];
    this.loadedOverlays = {};
    this.options = $.extend(komoo.MapOptions, options);
    this.drawingManagerOptions = {};
    this.overlayOptions = {};
    this.overlays = [];
    this.loadedOverlays = {};
    this.overlaysByType = {};
    this.initOverlaysByTypeObject();
    this.newOverlays = [];
    // Creates a jquery selector to use the jquery events feature.
    this.event = $('<div>');
    // Creates the Google Maps object.
    this.googleMap = new google.maps.Map(element, googleMapOptions);
    // Uses Tiles to get data from server.
    this.serverFetchMapType = new komoo.ServerFetchMapType(this);
    this.googleMap.overlayMapTypes.insertAt(0, this.serverFetchMapType);
    this.initMarkerClusterer();
    // Create the simple version of toolbar.
    this.editToolbar = $('<div>').addClass('map-toolbar').css('margin', '5px');
    this.initInfoWindow();
    this.setEditable(this.options.editable);
    this.initCustomControl();
    this.initStreetView();
    if (this.options.useGeoLocation) {
        this.goToUserLocation();
    }
    this.useSavedMapType();
    this.handleEvents();
    // Geocoder is used to search locations by name/address.
    this.geocoder = new google.maps.Geocoder();
    if (komoo.onMapReady) {
        komoo.onMapReady(this);
    }
};


/**
 * Prepares the infoWindow property. Should not be called externally
 */
komoo.Map.prototype.initInfoWindow = function () {
    var komooMap = this;
    if (window.InfoBox) {  // Uses infoBox if available.
        this.infoWindow = new InfoBox({
            pixelOffset: new google.maps.Size(0, -20),
            closeBoxMargin: '10px',
            boxStyle: {
                background: 'url(/static/img/infowindow-arrow.png) no-repeat 0 10px', // TODO: Hardcode is evil
                width: '200px'
            }
        });
        google.maps.event.addDomListener(this.infoWindow, 'domready', function (e) {
            var closeBox = komooMap.infoWindow.div_.firstChild;
            $(closeBox).hide();  // Removes the close button.
            google.maps.event.addDomListener(closeBox, 'click', function (e) {
                // Detach the overlay from infowindow when close it.
                komooMap.infoWindow.overlay = undefined;
            });
        });
    } else {  // Otherwise uses the default InfoWindow.
        if (window.console) console.log('Using default info window.');
        this.infoWindow = new google.maps.InfoWindow();
    }

    this.infoWindow.title = $('<a>');
    this.infoWindow.body = $('<div>');
    this.infoWindow.content = $('<div>').addClass('map-infowindow-content');
    this.infoWindow.content.append(this.infoWindow.title);
    this.infoWindow.content.append(this.infoWindow.body);
    if (InfoBox) {
        this.infoWindow.content.css({
            background: 'white',
            padding: '10px',
            margin: '0 0 0 15px'
        });
    }
    this.infoWindow.content.hover(
        function (e) {
            clearTimeout(komooMap.infoWindow.timer);
            komooMap.infoWindow.isMouseover = true;
        },
        function (e) {
            clearTimeout(komooMap.infoWindow.timer);
            komooMap.infoWindow.isMouseover = false;
            komooMap.infoWindow.timer = setTimeout(function () {
                if (!komooMap.infoWindow.isMouseover) {
                    komooMap.closeInfoWindow();
                }
            }, 200);
        }
    );
    this.infoWindow.setContent(this.infoWindow.content.get(0));
};


/**
 * Gets overlay icon.
 * @param {google.maps.MVCObject} overlay
 * @param {boolean} [opt_highlighted=false]
 * @param {number} [opt_zoom]
 * @returns {String} The icon url
 */
komoo.Map.prototype.getOverlayIcon = function (overlay, opt_highlighted, opt_zoom) {
    var highlighted =  (opt_highlighted !== undefined) ? opt_highlighted : false;
    var zoom = (opt_zoom !== undefined) ? opt_zoom : this.googleMap.getZoom();
    var url = '/static/img/' + ((zoom >= 15) ? 'near' : 'far') + '/' + (highlighted ? 'highlighted/' : '');

    if (overlay.properties.categories && overlay.properties.categories[0]) {
        url += overlay.properties.categories[0].name.toLowerCase() + '.png';
    } else {
        url += overlay.properties.type + '.png';
    }
    return url;
};


/**
 * Closes the information window.
 */
komoo.Map.prototype.closeInfoWindow = function () {
    this.infoWindow.close();
    var overlay = this.infoWindow.overlay;
    if (overlay && overlay.highlighted) {
        if (overlay.setIcon) {
            overlay.setIcon(this.getOverlayIcon(overlay));
        }
        overlay.highlighted = false;
    }
    this.infoWindow.overlay = undefined;
};


/**
 * Display the information window.
 * @param {google.maps.MVCObject} overlay
 * @param {google.maps.LatLng} latLng
 * @param {String} [opt_content=""]
 */
komoo.Map.prototype.openInfoWindow = function (overlay, latLng, opt_content) {
    var url;
    if (opt_content) {
        this.infoWindow.title.attr('href', '#');
        this.infoWindow.title.text('');
        this.infoWindow.body.html(opt_content);
    } else if (overlay) {
        this.infoWindow.title.attr('href', '#');
        this.infoWindow.title.text(overlay.properties.name);
        this.infoWindow.body.html('');
        if (overlay.properties.type == 'community') {
            // FIXME: Move url to options object
            this.infoWindow.title.attr('href', dutils.urls.resolve('view_community', {
                        community_slug: overlay.properties.community_slug
                    })
            );
            var msg = ngettext('%s resident', '%s residents', overlay.properties.population);
            this.infoWindow.body.html('<ul><li>' + interpolate(msg, [overlay.properties.population]) + '</li></ul>');
        } else if (overlay.properties.type == 'resource') {
            url = dutils.urls.resolve('view_resource', {
                        community_slug: overlay.properties.community_slug,
                        id: overlay.properties.id
                    }).replace('//', '/');
            this.infoWindow.title.attr('href', url);
        }  else if (overlay.properties.type == 'organizationbranch') {
            url = dutils.urls.resolve('view_organization', {
                        community_slug: overlay.properties.community_slug,
                        organization_slug: overlay.properties.slug
                    }).replace('//', '/');
            this.infoWindow.title.attr('href', url);
        }  else {
            var slugname = overlay.properties.type + '_slug';
            var params = {'community_slug': overlay.properties.community_slug};
            params[slugname] = overlay.properties[slugname];
            url = dutils.urls.resolve('view_' + overlay.properties.type, params).replace('//', '/');
            this.infoWindow.title.attr('href', url);
        }

        this.infoWindow.overlay = overlay;
    }
    this.infoWindow.setPosition(latLng);
    this.infoWindow.open(this.googleMap);
};


/**
 * Prepares the CustomControl property. Should not be called externally
 */
komoo.Map.prototype.initCustomControl = function () {
    // Draw our custom control.
    if (!this.options.defaultDrawingControl) {
        this.mainPanel = this._createMainPanel();
        if (!this.editable) {
            this.mainPanel.hide();
        }
        //this.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
        //        this.mainPanel.get(0));
        this.addPanel = this._createAddPanel();
        this.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
                this.addPanel.get(0));
        // Adds editor toolbar.
        //this.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
        //        this.editToolbar.get(0));
    }
};


/**
 * Prepares the markerClusterer property. Should not be called externally.
 */
komoo.Map.prototype.initMarkerClusterer = function () {
    var komooMap = this;
    this.clusterMarkers = [];
    // Adds MarkerClusterer if available.
    if (window.MarkerClusterer && this.options.enableCluster) {
        if (window.console) console.log('Initializing Marker Clusterer support.');
        this.clusterer = new MarkerClusterer(this.googleMap, [], {
            gridSize: 20,
            maxZoom: 13,
            imagePath: '/static/img/cluster/communities',
            imageSizes: [27, 33, 38, 43, 49]
        });
        /*
        google.maps.event.addListener(this.clusterer, 'mouseover', function (c) {
            if (komooMap.addPanel.is(':visible') || !komooMap.options.enableInfoWindow) {
                return;
            }
            clearTimeout(komooMap.infoWindow.timer);
            komooMap.infoWindow.timer = setTimeout(function () {
                if (komooMap.infoWindow.isMouseover || komooMap.addPanel.is(':visible') || komooMap.mode == komoo.Mode.SELECT_CENTER) {
                    return;
                }
                komooMap.openInfoWindow(undefined, c.getCenter(), 'Cluster Info Window.'); // FIXME: Create the real content
            }, 1200);
        });

        google.maps.event.addListener(this.clusterer, 'click', function (c) {
            komooMap.closeInfoWindow();
        });

        google.maps.event.addListener(this.clusterer, 'mouseout', function (c) {
            clearTimeout(komooMap.infoWindow.timer);
            if (!komooMap.infoWindow.isMouseover) {
                komooMap.infoWindow.timer = setTimeout(function () {
                    if (!komooMap.infoWindow.isMouseover) {
                        komooMap.closeInfoWindow();
                    }
                }, 200);
            }
        });
        */
    }
};


/**
 * Prepares the overlaysByType property. Should not be called externally.
 */
komoo.Map.prototype.initOverlaysByTypeObject = function () {
    var komooMap = this;
    $.each(this.options.regionTypes, function (i, type) {
        komooMap.overlaysByType[type.type] = {};
        komooMap.overlaysByType[type.type]['uncategorized'] = [];
        if (type.categories.length) {
            $.each(type.categories, function(j, category) {
                komooMap.overlaysByType[type.type][category] = [];
            });
        }
    });
};


/**
 * Prepares the streetVies property. Should not be called externally.
 */
komoo.Map.prototype.initStreetView = function () {
    if (window.console) console.log('Initializing StreetView support.');
    this.streetViewPanel = $('<div>').addClass('map-panel');
    this.googleMap.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(
            this.streetViewPanel.get(0));
    this.streetViewPanel.hide();
};


/**
 * Connects some important events. Should not be called externally.
 */
komoo.Map.prototype.handleEvents = function () {
    var komooMap = this;
    if (window.console) console.log('Connecting map events.');
    // Listen Google Maps map events.
    google.maps.event.addListener(this.googleMap, 'click', function (e) {
        if (komooMap.addPanel.is(':hidden')) {
            komooMap.setCurrentOverlay(null);  // Remove the overlay selection
        }
        if (komooMap.mode == komoo.Mode.SELECT_CENTER) {
            komooMap._emit_center_selected(e.latLng);
        }
        komooMap._emit_mapclick(e);
    });

    google.maps.event.addListener(this.googleMap, 'idle', function () {
        if (komooMap.options.autoSaveLocation) {
            komooMap.saveLocation();
        }
    });

    google.maps.event.addListener(this.googleMap, 'idle', function () {
        // FIXME: This is not the best way to do the cluster feature.
        var zoom = komooMap.googleMap.getZoom();
        if (komooMap.clusterer) {
            if (zoom < 13) {
                komooMap.clusterer.addMarkers(komooMap.clusterMarkers);
            } else {
                komooMap.clusterer.clearMarkers();
            }
        }
    });

    google.maps.event.addListener(this.googleMap, 'zoom_changed', function () {
        $.each(komooMap.keptOverlays, function (key, overlay) {
            overlay.setMap(null);
        });
        komooMap.keptOverlays = [];
    });
    google.maps.event.addListener(this.googleMap, 'projection_changed', function () {
        komooMap.projection = komooMap.googleMap.getProjection();
        komooMap.overlayView = new google.maps.OverlayView();
        komooMap.overlayView.draw = function () { };
        komooMap.overlayView.onAdd = function (d) { };
        komooMap.overlayView.setMap(komooMap.googleMap);
    });

    google.maps.event.addListener(this.googleMap, 'rightclick', function (e) {
        if (!komooMap.overlayView) {
            google.maps.event.trigger(komooMap.googleMap, 'projection_changed');
        }
        var overlay = komooMap.currentOverlay;
        if (overlay && overlay.properties &&
                overlay.properties.userCanEdit) {
            komooMap.deleteNode(e);
        }
    });

    google.maps.event.addListener(this.googleMap, 'maptypeid_changed', function () {
        komooMap.saveMapType();
    });
};


komoo.Map.prototype.getVisibleOverlays = function () {
    var bounds = this.googleMap.getBounds();
    var overlays = [];
    $.each(this.overlays, function (key, overlay) {
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
};


/**
 * Saves the map location to cookie
 * @property {google.maps.LatLng} center
 */
komoo.Map.prototype.saveLocation = function (center) {
    if (!center) {
        center = this.googleMap.getCenter();
    }
    var zoom = this.googleMap.getZoom();
    komoo.createCookie('lastLocation', center.toUrlValue(), 90);
    komoo.createCookie('lastZoom', zoom, 90);
};


/**
 * Loads the location saved in a cookie and go to there.
 * @see komoo.Map.saveLocation
 * @returns {boolean}
 */
komoo.Map.prototype.goToSavedLocation = function () {
    var lastLocation = komoo.readCookie('lastLocation');
    var zoom = parseInt(komoo.readCookie('lastZoom'), 10);
    if (lastLocation && zoom) {
        lastLocation = lastLocation.split(',');
        var center = new google.maps.LatLng(lastLocation[0], lastLocation[1]);
        this.googleMap.setCenter(center);
        this.googleMap.setZoom(zoom);
        return true;
    }
    return false;
};


/**
 * Saves the map type to cookie
 * @property {google.maps.MapTypeId|String} mapType
 */
komoo.Map.prototype.saveMapType = function (mapType) {
    if (!mapType) {
        mapType = this.googleMap.getMapTypeId();
    }
    komoo.createCookie('mapType', mapType, 90);
};


/**
 * Use the map type saved in a cookie.
 * @see komoo.Map.saveMapType
 * @returns {boolean}
 */
komoo.Map.prototype.useSavedMapType = function () {
    var mapType = komoo.readCookie('mapType');
    if (mapType) {
        this.googleMap.setMapTypeId(mapType);
        return true;
    }
    return false;
};


/**
 * Load the features from geoJSON into the map.
 * @param {json} geoJSON The json that will be loaded.
 * @param {boolean} panTo If true pan to the region where overlays are.
 * @param {boolean} [opt_attach=true]
 * @returns {google.maps.MVCObject[]}
 */
komoo.Map.prototype.loadGeoJSON = function (geoJSON, panTo, opt_attach) {
    // TODO: Use the correct color
    // TODO: Add a hidden marker for each polygon/polyline
    // TODO: Document the geoJSON properties:
    // - userCanEdit
    // - type (community, need...)
    var komooMap = this;
    var featureCollection;
    var overlays = [];

    if (opt_attach === undefined) {
        opt_attach = true;
    }

    var polygonOptions = $.extend({
        clickable: true,
        editable: false,
        zIndex: 1
    }, this.options.overlayOptions);
    var polylineOptions = $.extend({
        clickable: true,
        editable: false,
        zIndex: 3
    }, this.options.overlayOptions);
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
            polygonOptions.zIndex = feature.properties.type == 'community' ? 1 : 2
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
        /*}  else if (geometry.type == 'Point') {
            overlay = new google.maps.Marker(markerOptions);
            var pos = geometry.coordinates;
            var latLng = new google.maps.LatLng(pos[0], pos[1]);
            overlay.setPosition(latLng);
            overlay.setIcon(komooMap.getOverlayIcon(feature));
            if (panTo) {
                komooMap.googleMap.setCenter(latLng);
            }
        */} else if (geometry.type == 'MultiPoint' || geometry.type == 'Point') {
            overlay = new komoo.MultiMarker();
            var markers = [];
            var coordinates = geometry.type == 'MultiPoint' ? geometry.coordinates : [geometry.coordinates];
            $.each(coordinates, function (key, pos) {
                var marker = new google.maps.Marker(markerOptions);
                var latLng = new google.maps.LatLng(pos[0], pos[1]);
                marker.setPosition(latLng);
                markers.push(marker);
                bounds = getBounds(pos);
            });
            overlay.addMarkers(markers);
            overlay.setIcon(komooMap.getOverlayIcon(feature));
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
            if (opt_attach) {
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
                if (overlay.properties.type == 'community' && !overlay.marker) {
                    overlay.marker = new google.maps.Marker({
                            visible: true,
                            clickable: true
                    });
                    overlay.marker.setPosition(overlay.bounds.getCenter());
                    overlay.marker.setIcon(komooMap.getOverlayIcon(overlay));
                    google.maps.event.addListener(overlay.marker, 'click', function () {
                        komooMap.googleMap.fitBounds(overlay.bounds);
                    });
                    komooMap.clusterMarkers.push(overlay.marker);
                    // TODO: Add mouseover handler to open info window
                }
                n = null;
                w = null;
                s = null;
                e = null;
            }
        }
    });
    if (panTo && bounds) {
        this.googleMap.fitBounds(new google.maps.LatLngBounds(
                new google.maps.LatLng(bounds[0][0], bounds[0][1]),
                new google.maps.LatLng(bounds[1][0], bounds[1][1])
        ));
    }

    this._emit_geojson_loaded(geoJSON);
    return overlays;
};


/**
 * Create a GeoJSON with the map's overlays.
 * @param {boolean} newOnly
 * @returns {json}
 */
komoo.Map.prototype.getGeoJSON = function (options) {
    // TODO: Create a default options object
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
        list = this.newOverlays;
    } else if (options.currentOnly) {
        list = [this.currentOverlay];
    } else {
        list = this.overlays;
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
                path.forEach(function (pos, k) {
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
        } else if (overlay.getPositions) { // Overlay isa a multipoint
            feature.geometry.type = 'MultiPoint';
            overlay.getPositions().forEach(function (pos, j) {
                coords.push([pos.lat(), pos.lng()]);
            });
        }
        feature.properties = overlay.properties;
        if (feature.geometry.coordinates.length)  {
            if (geoJSON.features) geoJSON.features.push(feature);
            if (geoJSON.geometries) geoJSON.geometries.push(feature.geometry);
        }
    });
    return geoJSON;
};


/**
 * Gets a list of overlays of specific type.
 * @param {String} type
 * @param {String[]} [opt_categories=[]]
 * @param {boolean} [opt_strict=false]
 * @returns {google.maps.MVCObject[]} Overlays that matches the parameters.
 */
komoo.Map.prototype.getOverlaysByType = function (type, opt_categories, opt_strict) {
    var komooMap = this;
    var overlays = [];
    var categories = opt_categories;
    if (!this.overlaysByType[type]) {
        return false;
    }
    if (!categories) {
        categories = [];
        $.each(this.overlaysByType[type], function (category, overlays) {
            categories.push(category);
        });
    } else if (categories.length === 0) {
        categories = ['uncategorized'];
    }
    $.each(categories, function (key, category) {
        if (komooMap.overlaysByType[type][category]) {
            $.each(komooMap.overlaysByType[type][category], function (key, overlay) {
                if (!opt_strict || !overlay.properties.categories || overlay.properties.categories.length == 1) {
                    overlays.push(overlay);
                }
            });
        }
    });
    return overlays;
};


/**
 * Hides some overlays.
 * @property {google.maps.MVCObject[]} overlays
 * @returns {number} How many overlays were hidden.
 */
komoo.Map.prototype.hideOverlays = function (overlays) {
    var ret = 0;
    $.each(overlays, function (key, overlay) {
        overlay.setVisible(false);
        ret++;
    });
    return ret;
};


/**
 * Hides overlays of specific type.
 * @param {String} type
 * @param {String[]} [opt_categories=[]]
 * @param {boolean} [opt_strict=false]
 * @returns {number} How many overlays were hidden.
 */
komoo.Map.prototype.hideOverlaysByType = function (type, opt_categories, opt_strict) {
    var overlays = this.getOverlaysByType(type, opt_categories, opt_strict);
    return this.hideOverlays(overlays);
};


/**
 * Hides all overlays.
 * @returns {number} How many overlays were hidden.
 */
komoo.Map.prototype.hideAllOverlays = function () {
    return this.hideOverlays(this.overlays);
};


/**
 * Makes visible some overlays.
 * @property {google.maps.MVCObject[]} overlays
 * @returns {number} How many overlays were displayed.
 */
komoo.Map.prototype.showOverlays = function (overlays) {
    var ret = 0;
    $.each(overlays, function (key, overlay) {
        overlay.setVisible(true);
        ret++;
    });
    return ret;
};


/**
 * Makes visible overlays of specific type.
 * @param {String} type
 * @param {String[]} [opt_categories=[]]
 * @param {boolean} [opt_strict=false]
 * @returns {number} How many overlays were displayed.
 */
komoo.Map.prototype.showOverlaysByType = function (type, opt_categories, opt_strict) {
    var overlays = this.getOverlaysByType(type, opt_categories, opt_strict);
    return this.showOverlays(overlays);
};


/**
 * Makes visible all overlays.
 * @returns {number} How many overlays were displayed.
 */
komoo.Map.prototype.showAllOverlays = function () {
    return this.showOverlays(this.overlays);
};


/**
 * Remove all overlays from map.
 */
komoo.Map.prototype.clear = function () {
    this.initOverlaysByTypeObject();
    delete this.loadedOverlays;
    delete this.fetchedTiles;
    this.loadedOverlays = {};
    this.fetchedTiles = {};
    $.each(this.overlays, function (key, overlay) {
        overlay.setMap(null);
        delete overlay;
    });
    if (this.clusterer) {
        this.clusterer.clearMarkers();
    }
    delete this.overlays;
    this.overlays = [];
};


komoo.Map.prototype.deleteNode = function (e) {
    var nodeWidth = 6;
    var proj = this.googleMap.getProjection();
    var clickPoint = proj.fromLatLngToPoint(e.latLng);
    var poly = this.currentOverlay;
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
    var ovProj = this.overlayView.getProjection();
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
};


/**
 * Set the current overlay and display the edit controls.
 * @param {google.maps.Polygon|google.maps.Polyline|null} overlay
 *        The overlay to be set as current or null to remove the selection.
 */
komoo.Map.prototype.setCurrentOverlay = function (overlay) {
    // Marks only the current overlay as editable.
    if (this.currentOverlay && this.currentOverlay.setEditable) {
        this.currentOverlay.setEditable(false);
    }
    $('#komoo-map-add-button, #komoo-map-cut-out-button, #komoo-map-delete-button').hide();
    this.currentOverlay = overlay;
    if (this.currentOverlay && this.currentOverlay.properties &&
            this.currentOverlay.properties.userCanEdit) {
        if (this.currentOverlay.setEditable) {
            this.currentOverlay.setEditable(true);
        }
        if (this.currentOverlay.getPaths) {
            this.drawingMode_ = google.maps.drawing.OverlayType.POLYGON;
            $('#komoo-map-cut-out-button').show();
        } else if (this.currentOverlay.getPath) {
            this.drawingMode_ = google.maps.drawing.OverlayType.POLYLINE;
        } else {
            this.drawingMode_ = google.maps.drawing.OverlayType.MARKER;
        }
        $('#komoo-map-add-button, #komoo-map-delete-button').show();
    }
};


/**
 * Enable or disable the drawing feature.
 * @param {boolean} editable
 *        true to enable the drawing feature and false to disable.
 */
komoo.Map.prototype.setEditable = function (editable) {
    var options;
    this.editable = editable;
    if (!this.drawingManager) {
        this._initDrawingManager();
    }
    if (editable) {  // Enable
        this.drawingManagerOptions.drawingMode = null;
        if (this.options.defaultDrawingControl) {
            this.drawingManagerOptions.drawingControl = true;
        }
        this.setCurrentOverlay(this.currentOverlay);
        if (this.editToolbar) {
            this.editToolbar.show();
        }
        if (this.mainPanel) {
            this.mainPanel.show();
        }
    } else {  // Disable
        this.drawingManagerOptions.drawingMode = null;
        if (this.options.defaultDrawingControl) {
            this.drawingManagerOptions.drawingControl = false;
        }
        if (this.currentOverlay && this.currentOverlay.setEditable) {
            this.currentOverlay.setEditable(false);
        }
        if (this.editToolbar) {
            this.editToolbar.hide();
        }
        if (this.mainPanel) {
            this.mainPanel.hide();
        }
        this.setEditMode(null);
    }
    if (this.drawingManager) {
        this.drawingManager.setOptions(this.drawingManagerOptions);
    }
};


/**
 * Show a box containing the Google Street View layer.
 * @param {boolean} flag
 *        Sets to 'true' to make Street View visible or 'false' to hide.
 * @param {google.maps.LatLng} position
 */
komoo.Map.prototype.setStreetView = function (flag, position) {
    // FIXME: Add close button to the Street View panel
    // TODO: Define the panel position and size
    if (!this.streetView) {
        // Creates the StreetView object only when needed.
        this._createStreetViewObject();
    }
    if (!position) {
        position = this.googleMap.getCenter();
    }
    this.streetView.setPosition(position);
    if (flag) {
        this.streetViewPanel.show();
    } else {
        this.streetViewPanel.hide();
    }
    this.streetView.setVisible(flag);
};


/**
 * Use the HTML5 GeoLocation to set the user location as the map center.
 */
komoo.Map.prototype.goToUserLocation = function () {
    var pos;
    if (google.loader.ClientLocation) { // Gets from google service
        pos = new google.maps.LatLng(google.loader.ClientLocation.latitude,
                                         google.loader.ClientLocation.longitude);
    }
    if (navigator.geolocation) { // Uses "HTML5"
        navigator.geolocation.getCurrentPosition(function(position) {
            pos = new google.maps.LatLng(position.coords.latitude,
                                             position.coords.longitude);
            this.googleMap.setCenter(pos);
        }, function () { // User denied the "HTML5" access so use the info from google
            if (pos) {
                this.googleMap.setCenter(pos);
            }
        });
    } else { // Dont support "HTML5" so use info from google
        if (pos) {
            this.googleMap.setCenter(pos);
        }
    }
};


/**
 * Go to an address or to latitude, longitude position.
 * @param {String|google.maps.LatLng|number[]} position
 *        An address or a pair latitude, longitude.
 */
komoo.Map.prototype.goTo = function (position) {
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
            region: this.region
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
};


/**
 * Alias to {@link komoo.Map.goTo}.
 * @see komoo.Map.goTo
 */
komoo.Map.prototype.panTo = function (position) {
    return this.goTo(position);
};


komoo.Map.prototype.editOverlay = function (overlay) {
    if (!overlay.properties || !overlay.properties.userCanEdit) {
        return false;
    }
    if (overlay.setEditable) {
        overlay.setEditable(true);
    } else if (overlay.setDraggable) {
        overlay.setDraggable(true);
    }
    this.type = overlay.properties.type;
    $('.map-panel-title', this.addPanel).text(gettext('Edit'));
    this.addPanel.css({'margin-top': '33px'});
    this.addPanel.show();
    this.setCurrentOverlay(overlay);
    return true;
};


/**
 * Attach some events to overlay.
 * @param {google.maps.Polygon|google.maps.Polyline} overlay
 */
komoo.Map.prototype._attachOverlayEvents = function (overlay) {
    // FIXME: InfoWindow configuration should not be done here because this is called n times (n = number of overlays loaded)
    var komooMap = this;
    if (overlay.getPaths) {
        // Removes stroke from polygons.
        overlay.setOptions({strokeOpacity: 0});
    }

    google.maps.event.addListener(overlay, 'rightclick', function (e) {
        var overlay_ = this;
        if (overlay_.properties && overlay_.properties.userCanEdit &&
                overlay_ == komooMap.currentOverlay) {
            if (!komooMap.overlayView) {
                google.maps.event.trigger(komooMap.googleMap, 'projection_changed');
            }
            komooMap.deleteNode(e);
        }
    });

    google.maps.event.addListener(overlay, 'click', function (e, o) {
        var overlay_ = this;
        if (window.console) console.log('Clicked on overlay');
        if (komooMap.mode == komoo.Mode.SELECT_CENTER) {
            komooMap._emit_center_selected(e.latLng);
            return;
        }
        if (komooMap.addPanel.is(':visible') && overlay_ != komooMap.currentOverlay) {
            if (window.console) console.log('Clicked on unselected overlay');
            if (!overlay_.properties.userCanEdit) {
                return;
            }
        }
        if (komooMap.editMode == komoo.EditMode.DELETE && overlay_.properties &&
                overlay_.properties.userCanEdit) {
                komooMap.setCurrentOverlay(null);
            var l = 0;
            if (overlay_.getPaths) {  // Clicked on polygon.
                var paths = overlay_.getPaths();
                l = paths.getLength();
                paths.forEach(function (path, i) {
                    // Delete the correct path.
                    if (komoo.isPointInside(e.latLng, path)) {
                        paths.removeAt(i);
                        l--;
                    }
                });
            } else if (overlay_.getMarkers) {
                var markers = overlay.getMarkers();
                l = markers.getLength();
                if (o) {
                    markers.forEach(function (marker, i) {
                        if (marker == o) {
                            markers.removeAt(i);
                            marker.setMap(null);
                            l--;
                        }
                    });
                }
            }
            if (l === 0) {  // We had only one path, or the overlay wasnt a polygon.
                overlay_.setMap(null);
            } else {
                komooMap.setCurrentOverlay(overlay_);
            }
            // TODO: (IMPORTANT) Remove the overlay from komooMap.overlays
            komooMap.setEditMode(null);
            komooMap._emit_changed();
        } else {
            komooMap.setEditMode(null);
            komooMap.setCurrentOverlay(overlay_);  // Select the clicked overlay
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
            if (komooMap.infoWindow.isMouseover || komooMap.addPanel.is(':visible') || komooMap.mode == komoo.Mode.SELECT_CENTER) {
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
                    komooMap.closeInfoWindow();
                }
            }, 200);
        }
    });
};


/**
 * Initialize the Google Maps Drawing Manager.
 */
komoo.Map.prototype._initDrawingManager = function () {
    var komooMap = this;
    var controlsPosition = google.maps.ControlPosition.TOP_LEFT;

    this.drawingManagerOptions = {
        map: this.googleMap,
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
        }, this.options.overlayOptions),
        polylineOptions: $.extend({
            clickable: true,
            editable: false
        }, this.options.overlayOptions),
        circleOptions: {
            fillColor: 'white',
            fillOpacity: 0.15,
            editable: true,
            zIndex: -1
        },
        drawingMode: google.maps.drawing.OverlayType.POLYGON
    };
    this.drawingManager = new google.maps.drawing.DrawingManager(
            this.drawingManagerOptions);
    google.maps.event.addListener(this.drawingManager,
            'overlaycomplete', function (e) {
        e.overlay.properties = {
            userCanEdit: true,
            type: komooMap.type,
            name: 'Sem nome'
        };

        // Switch back to non-drawing mode after drawing a shape.
        komooMap.drawingManager.setDrawingMode(null);

        // Sets the custom image.
        if (e.overlay.setIcon) {
            e.overlay.setIcon(komooMap.getOverlayIcon(e.overlay));
        }

        var path;
        if (e.overlay.getPath) {
            path = e.overlay.getPath();
        }

        if ((komooMap.editMode == komoo.EditMode.CUTOUT || komooMap.editMode == komoo.EditMode.ADD) &&
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
            if ((orientation == orientationAdded && komooMap.editMode == komoo.EditMode.CUTOUT) ||
                    orientation != orientationAdded && komooMap.editMode == komoo.EditMode.ADD) {
                /* Reverse path orientation to correspond to the action  */
                path = new google.maps.MVCArray(path.getArray().reverse());
            }
            paths.push(path);
            komooMap.currentOverlay.setPaths(paths);
            e.overlay.setMap(null);
            komooMap.setEditMode(komoo.EditMode.DRAW);
        } else if (komooMap.editMode == komoo.EditMode.ADD && e.overlay.getPosition) {
            komooMap.currentOverlay.addMarker(e.overlay);
            komooMap.setEditMode(komoo.EditMode.DRAW);
        } else if (e.overlay.getPosition) {
            // FIXME: DRY
            var overlay = new komoo.MultiMarker();
            overlay.addMarker(e.overlay);
            overlay.setMap(komooMap.googleMap);
            overlay.properties = {userCanEdit: true};
            komooMap.overlays.push(overlay);
            komooMap.newOverlays.push(overlay);
            // Listen events from drawn overlay.
            komooMap._attachOverlayEvents(overlay);
            komooMap.setCurrentOverlay(overlay);
            komooMap.setEditMode(komoo.EditMode.DRAW);
        } else {
            e.overlay.properties = {userCanEdit: true};
            komooMap.overlays.push(e.overlay);
            komooMap.newOverlays.push(e.overlay);
            // Listen events from drawn overlay.
            komooMap._attachOverlayEvents(e.overlay);
            komooMap.setCurrentOverlay(e.overlay);
            komooMap.setEditMode(komoo.EditMode.DRAW);
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

    if (!this.options.defaultDrawingControl) {
        // Adds new HTML elements to the map.
        var polygonButton = komoo.createMapButton(gettext('Add shape'), gettext('Draw a shape'), function (e) {
            komooMap.setEditMode(komoo.EditMode.DRAW);
            komooMap.setCurrentOverlay(null);  // Remove the overlay selection
            komooMap.drawingMode_ = google.maps.drawing.OverlayType.POLYGON;
            komooMap.drawingManager.setDrawingMode(komooMap.drawingMode_);
            if (komooMap.overlayOptions[komooMap.type]) {
                var color = komooMap.overlayOptions[komooMap.type].color;
                komooMap.drawingManagerOptions.polygonOptions.fillColor = color;
                komooMap.drawingManagerOptions.polygonOptions.strokeColor = color;
            }
        }).attr('id', 'map-add-' + google.maps.drawing.OverlayType.POLYGON);

        var lineButton = komoo.createMapButton(gettext('Add line'), gettext('Draw a line'), function (e) {
            komooMap.setEditMode(komoo.EditMode.DRAW);
            komooMap.setCurrentOverlay(null);  // Remove the overlay selection
            komooMap.drawingMode_ = google.maps.drawing.OverlayType.POLYLINE;
            komooMap.drawingManager.setDrawingMode(komooMap.drawingMode_);
            if (komooMap.overlayOptions[komooMap.type]) {
                var color = komooMap.overlayOptions[komooMap.type].color;
                komooMap.drawingManagerOptions.polylineOptions.strokeColor = color;
            }
        }).attr('id', 'map-add-' + google.maps.drawing.OverlayType.POLYLINE);

        var markerButton = komoo.createMapButton(gettext('Add point'), gettext('Add a marker'), function (e) {
            komooMap.setEditMode(komoo.EditMode.DRAW);
            komooMap.setCurrentOverlay(null);  // Remove the overlay selection
            komooMap.drawingMode_ = google.maps.drawing.OverlayType.MARKER;
            komooMap.drawingManager.setDrawingMode(komooMap.drawingMode_);
        }).attr('id', 'map-add-' + google.maps.drawing.OverlayType.MARKER);

        var addMenu = komoo.createMapMenu(gettext('Add new...'), [polygonButton, lineButton, markerButton]);
        //this.editToolbar.append(addMenu);
        this.addItems = $('.map-container', addMenu);

        var addButton = komoo.createMapButton(gettext('Add'), gettext('Add another region'), function (e) {
            if (komooMap.editMode == komoo.EditMode.ADD) {
                komooMap.setEditMode(komoo.EditMode.DRAW);
            } else {
                komooMap.setEditMode(komoo.EditMode.ADD);
            }
            komooMap.drawingManager.setDrawingMode(komooMap.drawingMode_);
        });
        addButton.hide();
        addButton.attr('id', 'komoo-map-add-button');
        this.editToolbar.append(addButton);

        var cutOutButton = komoo.createMapButton(gettext('Cut out'), gettext('Cut out a hole from a region'), function (e) {
            if (komooMap.editMode == komoo.EditMode.CUTOUT) {
                komooMap.setEditMode(komoo.EditMode.DRAW);
            } else {
                komooMap.setEditMode(komoo.EditMode.CUTOUT);
            }
            komooMap.drawingManager.setDrawingMode(komooMap.drawingMode_);
        });
        cutOutButton.hide();
        cutOutButton.attr('id', 'komoo-map-cut-out-button');
        this.editToolbar.append(cutOutButton);

        var deleteButton = komoo.createMapButton(gettext('Delete'), gettext('Delete a region'), function (e) {
            if (komooMap.editMode == komoo.EditMode.DELETE) {
                komooMap.setEditMode(komoo.EditMode.DRAW);
            } else {
                komooMap.setEditMode(komoo.EditMode.DELETE);
            }
            komooMap.drawingManagerOptions.drawingMode = null;
            komooMap.drawingManager.setOptions(komooMap.drawingManagerOptions);
        });
        deleteButton.hide();
        deleteButton.attr('id', 'komoo-map-delete-button');
        this.editToolbar.append(deleteButton);

        this.event.bind('editmode_changed', function(e, mode) {
            komooMap.closeInfoWindow();
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
};


/**
 * @param {String} mode
 */
komoo.Map.prototype.setMode = function (mode) {
    this.mode = mode;
    if (this.mode != komoo.Mode.DRAW) {
        this.setEditMode(komoo.EditMode.NONE);
    }
    /**
     * @name komoo.Map#mode_changed
     * @event
     */
    this.event.trigger('mode_changed', mode);
};


/**
 * @param {String} mode
 */
komoo.Map.prototype.setEditMode = function (mode) {
    this.editMode = mode;
    if (this.editMode != komoo.EditMode.NONE && this.mode != komoo.Mode.DRAW) {
        this.setMode(komoo.Mode.DRAW);
    }
    /**
     * @name komoo.Map#editmode_changed
     * @event
     */
    this.event.trigger('editmode_changed', mode);
};


/**
 * Initialize the Google Street View.
 */
komoo.Map.prototype._createStreetViewObject = function () {
    var options = {};
    this.streetView = new google.maps.StreetViewPanorama(
            this.streetViewPanel.get(0), options);
};


/**
 * @returns {JQuery}
 */
komoo.Map.prototype._createMainPanel = function () {
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
        $.each(this.options.regionTypes, function (i, type) {
            komooMap.overlayOptions[type.type] = type;
        });
    } else {
        $.each(this.options.regionTypes, function (i, type) {
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

    google.maps.event.addListener(this.drawingManager, 'drawingmode_changed',
        function (e){
            if (komooMap.drawingManager.drawingMode) {
                komooMap.addPanel.show();
            }
        });


    this.addMenu = addMenu;
    return panel;
};


/**
 * @returns {JQuery}
 */
komoo.Map.prototype._createAddPanel = function () {
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
        /**
         * @name komoo.Map#cancel_click
         * @event
         */
        komooMap.event.trigger('cancel_click');
        komooMap.type = null;
        komooMap.setEditMode(undefined);
    });
    finishButton.bind('click', function () {
        button_click();
        /**
         * @name komoo.Map#finish_click
         * @event
         */
        komooMap.event.trigger('finish_click', komooMap.overlayOptions[komooMap.type]);
        komooMap.type = null;
        komooMap.setEditMode(undefined);
    });

    content.css({'clear': 'both'});
    buttons.css({'clear': 'both'});
    content.append(this.editToolbar);
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
};


/**
 * Sets to the 'select_center' mode to user select the center point of radius filter.
 * Emits 'center_selected' event when done.
 * @param {number} [opt_radius]
 * @param {function} [opt_callBack] Optional callback function. The callback parameters are 'latLng' and 'circle'.
 *                   'latLng' receives a google.maps.LatLng object. 'circle' receives google.maps.Circle object.
 */
komoo.Map.prototype.selectCenter = function (opt_radius, opt_callBack) {
    var komooMap = this;
    this.setMode(komoo.Mode.SELECT_CENTER);
    var handler = function (e, latLng, circle) {
        if (typeof opt_radius == 'number') {
            circle.setRadius(opt_radius);
        }
        if (typeof opt_callBack == 'function') {
            opt_callBack(latLng, circle);
        }
        komooMap.event.unbind('center_selected', handler);
    };
    this.event.bind('center_selected', handler);
};


komoo.Map.prototype.getOverlay = function (overlayType, id) {
    return this.loadedOverlays[overlayType + '_' + id];
};


komoo.Map.prototype.highlightOverlay = function (overlay, id) {
    var overlayType;
    var overlayCenter;
    if (typeof overlay == 'string') {
        overlayType = overlay;
        overlay = this.getOverlay(overlayType, id);
    }
    if (!overlay) {
        return false;
    }
    if (overlay.highlighted) {
        return true;
    }

    if (overlay.getCenter) {
        overlayCenter = overlay.getCenter();
    } else if (overlay.getPosition) {
        overlayCenter = overlay.getPosition();
    } else if (overlay.bounds) {
        overlayCenter = overlay.bounds.getCenter();
    }

    if (overlay.setIcon) {
        overlay.setIcon(this.getOverlayIcon(overlay, true));
    }
    overlay.highlighted = true;
    this.closeInfoWindow();
    this.openInfoWindow(overlay, overlayCenter);

    return true;
};


komoo.Map.prototype._emit_geojson_loaded = function (e) {
    /**
     * @name komoo.Map#geojson_loaded
     * @event
     */
    this.event.trigger('geojson_loaded', e);
};


komoo.Map.prototype._emit_mapclick = function (e) {
    /**
     * @name komoo.Map#mapclick
     * @event
     */
    this.event.trigger('mapclick', e);
};


komoo.Map.prototype._emit_overlayclick = function (e) {
    /**
     * @name komoo.Map#overlayclick
     * @event
     */
    this.event.trigger('overlayclick', e);
};


komoo.Map.prototype._emit_center_selected = function (latLng) {
    var komooMap = this;
    if (!this.radiusCircle) {
        this.radiusCircle = new google.maps.Circle({
                visible: true,
                radius: 100,
                fillColor: 'white',
                fillOpacity: 0.0,
                strokeColor: '#ffbda8',
                zIndex: -1
        });

        google.maps.event.addListener(this.radiusCircle, 'click', function(e) {
            if (komooMap.mode == komoo.Mode.SELECT_CENTER) {
                komooMap._emit_center_selected(e.latLng);
            }
        });
        this.radiusCircle.setMap(this.googleMap);
    }
    if (!this.centerMarker) {
        this.centerMarker = new google.maps.Marker({
                visible: true,
                icon: '/static/img/marker.png',
                zIndex: 4
        });
        this.centerMarker.setMap(this.googleMap);
    }
    this.centerMarker.setPosition(latLng);
    this.radiusCircle.setCenter(latLng);
    /**
     * @name komoo.Map#center_selecter
     * @event
     */
    this.event.trigger('center_selected', [latLng, this.radiusCircle]);
    this.setMode(null);
};


komoo.Map.prototype._emit_changed = function (e) {
    /**
     * @name komoo.Map#changed
     * @event
     */
    this.event.trigger('changed', e);
};




/**
 * Verify if a point is inside a closed path.
 * @param {google.maps.LatLng} point
 * @param {google.maps.MVCArray(google.maps.LatLng)} path
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
 * @param {String | number} value
 * @param {number} days
 */
komoo.createCookie = function (name, value, days) {
    var expires;
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = '; expires=' + date.toGMTString();
    }
    else {
        expires = '';
    }
    document.cookie = name + '=' + value + expires + '; path=/';
};


/**
 * Reads a cookie.
 * @param {String} name
 * @returns {String}
 */
komoo.readCookie = function (name) {
    var nameEQ = name + '=';
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
 */
komoo.eraseCookie = function (name) {
    createCookie(name, '', -1);
};
