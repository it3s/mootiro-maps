/**
 * View, create and edit regions on Google Maps.
 *
 * @name map.js
 * @fileOverview A simple way to use Google Maps.
 * @version 0.1.0b
 * @author Komoo Team
 * @copyright (c) 2012 it3s
 */

// TODO: Get from Django the static url to avoid hardcode some urls.
// TODO: Create a generic function to attach events to open/close info window.

/** @namespace */
if (!window.komoo) komoo = {};
if (!komoo.event) komoo.event = google.maps.event;


komoo.CLEAN_MAPTYPE_ID = "clean";


/**
 * @name komoo.GeometryType
 * @class Object that represents a item on Add tab of main panel.
 * @property {String} type An internal identifier.
 * @property {String[]} categories
 * @property {String} title The text displayed to user as a menu item.
 * @property {String} tooltip The text displayed on mouse over.
 * @property {String} color
 * @property {String} icon The icon url.
 * @property {google.maps.drawing.GeometryType[]} geometryTypes The geometry options displayed as submenu.
 * @property {String} formUrl The url used to load the form via ajax.
 *           This occurs when user click on Finish button.
 *           Please use dutils.urls.resolve instead of hardcode the address.
 * @property {boolean} disabled
 */

komoo.GeometryType = {
    POINT: 'Point',
    MULTIPOINT: 'MultiPoint',
    POLYGON: 'Polygon',
    POLYLINE: 'LineString',
};


/**
 * Options object to {@link komoo.Map}.
 *
 * @class
 * @property {boolen} [editable=true]  Define if the drawing feature will be enabled.
 * @property {boolean} [useGeoLocation=false] Define if the HTML5 GeoLocation will be used to set the initial location.
 * @property {boolean} [defaultDrawingControl=false] If true the controls from Google Drawing library are used.
 * @property {komoo.GeometryType[]} [featureTypes=komoo.GeometryTypes]
 * @property {boolean} [autoSaveLocation=false] Determines if the current location is saved to be displayed the next time the map is loaded.
 * @property {boolean} [enableInfoWindow=true] Shows informations on mouse over.
 * @property {boolean} [enableCluster=false] Cluster some points together.
 * @property {boolean} [debug=false]
 * @property {Object} [featureOptions]
 * @property {google.maps.MapOptions} [googleMapOptions] The Google Maps map options.
 */
komoo.MapOptions = {
    clustererMaxZoom: 10,
    polygonIconsMinZoom: 17,
    fetchUrl: "/get_geojson?",
    editable: true,
    useGeoLocation: false,
    defaultDrawingControl: false,
    featureTypes: [],
    autoSaveLocation: false,
    autoSaveMapType: false,
    enableInfoWindow: true,
    displayClosePanel: false,
    displaySupporter: false,
    enableCluster: true,
    fetchFeatures: true,
    debug: false,
    featureOptions: {
        visible: true,
        fillColor: "#ff0",
        fillOpacity: 0.70,
        strokeColor: "#ff0",
        strokeWeight: 3,
        strokeOpacity: 0.70
    },
    googleMapOptions: {  // Our default options for Google Maps map object.
        center: new google.maps.LatLng(-23.55, -46.65),  // São Paulo, SP - Brasil
        zoom: 13,
        minZoom: 2,
        disableDefaultUI: false,
        mapTypeControlOptions: {
            mapTypeIds: [google.maps.MapTypeId.ROADMAP,
                         komoo.CLEAN_MAPTYPE_ID,
                         google.maps.MapTypeId.HYBRID]
        },
        mapTypeId: komoo.CLEAN_MAPTYPE_ID,
        streetViewControl: false,
        scaleControl: true,
        panControlOptions: {position: google.maps.ControlPosition.RIGHT_TOP},
        zoomControlOptions: {position: google.maps.ControlPosition.RIGHT_TOP},
        scaleControlOptions: {position: google.maps.ControlPosition.RIGHT_BOTTOM,
                              style: google.maps.ScaleControlStyle.DEFAULT}
    }
};




/**
 * @class Object used to get features from server for each tile
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
    this.addrLatLngCache = {};
    this.tileSize = new google.maps.Size(256, 256);
    this.maxZoom = 32;
    this.name = "Server Data";
    this.alt  = "Server Data Tile Map Type";
};


komoo.ServerFetchMapType.prototype.releaseTile = function (tile) {
    var serverFetchMapType = this;
    if (this.komooMap.fetchedTiles[tile.tileKey]) {
        var bounds = serverFetchMapType.komooMap.googleMap.getBounds();
        this.komooMap.fetchedTiles[tile.tileKey].features.forEach(function (feature, index, orig) {
            if (feature.getBounds()) {
                if (!bounds.intersects(feature.getBounds())) {
                    feature.setMap(null);
                } else if (!bounds.contains(feature.getBounds().getNorthEast()) ||
                        !bounds.contains(feature.getBounds().getSouthWest())){
                    serverFetchMapType.komooMap.keptFeatures.push(feature);
                }
            } else if (feature.getPosition) {
                if (bounds.contains(feature.getPosition())) {
                    feature.setMap(null);
                }
            }
        });
    }
};


komoo.ServerFetchMapType.prototype.getTile = function (coord, zoom, ownerDocument) {
    var me = this;
    var div = ownerDocument.createElement("DIV");
    var addr = this.getAddrLatLng(coord, zoom);
    div.tileKey = addr;
    if (this.komooMap.options.debug) {
        // Display debug info.
        $(div).css({
            "width": this.tileSize.width + "px",
            "height": this.tileSize.height + "px",
            "border": "solid 1px #AAAAAA",
            "overflow": "hidden",
            "font-size": "9px"
        });
    }

    // Verify if we already loaded this block.
    if (this.komooMap.fetchedTiles[addr]) {
        if (this.komooMap.options.debug) {
            // Display debug info.
            div.innerHTML = this.komooMap.fetchedTiles[addr].geojson;
        }
        this.komooMap.fetchedTiles[addr].features.forEach(function (feature, index, orig) {
            feature.setMap(me.komooMap);
            feature.updateIcon();
        });
        return div;
    }
    if (this.komooMap.options.fetchFeatures != false) {
        $.ajax({
            url: this.komooMap.options.fetchUrl + addr,
            dataType: "json",
            type: "GET",
            success: function (data, textStatus, jqXHR) {
                var features = me.komooMap.loadGeoJSON(JSON.parse(data), false);
                me.komooMap.fetchedTiles[addr] = {
                    geojson: data,
                    features: features
                };
                if (me.komooMap.options.debug) {
                    // Display debug info.
                    div.innerHTML = data;
                    $(div).css("border", "solid 1px #F00");
                }
                features.forEach(function (feature, index, orig) {
                    feature.setMap(me.komooMap);
                    feature.updateIcon();
                });
            },
            error: function (jqXHR, textStatus, errorThrown) {
                if (window.console) console.error(textStatus);
                var serverError = $("#server-error");
                if (serverError.parent().length == 0) {
                    serverError = $("<div>").attr("id", "server-error");
                    $("body").append(serverError);
                    var error = $("<div>").html(jqXHR.responseText)
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
    var key = "x=" + coord.x + ",y=" + coord.y + ",z=" + zoom
    if (this.addrLatLngCache[key]) {
        return this.addrLatLngCache[key];
    }
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
    this.addrLatLngCache[key] = "bounds=" + ne.toUrlValue() + "," + sw.toUrlValue() + "&zoom=" + zoom;
    return this.addrLatLngCache[key];
};



komoo.WikimapiaMapType = function (komooMap) {
    this.komooMap = komooMap;
    this.addrLatLngCache = {};
    this.loadedFeatures = {};
    this.tileSize = new google.maps.Size(256, 256);
    this.maxZoom = 32;
    this.name = "Wikimapia Data";
    this.alt = "Wikimapia Data Tile Map Type";
    this.key = "Add here your wikimapia key";
};

komoo.WikimapiaMapType.prototype.getAddrLatLng = function (coord, zoom) {
    var key = "x=" + coord.x + ",y=" + coord.y
    if (this.addrLatLngCache[key]) {
        return this.addrLatLngCache[key];
    }
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
    this.addrLatLngCache[key] = sw.lng() + "," + sw.lat() + "," + ne.lng() + "," + ne.lat();
    return this.addrLatLngCache[key];
};

komoo.WikimapiaMapType.prototype.getTile = function (coord, zoom, ownerDocument) {
    var me = this;

    function createFeatures(json) {
        var features = komoo.collections.makeFeatureCollection({map: me.komooMap});
        var folder = json.folder;
        folder.forEach(function (item, index, orig) {
            var coords = [];
            item.polygon.forEach(function (point, index, orig) {
                coords.push(new google.maps.LatLng(point.y, point.x));
            });
            var polygon = new google.maps.Polygon({paths: [coords], fillColor: 'gray'});
            polygon.wikimapia_id = item.id;
            polygon.wikimapia_name = item.name;
            features.push(polygon)
        });
        return features;
    }

    var div = ownerDocument.createElement("DIV");
    var addr = this.getAddrLatLng(coord, zoom);
    var url = "http://api.wikimapia.org/?function=box&bbox=" + addr + "&format=json&key=" + this.key;
    div.tileKey = addr;
    //if (this.komooMap.options.debug) {
        // Display debug info.
        $(div).css({
            "width": this.tileSize.width + "px",
            "height": this.tileSize.height + "px",
            "border": "solid 1px #AAAAAA",
            "overflow": "hidden",
            "font-size": "9px"
        });
    //}

    // Verify if we already loaded this block.
    if (this.komooMap.fetchedTiles[addr]) {
        //if (this.komooMap.options.debug) {
            // Display debug info.
            div.innerHTML = JSON.stringify(this.komooMap.fetchedTiles[addr].geojson);
        //}
        return div;
    }
    if (this.komooMap.options.fetchFeatures != false) {
        $.ajax({
            url: url,
            dataType: "json",
            type: "GET",
            success: function (data, textStatus, jqXHR) {
                var features = createFeatures(data);
                me.komooMap.fetchedTiles[addr] = {
                    json: data,
                    features: features
                };
                features.forEach(function (feature, index, orig) {
                    if (!me.loadedFeatures[feature.wikimapia_id]) {
                        feature.setMap(me.komooMap);
                        me.loadedFeatures[feature.wikimapia_id] = feature;
                    }
                });
                //if (me.komooMap.options.debug) {
                    // Display debug info.
                    div.innerHTML = JSON.stringify(data);
                    $(div).css("border", "solid 1px #F00");
                //}
            },
            error: function (jqXHR, textStatus, errorThrown) {
                if (window.console) console.error(textStatus);
            }
        });
    }
    return div;
};

/** @namespace */
komoo.Mode = {};
/***/ komoo.Mode.NAVIGATE = "navigate";
/***/ komoo.Mode.SELECT_CENTER = "select_center";
/***/ komoo.Mode.DRAW = "draw";




/** @namespace */
komoo.EditMode = {};
/***/ komoo.EditMode.NONE = null;
/***/ komoo.EditMode.DRAW = "draw";
/***/ komoo.EditMode.ADD = "add";
/***/ komoo.EditMode.CUTOUT = "cutout";
/***/ komoo.EditMode.DELETE = "delete";




/**
 * Wrapper for Google Maps map object with some helper methods.
 *
 * @class
 * @param {DOM} element The map canvas.
 * @param {komoo.MapOptions} options The options object.
 * @property {undefined | MarkerClusterer} clusterer A MarkerClusterer object used to cluster markers.
 * @property {google.maps.drawing.DrawingManager} drawingManager Drawing manager from Google Maps library.
 * @property {boolean} editable The status of the drawing feature.
 * @property {komoo.EditMode} editMode The current mode of edit feature. Possible values are cutout, add and delete.
 * @property {JQuery} editToolbar JQuery selector of edit toolbar.
 * @property {JQuery} event JQuery selector used to emit events.
 * @property {Object} fetchedTiles Cache the json and the features for each tile
 * @property {google.maps.Geocoder} geocoder  Google service to get addresses locations.
 * @property {google.maps.Map} googleMap The Google Maps map object.
 * @property {InfoBox | google.maps.InfoWindow} infoWindow
 * @property {InfoBox | google.maps.InfoWindow} tooltip
 * @property {Object} loadedverlays Cache all features
 * @property {komoo.Mode} mode Possible values are null, new, edit
 * @property {google.maps.MVCObject[]} newFeatures Array containing new features added by user.
 * @property {komoo.MapOptions} options The options object used to construct the komoo.Map object.
 * @property {Object} featureOptions
 * @property {google.maps.MVCObject[]} features Array containing all features.
 * @property {google.maps.Circle} radiusCircle
 * @property {komoo.ServerFetchMapType} serverFetchMapType
 * @property {google.maps.StreetViewPanorama} streetView
 * @property {JQuery} streetViewPanel JQuery selector of Street View panel.
 */
komoo.Map = function (element, options) {
    var komooMap = this;
    // options should be an object.
    if (typeof options !== "object") {
        options = {};
    }
    this.drawingMode = {};
    this.drawingMode[komoo.GeometryType.POINT] = google.maps.drawing.OverlayType.MARKER;
    this.drawingMode[komoo.GeometryType.POLYGON] = google.maps.drawing.OverlayType.POLYGON;
    this.drawingMode[komoo.GeometryType.POLYLINE] = google.maps.drawing.OverlayType.POLYLINE;

    // Join default option with custom options.
    var googleMapOptions = $.extend(komoo.MapOptions.googleMapOptions,
                                    options.googleMapOptions);
    // TODO: init feature options
    // Initializing some properties.
    this.mode = komoo.Mode.NAVIGATE;
    this.fetchedTiles = {};
    this.loadedFeatures = {};
    this.options = $.extend(komoo.MapOptions, options);
    this.drawingManagerOptions = {};
    this.featureOptions = {};
    this.features = komoo.collections.makeFeatureCollection({map: this});
    this.keptFeatures = komoo.collections.makeFeatureCollection({map: this});
    this.newFeatures = komoo.collections.makeFeatureCollection({map: this});
    this.loadedFeatures = {};
    this.featuresByType = {};
    this.initFeaturesByTypeObject();
    // Creates a jquery selector to use the jquery events feature.
    this.event = $("<div>");
    // Creates the Google Maps object.
    this.googleMap = new google.maps.Map(element, googleMapOptions);
    // Uses Tiles to get data from server.
    this.serverFetchMapType = new komoo.ServerFetchMapType(this);
    this.googleMap.overlayMapTypes.insertAt(0, this.serverFetchMapType);
    this.wikimapiaMapType = new komoo.WikimapiaMapType(this);
    //this.googleMap.overlayMapTypes.insertAt(0, this.wikimapiaMapType);
    // Create the simple version of toolbar.
    this.editToolbar = $("<div>").addClass("map-toolbar").css("margin", "5px");
    this.initControls();
    this.setEditable(this.options.editable);
    this.initCustomControl();
    this.initStreetView();
    if (this.options.useGeoLocation) {
        this.goToUserLocation();
    }
    if (this.options.autoSaveMapType) {
        this.useSavedMapType();
    }
    this.handleEvents();
    // Geocoder is used to search locations by name/address.
    this.geocoder = new google.maps.Geocoder();
    if (komoo.onMapReady) {
        komoo.onMapReady(this);
    }

    this.cleanMapType = new google.maps.StyledMapType([
        {
            featureType: "poi",
            elementType: "all",
            stylers: [
                {visibility: "off"}
            ]
        },
        {
            featureType: "road",
            elementType: "all",
            stylers: [
                {lightness: 70}
            ]
        },
        {
            featureType: "transit",
            elementType: "all",
            stylers: [
                {lightness: 50}
            ]
        },
        {
            featureType: "water",
            elementType: "all",
            stylers: [
                {lightness: 50}
            ]
        },
        {
            featureType: "administrative",
            elementType: "labels",
            stylers: [
                {lightness: 30}
            ]
        }
    ], {
        name: gettext("Clean")
    });

    this.googleMap.mapTypes.set(komoo.CLEAN_MAPTYPE_ID, this.cleanMapType);
    this.initEvents();
};

komoo.Map.prototype.initEvents = function (opt_object) {
    var that = this;
    var object = this.googleMap;
    var eventsNames = ['zoom_changed'];
    eventsNames.forEach(function(eventName, index, orig) {
        komoo.event.addListener(object, eventName, function (e, args) {
            if (eventName == 'zoom_changed') e = that.googleMap.getZoom();
            komoo.event.trigger(that, eventName, e, args);
        });
    });
};

komoo.Map.prototype.initControls = function () {
    this.initMarkerClusterer();
    this.tooltip = komoo.controls.makeTooltip({map: this});
    this.infoWindow = komoo.controls.makeInfoWindow({map: this});
};

/**
 * Display the information window.
 * @param {Object} opts
 */
komoo.Map.prototype.openInfoWindow = function (opts) {
    if (!this.options.enableInfoWindow) return;
    this.closeTooltip();
    this.infoWindow.open(opts);
};

komoo.Map.prototype.closeInfoWindow = function () {
    this.infoWindow.close();
};


/**
 * Display the tooltip.
 * @param {Object} opts
 */
komoo.Map.prototype.openTooltip = function (opts) {
    var options = opts || {};
    if (!this.options.enableInfoWindow ||
            this.addPanel.is(":visible") ||
            this.infoWindow.isMouseover ||
            this.tooltip.feature == options.feature ||
            (options.features && options.feature == this.infoWindow.feature))
        return;

    this.tooltip.open(options);
};

komoo.Map.prototype.closeTooltip = function () {
    clearTimeout(this.tooltip.timer);
    this.tooltip.close();
};


/**
 * Prepares the CustomControl property. Should not be called externally
 */
komoo.Map.prototype.initCustomControl = function () {
    // Draw our custom control.
    if (!this.options.defaultDrawingControl) {
        this.closePanel = this._createClosePanel();
        if (this.options.displayClosePanel) {
            this.closePanel.show();
        }
        this.mainPanel = this._createMainPanel();
        if (!this.editable) {
            this.mainPanel.hide();
        }
        //this.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
        //        this.mainPanel.get(0));
        this.addPanel = this._createAddPanel();
        this.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
                this.addPanel.get(0));
        this.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
                this.closePanel.get(0));
        // Adds editor toolbar.
        //this.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
        //        this.editToolbar.get(0));

        if (this.options.displaySupporter) {
            this.supportersBox = $("<div>");
            this.supportersBox.attr("id", "map-supporters");
            this.googleMap.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(
                    this.supportersBox.get(0));
        }
    }
};


komoo.Map.prototype.setSupportersContent = function (selector) {
    if (this.supportersBox) {
        this.supportersBox.append(selector.show());
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
        if (window.console) console.log("Initializing Marker Clusterer support.");
        this.clusterer = new MarkerClusterer(this.googleMap, [], {
            gridSize: 20,
            maxZoom: this.options.clustererMaxZoom,
            minimumClusterSize: 1,
            imagePath: "/static/img/cluster/communities",
            imageSizes: [24, 29, 35, 41, 47]
        });
        google.maps.event.addListener(this.clusterer, 'mouseover', function (c) {
            var markers = c.getMarkers();
            var features = [];
            markers.forEach(function (marker, index, orig) {
                features.push(marker.feature);
            });
            features.sort(function (a, b) {
                return a.getProperty('lastUpdate') < b.getProperty('lastUpdate');
            });
            komooMap.openTooltip({feature: features[0],
                                  features: features,
                                  position: c.getCenter()});
        })
        google.maps.event.addListener(this.clusterer, 'mouseout', function (c) {
            komooMap.closeTooltip();
        })
    }
};


/**
 * Prepares the featuresByType property. Should not be called externally.
 */
komoo.Map.prototype.initFeaturesByTypeObject = function () {
    // TODO: Refactoring
    var komooMap = this;
    this.options.featureTypes.forEach(function (type, index, orig) {
        var opts = {
            map: komooMap
        };
        komooMap.featuresByType[type.type] = {categories: type.categories};
        komooMap.featuresByType[type.type].categories.push("uncategorized");
        komooMap.featuresByType[type.type].forEach = function (callback) {
            this.categories.forEach(function (item, index, orig) {
                callback(komooMap.featuresByType[type.type][item], item, orig);
            });
        };
        komooMap.featuresByType[type.type]["uncategorized"] = komoo.collections.makeFeatureCollection(opts);
        if (type.categories.length) {
            type.categories.forEach(function(category, index_, orig_) {
                komooMap.featuresByType[type.type][category] = komoo.collections.makeFeatureCollection(opts);
            });
        }
    });
};


/**
 * Prepares the streetVies property. Should not be called externally.
 */
komoo.Map.prototype.initStreetView = function () {
    if (window.console) console.log("Initializing StreetView support.");
    this.streetViewPanel = $("<div>").addClass("map-panel").height("100%").width("50%");
    this.googleMap.controls[google.maps.ControlPosition.TOP_LEFT].push(
            this.streetViewPanel.get(0));
    this.streetViewPanel.hide();
    this._createStreetViewObject();
};


komoo.Map.prototype.updateClusterers = function () {
    // FIXME: This is not the best way to do the cluster feature.
    var zoom = this.googleMap.getZoom();
    if (this.clusterer) {
        if (zoom < this.options.clustererMaxZoom) {
            this.clusterer.addMarkers(this.clusterMarkers);
        } else {
            this.clusterer.clearMarkers();
        }
    }
};



/**
 * Connects some important events. Should not be called externally.
 */
komoo.Map.prototype.handleEvents = function () {
    var komooMap = this;
    if (window.console) console.log("Connecting map events.");
    // Listen Google Maps map events.
    google.maps.event.addListener(this.googleMap, "click", function (e) {
        if (komooMap.addPanel.is(":hidden")) {
            komooMap.setCurrentFeature(null);  // Remove the feature selection
        }
        if (komooMap.mode == komoo.Mode.SELECT_CENTER) {
            komooMap._emit_center_selected(e.latLng);
        }
        komooMap._emit_mapclick(e);
    });

    google.maps.event.addListener(this.googleMap, "idle", function () {
        var bounds = komooMap.googleMap.getBounds();
        if (komooMap.options.autoSaveLocation) {
            komooMap.saveLocation();
        }
        komooMap.keptFeatures.forEach(function (feature, index, orig) {
            if (!bounds.intersects(feature.getBounds())) {
                feature.setMap(null);
            }
        });
        komooMap.keptFeatures.clear();
    });

    google.maps.event.addListener(this.googleMap, "zoom_changed", function () {
        komooMap.closeTooltip();
        komooMap.updateClusterers();
    });

    google.maps.event.addListener(this.googleMap, "projection_changed", function () {
        komooMap.projection = komooMap.googleMap.getProjection();
        komooMap.overlayView = new google.maps.OverlayView();
        komooMap.overlayView.draw = function () { };
        komooMap.overlayView.onAdd = function (d) { };
        komooMap.overlayView.setMap(komooMap.googleMap);
    });

    google.maps.event.addListener(this.googleMap, "rightclick", function (e) {
        if (!komooMap.overlayView) {
            google.maps.event.trigger(komooMap.googleMap, "projection_changed");
        }
        var feature = komooMap.currentFeature;
        if (feature && feature.getProperties() &&
                feature.getProperties().userCanEdit) {
            komooMap.deleteNode(e);
        }
    });

    if (this.options.autoSaveMapType) {
        google.maps.event.addListener(this.googleMap, "maptypeid_changed", function () {
            komooMap.saveMapType();
        });
    }
};


komoo.Map.prototype.getVisibleFeatures = function () {
    var bounds = this.googleMap.getBounds();
    if (!bounds) return [];

    var features = komoo.collections.makeFeaturesCollection();
    this.features.forEach(function (feature, index, orig) {
        if (!feature.getMap() && (feature.getMarker() && !feature.getMarker().getVisible())) {
            // Dont verify the intersection if feature is invisible.
            return;
        }
        if (feature.getBounds()) {
            if (bounds.intersects(feature.getBounds())) {
                features.push(feature);
            }
        } else if (feature.getPosition) {
            if (bounds.contains(feature.getPosition())) {
                features.push(feature);
            }
        }
    });
    return features;
};


/**
 * Saves the map location to cookie
 * @property {google.maps.LatLng} opt_center
 * @property {integer} opt_zoom
 */
komoo.Map.prototype.saveLocation = function (opt_center, opt_zoom) {
    var center = opt_center || this.googleMap.getCenter();
    var zoom = opt_zoom || this.googleMap.getZoom();
    komoo.utils.createCookie('lastLocation', center.toUrlValue(), 90);
    komoo.utils.createCookie('lastZoom', zoom, 90);
};


/**
 * Loads the location saved in a cookie and go to there.
 * @see komoo.Map.saveLocation
 * @returns {boolean}
 */
komoo.Map.prototype.goToSavedLocation = function () {
    var lastLocation = komoo.utils.readCookie('lastLocation');
    var zoom = parseInt(komoo.utils.readCookie('lastZoom'), 10);
    if (lastLocation && zoom) {
        if (window.console) console.log('Getting location from cookie...');
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
 * @property {google.maps.MapTypeId|String} opt_mapType
 */
komoo.Map.prototype.saveMapType = function (opt_mapType) {
    var mapType = opt_mapType || this.googleMap.getMapTypeId();
    komoo.utils.createCookie('mapType', mapType, 90);
};


/**
 * Use the map type saved in a cookie.
 * @see komoo.Map.saveMapType
 * @returns {boolean}
 */
komoo.Map.prototype.useSavedMapType = function () {
    var mapType = komoo.utils.readCookie('mapType');
    if (mapType) {
        this.googleMap.setMapTypeId(mapType);
        return true;
    }
    return false;
};


komoo.Map.prototype.updateFeature = function (feature, geojson) {
    var geometry;

    // if we got only the geojson, as first parameter, we will try to get the
    // correct feature
    if (!geojson) {
        geojson = feature;
        var feature = geojson.features[0];
        feature = this.getFeature(feature.properties.type, feature.properties.id);
    }

    // Get the geometry from geojson
    if (geojson.type == 'FeatureCollection' && geojson.features) {
        geometry = geojson.features[0].geometry;
    } else if (geojson.type == 'GeometryCollection' && geojson.geometries) {
        geometry = geojson.geometries[0];
    }

    // Update the feature geometry
    if (feature.getGeometryType() == geometry.type)
        feature.setCoordinates(geometry.coordinates);
};

komoo.Map.prototype.getZoom = function () {
    return this.googleMap.getZoom();
};

komoo.Map.prototype.setZoom = function (zoom) {
    return this.googleMap.setZoom(zoom);
};

/**
 * Load the features from geoJSON into the map.
 * @param {json} geoJSON The json that will be loaded.
 * @param {boolean} panTo If true pan to the region where features are.
 * @param {boolean} [opt_attach=true]
 * @returns {google.maps.MVCObject[]}
 */
komoo.Map.prototype.loadGeoJSON = function (geoJSON, panTo, opt_attach) {
    // TODO: Refactoring
    // TODO: Use the correct color
    // TODO: Add a hidden marker for each polygon/polyline
    // TODO: Document the geoJSON properties:
    // - userCanEdit
    // - type (community, need...)
    var komooMap = this;
    var featureCollection;
    var features = komoo.collections.makeFeatureCollection({map: this});

    if (opt_attach === undefined) {
        opt_attach = true;
    }

    var polygonOptions = $.extend({
        clickable: true,
        editable: false,
        zIndex: 1
    }, this.options.featureOptions);
    var polylineOptions = $.extend({
        clickable: true,
        editable: false,
        zIndex: 3
    }, this.options.featureOptions);
    var markerOptions = {};

    if (!geoJSON.type) return; // geoJSON is invalid.

    if (geoJSON.type == "FeatureCollection") {
        var geoJsonFeatureCollection = geoJSON.features;
    }
    var feature;
    if (!geoJsonFeatureCollection) {
        return [];
    }
    geoJsonFeatureCollection.forEach(function (geoJsonFeature, index, orig) {
        var geometry = geoJsonFeature.geometry;
        feature = komooMap.getFeature(geoJsonFeature.properties.type, geoJsonFeature.properties.id);
        if (!feature)
            feature = komoo.features.makeFeature(geoJsonFeature, komooMap.featureOptions);
        var paths = [];

        // Dont attach or return the features already loaded
        if (feature) {
            feature = komooMap.loadedFeatures[geoJsonFeature.properties.type + "_" + geoJsonFeature.properties.id] || feature;
            if (!komooMap.loadedFeatures[feature.getProperties().type + "_" + feature.getProperties().id]) {
                komooMap.features.push(feature);
                komooMap.loadedFeatures[feature.getProperties().type + "_" + feature.getProperties().id] = feature;
                komooMap._attachFeatureEvents(feature);
            }
            features.push(feature);
            if (opt_attach) {
                feature.setMap(komooMap);
            }
            var featuresByType = komooMap.featuresByType[feature.getProperties().type];
            var categories = feature.getProperties().categories;
            if (categories && categories.length) {
                categories.forEach(function(category, index, orig) {
                    if (featuresByType[category.name]) {
                        featuresByType[category.name].push(feature);
                    }
                });
            } else {
                featuresByType["uncategorized"].push(feature);
            }
            if (feature.getMarker()) {
                google.maps.event.addListener(feature.getMarker(), "click", function () {
                    komooMap.googleMap.fitBounds(feature.getBounds());
                });
                if (feature.getProperties().type == "Community") {
                    komooMap.clusterMarkers.push(feature.getMarker().getOverlay());
                }
            }
            feature.updateIcon();
        }
    });
    if (panTo && feature.getBounds()) {
        this.googleMap.fitBounds(feature.getBounds());
    }

    this._emit_geojson_loaded(geoJSON);
    return features;
};


/**
 * Create a GeoJSON with the maps features.
 * @param {boolean} newOnly
 * @returns {json}
 */
komoo.Map.prototype.getGeoJSON = function (opt_options) {
    var options = opt_options || {};
    var geoJSON;
    var geoms = [];
    var list;
    var newOnly = options.newOnly || false;
    var currentOnly = options.currentOnly || false;
    var createGeometryCollection = options.geometryCollection || false;
    if (newOnly) {
        list = this.newFeatures;
    } else if (currentOnly) {
        list = komoo.collections.makeFeatureCollection({map: this});
        list.push(this.currentFeature);
    } else {
        list = this.features;
    }
    if (createGeometryCollection) {
        // TODO
        geoJSON = {
            "type": "GeometryCollection",
            "geometries": geoms
        };
    } else {
        return list.getGeoJson();
    }
    list.forEach(function (feature, index, orig) {
        if (feature.getGeoJsonGeometry())
            geoms.push(feature.getGeoJsonGeometry());
    });
    return geoJSON;
};


/**
 * Gets a list of features of specific type.
 * @param {String} type
 * @param {String[]} [opt_categories=[]]
 * @param {boolean} [opt_strict=false]
 * @returns {google.maps.MVCObject[]} features that matches the parameters.
 */
komoo.Map.prototype.getFeaturesByType = function (type, opt_categories, opt_strict) {
    var komooMap = this;
    var features = new komoo.collections.makeFeatureCollection({map: this});
    var categories = opt_categories;
    if (!this.featuresByType[type]) {
        return false;
    }
    if (!categories) {
        categories = [];
        this.featuresByType[type].forEach(function (features, category, orig) {
            categories.push(category);
        });
    } else if (categories.length === 0) {
        categories = ["uncategorized"];
    }
    categories.forEach(function (category, index, orig) {
        if (komooMap.featuresByType[type][category]) {
            komooMap.featuresByType[type][category].forEach(function (feature, index, orig) {
                if (!opt_strict || !feature.getProperties().categories || feature.getProperties().categories.length == 1) {
                    features.push(feature);
                }
            });
        }
    });
    return features;
};


/**
 * Hides some features.
 * @property {google.maps.MVCObject[]} features
 * @returns {number} How many features were hidden.
 */
komoo.Map.prototype.hideFeatures = function (features) {
    return features.hide();
};


/**
 * Hides features of specific type.
 * @param {String} type
 * @param {String[]} [opt_categories=[]]
 * @param {boolean} [opt_strict=false]
 * @returns {number} How many features were hidden.
 */
komoo.Map.prototype.hideFeaturesByType = function (type, opt_categories, opt_strict) {
    return this.getFeaturesByType(type, opt_categories, opt_strict).hide();
};


/**
 * Hides all features.
 * @returns {number} How many features were hidden.
 */
komoo.Map.prototype.hideAllFeatures = function () {
    return this.features.hide();
};


/**
 * Makes visible some features.
 * @property {google.maps.MVCObject[]} features
 * @returns {number} How many features were displayed.
 */
komoo.Map.prototype.showFeatures = function (features) {
    return features.show();
};


/**
 * Makes visible features of specific type.
 * @param {String} type
 * @param {String[]} [opt_categories=[]]
 * @param {boolean} [opt_strict=false]
 * @returns {number} How many features were displayed.
 */
komoo.Map.prototype.showFeaturesByType = function (type, opt_categories, opt_strict) {
    return this.getFeaturesByType(type, opt_categories, opt_strict).show();
};


/**
 * Makes visible all features.
 * @returns {number} How many features were displayed.
 */
komoo.Map.prototype.showAllFeatures = function () {
    return this.features.show();
};


/**
 * Remove all features from map.
 */
komoo.Map.prototype.clear = function () {
    this.initFeaturesByTypeObject();
    this.loadedFeatures = {};
    this.fetchedTiles = {};
    this.features.removeAllFromMap()
    this.features.clear()
    this.clusterMarkers = [];
    if (this.clusterer) {
        this.clusterer.clearMarkers();
    }
};


komoo.Map.prototype.deleteNode = function (e) {
    var nodeWidth = 6;
    var proj = this.googleMap.getProjection();
    var clickPoint = proj.fromLatLngToPoint(e.latLng);
    var poly = this.currentFeature;
    var minDist = 512;
    var selectedIndex = -1;
    var pathIndex = -1;
    var paths;
    if (poly.getGeometry().getPaths) {
        paths = poly.getGeometry().getPaths();
    } else if (poly.getGeometry().getPath) {
        paths = new google.maps.MVCArray([poly.getGeometry().getPath()]);
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
    // Check if we are clicking inside the node
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
 * Set the current feature and display the edit controls.
 * @param {google.maps.Polygon|google.maps.Polyline|null} feature
 *        The feature to be set as current or null to remove the selection.
 */
komoo.Map.prototype.setCurrentFeature = function (feature, opt_force) {
    //if (this.currentFeature == feature && !opt_force) return;
    $("#komoo-map-add-button, #komoo-map-cut-out-button, #komoo-map-delete-button").hide();
    this.currentFeature = feature;
    if (this.currentFeature && this.currentFeature.getProperties() &&
            this.currentFeature.getProperties().userCanEdit) {
        this.currentFeature.setEditable(true);
        var geometry = this.currentFeature.getGeometry();
        if (geometry.getGeometryType() == 'Polygon') {
            this.drawingMode_ = komoo.GeometryType.POLYGON;
            $("#komoo-map-cut-out-button").show();
        } else if (geometry.getGeometryType() == 'LineString' ||
                   this.currentFeature.getGeometry().getGeometryType() == 'MultiLineString') {
            this.drawingMode_ = komoo.GeometryType.POLYLINE;
        } else if (geometry.getGeometryType() == 'Point' ||
                   this.currentFeature.getGeometry().getGeometryType() == 'MultiPoint') {
            this.drawingMode_ = komoo.GeometryType.POINT;
        }
        $("#komoo-map-add-button, #komoo-map-delete-button").show();
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
        this.setCurrentFeature(this.currentFeature);
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
        if (this.currentFeature && this.currentFeature.setEditable) {
            this.currentFeature.setEditable(false);
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
 *        Sets to true to make Street View visible or false to hide.
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
    var komooMap = this;
    var pos;
    if (google.loader.ClientLocation) { // Gets from google service
        pos = new google.maps.LatLng(google.loader.ClientLocation.latitude,
                                         google.loader.ClientLocation.longitude);
        this.googleMap.setCenter(pos);
        if (window.console) console.log("Getting location from Google...");
    }
    if (navigator.geolocation) { // Uses HTML5
        navigator.geolocation.getCurrentPosition(function(position) {
            pos = new google.maps.LatLng(position.coords.latitude,
                                             position.coords.longitude);
            komooMap.googleMap.setCenter(pos);
            if (window.console) console.log("Getting location from navigator.geolocation...");
        }, function () {
            if (window.console) console.log("User denied access to navigator.geolocation...");
        });
    }
};


/**
 * Go to an address or to latitude, longitude position.
 * @param {String|google.maps.LatLng|number[]} position
 *        An address or a pair latitude, longitude.
 */
komoo.Map.prototype.goTo = function (position, optDisplayMarker) {
    if (optDisplayMarker == undefined) optDisplayMarker = true;
    var komooMap = this;
    var latLng;
    function _go (latLng) {
        if (latLng) {
            komooMap.googleMap.panTo(latLng);
            if (! komooMap.searchMarker) {
                komooMap.searchMarker = new google.maps.Marker();
                komooMap.searchMarker.setMap(komooMap.googleMap);
            }
            if (optDisplayMarker) komooMap.searchMarker.setPosition(latLng);
        }
    }
    if (typeof position == "string") { // Got address
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
komoo.Map.prototype.panTo = function (position, optDisplayMarker) {
    return this.goTo(position, optDisplayMarker);
};

komoo.Map.prototype.selectNewGeometryType = function (feature, opt_edit) {
    var that = this;
    var buttons = [];
    feature.featureType.geometryTypes.forEach(function (geometryType, index, orig) {
        buttons.push({
            text: gettext(geometryType),
            'class': "button",
            click: function () {
                var newGeometry = komoo.geometries.makeGeometry({geometry: {type: geometryType}}, feature);
                feature.setGeometry(newGeometry);
                if (opt_edit) {
                    that.editFeature(feature);
                    that.setEditMode(komoo.EditMode.ADD);
                    that.drawingManager.setDrawingMode(that.drawingMode[that.drawingMode_]);
                }
                $(this).dialog("close");
            }
        })
    });
    return infoMessage('Geometry', 'Select the geometry type you want to draw', null, buttons);
};

komoo.Map.prototype.editFeature = function (feature) {
    if (!feature || !feature.getProperties() || !feature.getProperties().userCanEdit) {
        return false;
    }
    if (feature.getGeometryType() == 'Empty')
        return this.selectNewGeometryType(feature, true);

    feature.setEditable(true);
    feature.setMap(this);
    this.type = feature.getProperties('type');
    this.setCurrentFeature(feature, true);
    this.setMode(komoo.Mode.DRAW);
    $(".map-panel-title", this.addPanel).text(gettext("Edit"));
    this.addPanel.css({"margin-top": "33px"});
    this.addPanel.show();
    var color = this.featureOptions[feature.getProperties().type].color;
    var border = this.featureOptions[feature.getProperties().type].border;
    var zIndex = this.featureOptions[feature.getProperties().type].zIndex;
    this.drawingManagerOptions.polylineOptions.strokeColor = border;
    this.drawingManagerOptions.polygonOptions.fillColor = color;
    this.drawingManagerOptions.polygonOptions.strokeColor = border;
    this.drawingManagerOptions.polygonOptions.zIndex = zIndex;
    return true;
};


/**
 * Attach some events to feature.
 * @param {google.maps.Polygon|google.maps.Polyline} feature
 */
komoo.Map.prototype._attachFeatureEvents = function (feature) {
    var komooMap = this;
    if (feature.getPaths) {
        // Removes stroke from polygons.
        feature.setOptions({strokeWeight: 1.5});
    }

    google.maps.event.addListener(feature, "rightclick", function (e) {
        var feature_ = this;
        if (feature_.getProperties() && feature_.getProperties().userCanEdit &&
                feature_ == komooMap.currentFeature) {
            if (!komooMap.featureView) {
                google.maps.event.trigger(komooMap.googleMap, "projection_changed");
            }
            komooMap.deleteNode(e);
        }
    });

    google.maps.event.addListener(feature, "click", function (e, o) {
        var feature_ = this;
        if (window.console) console.log("Clicked on feature");
        if (komooMap.mode == komoo.Mode.SELECT_CENTER) {
            komooMap._emit_center_selected(e.latLng);
            return;
        }
        if (komooMap.addPanel.is(":visible") && feature_ != komooMap.currentFeature) {
            if (window.console) console.log("Clicked on unselected feature");
            if (!feature_.getProperties().userCanEdit) {
                return;
            }
        }
        if (komooMap.editMode == komoo.EditMode.DELETE && feature_.getProperties() &&
                feature_.getProperties().userCanEdit) {
            //komooMap.setCurrentFeature(null);
            var l = 0;
            if (feature_.getGeometryType() == komoo.GeometryType.POLYGON) {  // Clicked on polygon.
                var paths = feature_.getGeometry().getPaths();
                l = paths.getLength();
                paths.forEach(function (path, i) {
                    // Delete the correct path.
                    if (komoo.utils.isPointInside(e.latLng, path)) {
                        paths.removeAt(i);
                        l--;
                    }
                });
            } else if (feature_.getGeometryType() == komoo.GeometryType.MULTIPOINT) {
                var markers = feature_.getGeometry().getMarkers();
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
            if (l === 0) {  // We had only one path, or the feature wasnt a polygon.
                //feature_.setMap(null);
            } else {
                komooMap.setCurrentFeature(feature_);
            }
            // TODO: (IMPORTANT) Remove the feature from komooMap.features
            komooMap.setEditMode(null);
            komooMap._emit_changed();
        } else {
            komooMap.setEditMode(null);
            komooMap.setCurrentFeature(feature_);  // Select the clicked feature
            komooMap.closeTooltip();
            setTimeout(function () {
                komooMap.openInfoWindow({feature: feature_, position: e.latLng});
            }, 200);
        }
    });

    google.maps.event.addListener(feature, 'dblclick', function (e, o) {
        e.stop();
        var url = this.getUrl();
        if (url) window.location = url;
    });

    google.maps.event.addListener(feature, 'mousemove', function (e) {
        clearTimeout(komooMap.tooltip.timer);
        var delay = (feature.getProperty('type') == 'Community') ? 400 : 0;
        komooMap.tooltip.timer = setTimeout(function () {
            komooMap.openTooltip({feature: feature, position: e.latLng});
        }, delay);
    });

    google.maps.event.addListener(feature, 'mouseout', function (e) {
        komooMap.closeTooltip();
    });
};


komoo.Map.prototype.drawNew = function (geometryType, featureType) {
    // TODO: HERE
    if (window.console) console.log(geometryType, featureType);
};


komoo.Map.prototype.setDrawingMode = function (type, featureType) {
    if (!featureType) {
        featureType = type;
        type = this.type;
    }
    this.type = type;
    this.setEditMode(komoo.EditMode.DRAW);
    this.setCurrentFeature(null);  // Remove the feature selection
    this.drawingMode_ = this.drawingMode[featureType];
    this.drawingManager.setDrawingMode(this.drawingMode_);
    var FeatureTypeTitle = {};
    FeatureTypeTitle[komoo.GeometryType.POLYGON] = gettext("Add shape");
    FeatureTypeTitle[komoo.GeometryType.POLYLINE] = gettext("Add line");
    FeatureTypeTitle[komoo.GeometryType.POINT] = gettext("Add point");
    $(".map-panel-title", this.addPanel).text(FeatureTypeTitle[featureType]);
    if (this.featureOptions[this.type]) {
        var color = this.featureOptions[this.type].color;
        var border = this.featureOptions[this.type].border;
        var zIndex = this.featureOptions[this.type].zIndex;
        this.drawingManagerOptions.polylineOptions.strokeColor = border;
        this.drawingManagerOptions.polygonOptions.fillColor = color;
        this.drawingManagerOptions.polygonOptions.strokeColor = border;
        this.drawingManagerOptions.polygonOptions.zIndex = zIndex;
    }
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
                komoo.GeometryType.POLYGON,
                komoo.GeometryType.POLYLINE,
                komoo.GeometryType.CIRCLE,
                komoo.GeometryType.POINT
            ]
        },
        polygonOptions: $.extend({
            clickable: true,
            editable: false,
            zIndex: 1
        }, this.options.featureOptions),
        polylineOptions: $.extend({
            clickable: true,
            editable: false
        }, this.options.featureOptions),
        circleOptions: {
            fillColor: "white",
            fillOpacity: 0.15,
            editable: true,
            zIndex: -1
        },
        drawingMode: komoo.GeometryType.POLYGON
    };
    this.drawingManager = new google.maps.drawing.DrawingManager(
            this.drawingManagerOptions);
    google.maps.event.addListener(this.drawingManager,
            "overlaycomplete", function (e) {
        // FIXME: REWRITE

        var path;
        if (e.overlay.getPath) {
            path = e.overlay.getPath();
        }

        var overlay;
        if ((komooMap.editMode == komoo.EditMode.CUTOUT || komooMap.editMode == komoo.EditMode.ADD) &&
                    e.overlay.getPaths) {
            // Gets the overlays path orientation.
            var paths = komooMap.currentFeature.getGeometry().getPaths();
            if (paths.length > 0) {
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
            }
            paths.push(path);
            komooMap.currentFeature.getGeometry().setPaths(paths);
            // Remove the temporary overlay from map
            e.overlay.setMap(null);
            komooMap.setEditMode(komoo.EditMode.DRAW);
        } else if (komooMap.editMode == komoo.EditMode.ADD && e.overlay.getPosition) {
            komooMap.currentFeature.getGeometry().addMarker(e.overlay);
            komooMap.currentFeature.updateIcon(100);
            komooMap.setEditMode(komoo.EditMode.DRAW);
        } else if (komooMap.editMode == komoo.EditMode.ADD && e.overlay.getPath) {
            komooMap.currentFeature.getGeometry().addPolyline(e.overlay);
            komooMap.setEditMode(komoo.EditMode.DRAW);
        } else if (e.overlay.getPosition) {
            overlay = new MultiMarker();
            overlay.addMarker(e.overlay);
            overlay.setMap(komooMap.googleMap);
        } else if (e.overlay.getPath && !e.overlay.getPaths) {
            overlay = new MultiPolyline();
            overlay.addPolyline(e.overlay);
            overlay.setMap(komooMap.googleMap);
        } else {
            overlay = e.overlay;
        }
        if (overlay) {
            var feature = komoo.features.makeFeature({
                'properties': {
                    'userCanEdit': true,
                    'type': komooMap.type,
                    'name': 'sem nome',
                    'alwaysVisible': true
                },
                'geometry': {
                    'type': komooMap.drawingManager.getDrawingMode(),
                }
            });
            var type = komooMap.featureOptions[komooMap.type];
            if (type) feature.setFeatureType(type);
            var geometry = feature.getGeometry();
            geometry.setOverlay(overlay);
            feature.setMap(komooMap, {geometry: true});

            // Sets the custom image.
            feature.updateIcon(komooMap.googleMap.getZoom());

            komooMap.features.push(feature);
            komooMap.newFeatures.push(feature);
            // Listen events from drawn feature.
            komooMap._attachFeatureEvents(feature);
            komooMap.setCurrentFeature(feature);
            komooMap.setEditMode(komoo.EditMode.DRAW);
        }
        if (path) {
            // Emit changed event when edit paths.
            google.maps.event.addListener(path, "set_at", function() {
                komooMap._emit_changed();
            });
            google.maps.event.addListener(path, "insert_at", function() {
                komooMap._emit_changed();
            });
        }
        // Switch back to non-drawing mode after drawing a shape.
        komooMap.drawingManager.setDrawingMode(null);

        komooMap._emit_changed();
        return true;
    });

    if (!this.options.defaultDrawingControl) {
        // Adds new HTML elements to the map.
        var polygonButton = komoo.createMapButton(gettext("Add shape"), gettext("Draw a shape"), function (e) {
            komooMap.setDrawingMode(komoo.GeometryType.POLYGON);
        }).attr("id", "map-add-" + komoo.GeometryType.POLYGON);

        var lineButton = komoo.createMapButton(gettext("Add line"), gettext("Draw a line"), function (e) {
            komooMap.setDrawingMode(komoo.GeometryType.POLYLINE);
        }).attr("id", "map-add-" + komoo.GeometryType.POLYLINE);

        var markerButton = komoo.createMapButton(gettext("Add point"), gettext("Add a marker"), function (e) {
            komooMap.setDrawingMode(komoo.GeometryType.POINT);
        }).attr("id", "map-add-" + komoo.GeometryType.POINT);

        var addMenu = komoo.createMapMenu(gettext("Add new..."), [polygonButton, lineButton, markerButton]);
        //this.editToolbar.append(addMenu);
        this.addItems = $(".map-container", addMenu);

        var addButton = komoo.createMapButton(gettext("Add"), gettext("Add another region"), function (e) {
            if (komooMap.editMode == komoo.EditMode.ADD) {
                komooMap.setEditMode(komoo.EditMode.DRAW);
            } else {
                komooMap.setEditMode(komoo.EditMode.ADD);
            }
            komooMap.drawingManager.setDrawingMode(komooMap.drawingMode[komooMap.drawingMode_]);
        });
        addButton.hide();
        addButton.attr("id", "komoo-map-add-button");
        this.editToolbar.append(addButton);

        var cutOutButton = komoo.createMapButton(gettext("Cut out"), gettext("Cut out a hole from a region"), function (e) {
            if (komooMap.editMode == komoo.EditMode.CUTOUT) {
                komooMap.setEditMode(komoo.EditMode.DRAW);
            } else {
                komooMap.setEditMode(komoo.EditMode.CUTOUT);
            }
            komooMap.drawingManager.setDrawingMode(komooMap.drawingMode[komooMap.drawingMode_]);
        });
        cutOutButton.hide();
        cutOutButton.attr("id", "komoo-map-cut-out-button");
        this.editToolbar.append(cutOutButton);

        var deleteButton = komoo.createMapButton(gettext("Delete"), gettext("Delete a region"), function (e) {
            if (komooMap.editMode == komoo.EditMode.DELETE) {
                komooMap.setEditMode(komoo.EditMode.DRAW);
            } else {
                komooMap.setEditMode(komoo.EditMode.DELETE);
            }
            komooMap.drawingManagerOptions.drawingMode = null;
            komooMap.drawingManager.setOptions(komooMap.drawingManagerOptions);
        });
        deleteButton.hide();
        deleteButton.attr("id", "komoo-map-delete-button");
        this.editToolbar.append(deleteButton);

        this.event.bind("editmode_changed", function(e, mode) {
            komooMap.closeInfoWindow();
            komooMap.closeTooltip();
            // Set the correct button style when editMode was changed.
            addButton.removeClass("active");
            cutOutButton.removeClass("active");
            deleteButton.removeClass("active");
            if (mode == "add") {
                addButton.addClass("active");
            } else if (mode == "cutout") {
                cutOutButton.addClass("active");
            } else if (mode == "delete") {
                deleteButton.addClass("active");
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
    this.event.trigger("mode_changed", mode);
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
    this.event.trigger("editmode_changed", mode);
};


/**
 * Initialize the Google Street View.
 */
komoo.Map.prototype._createStreetViewObject = function () {
    var that = this;
    var options = {
        enableCloseButton: true,
        visible: false
    };
    this.streetView = new google.maps.StreetViewPanorama(
            this.streetViewPanel.get(0), options);
    this.googleMap.setStreetView(this.streetView);
    google.maps.event.addListener(this.streetView, "visible_changed", function () {
        if (that.streetView.getVisible())
            that.streetViewPanel.show();
        else
            that.streetViewPanel.hide();
    });
};


/**
 * @returns {JQuery}
 */
komoo.Map.prototype._createMainPanel = function () {
    var komooMap = this;
    var panel = $("<div>").addClass("map-panel");
    var addMenu = $("<ul>").addClass("map-menu");

    var tabs = komoo.createMapTab([
        {title: gettext("Filter")},
        {title: gettext("Add")/*, content: addMenu*/}
    ]);

    // Only logged in users can add new items.
    if (!isAuthenticated) {
        var submenuItem = addMenu.append($("<li>").addClass("map-menuitem").text(gettext("Please log in.")));
        submenuItem.bind("click", function (){
            window.location = "/user/login"; // FIXME: Hardcode is evil
        });
        this.options.featureTypes.forEach(function (type, index, orig) {
            komooMap.featureOptions[type.type] = type;
        });
    } else {
        this.options.featureTypes.forEach(function (type, index, orig) {
            komooMap.featureOptions[type.type] = type;
            var item = $("<li>").addClass("map-menuitem");
            if (!type.icon) {
                if (type.type == 'OrganizationBranch')
                    type.icon = '/static/img/organization.png';
                else
                    type.icon = '/static/img/' + type.type.toLowerCase() + '.png';
            }
            var icon = $("<img>").attr({src: type.icon}).css("float", "left");
            if (type.disabled) icon.css("opacity", "0.3");
            item.append(icon);

            item.append($("<div>").addClass("item-title").text(type.title).attr("title", type.tooltip));
            var submenu = komooMap.addItems.clone(true).addClass("map-submenu");
            $("div", submenu).hide();
            type.geometryTypes.forEach(function (featureType, index, orig) {
                $("#map-add-" + featureType, submenu).addClass("enabled").show();
            });
            var submenuItems = $("div.enabled", submenu);
            if (type.disabled) {
                item.addClass("disabled");
            }
            item.css({
                "position": "relative"
            });
            submenuItems.removeClass("map-button").addClass("map-menuitem"); // Change the class
            submenuItems.bind("click", function () {
                $(".map-submenu", addMenu).hide();
                $(".map-menuitem.selected", komooMap.mainPanel).removeClass("selected");
                item.addClass("selected");
                $(".map-menuitem:not(.selected)", komooMap.mainPanel).addClass("frozen");
            });
            if (submenuItems.length == 1) {
                submenuItems.hide();
                item.bind("click", function () {
                    if (komooMap.addPanel.is(":hidden") && !$(this).hasClass("disabled")) {
                        komooMap.type = type.type;
                        submenuItems.trigger("click");
                    }
                });
            } else {
                item.bind("click", function () {
                    // Menu should not work if add panel is visible.
                    if (komooMap.addPanel.is(":hidden") && !$(this).hasClass("disabled")) {
                        komooMap.type = type.type;
                        submenu.css({"left": item.outerWidth() + "px"});
                        submenu.toggle();
                    }
                });
            }
            submenu.css({
                "top": "0",
                "z-index": "999999"
            });
            item.append(submenu);
            //addMenu.append(item);
            type.selector = item;
        });
    }

    panel.css({
        "margin": "10px 5px 10px 10px",
        "width": "180px"
    });

    panel.append(tabs.selector);

    google.maps.event.addListener(this.drawingManager, "drawingmode_changed",
        function (e){
            if (komooMap.drawingManager.drawingMode) {
                komooMap.addPanel.show();
            }
        });


    this.addMenu = addMenu;
    return panel;
};


komoo.Map.prototype._createClosePanel = function () {
    var komooMap = this;
    var panel = $("<div>").addClass("map-panel");
    var content = $("<div>").addClass("content");
    var buttons = $("<div>").addClass("map-panel-buttons");
    var closeButton = $("<div>").addClass("map-button");

    closeButton.append($("<i>").addClass("icon-remove"));
    closeButton.append($("<span>").text(gettext("Close")));

    content.css({"clear": "both"});
    buttons.css({"clear": "both"});
    panel.append(content);
    panel.append(buttons);
    buttons.append(closeButton);

    panel.css({
        "margin": "10px",
        "width": "220px"
    });

    closeButton.click(function (e) {
        komooMap.event.trigger("close_click");
    });
    return panel.hide();
};


/**
 * @returns {JQuery}
 */
komoo.Map.prototype._createAddPanel = function () {
    var komooMap = this;
    var panel = $("<div>").addClass("map-panel");
    var content = $("<div>").addClass("content");
    var title = $("<div>").text(gettext("Title")).addClass("map-panel-title");
    var buttons = $("<div>").addClass("map-panel-buttons");
    var finishButton = $("<div>").text(gettext("Finish")).addClass("map-button");
    var cancelButton = $("<div>").text(gettext("Cancel")).addClass("map-button");

    function button_click () {
        $(".map-menuitem.selected", komooMap.addMenu).removeClass("selected");
        $(".frozen", komooMap.mainPanel).removeClass("frozen");
        komooMap.drawingManager.setDrawingMode(null);
        komooMap.setMode(komoo.Mode.NAVIGATE);
        panel.hide();
    }
    cancelButton.bind("click", function () {
        button_click();
        if (komooMap.newFeatures.length > 0) { // User drew a feature, so remove it.
            komooMap.newFeatures.forEach(function (item, index, orig) {
                var feature = komooMap.features.pop(); // The newly created feature should be the last at array.
                feature.removeFromMap();
            });
            komooMap.newFeatures.clear();
        }
        /**
         * @name komoo.Map#cancel_click
         * @event
         */
        komooMap.event.trigger("cancel_click");
        komooMap.type = null;
        komooMap.setEditMode(undefined);
    });
    finishButton.bind("click", function () {
        button_click();
        /**
         * @name komoo.Map#finish_click
         * @event
         */
        komooMap.event.trigger("finish_click", komooMap.featureOptions[komooMap.type]);
        komooMap.type = null;
        komooMap.setEditMode(undefined);
    });

    content.css({"clear": "both"});
    buttons.css({"clear": "both"});
    content.append(this.editToolbar);
    panel.append(title);
    panel.append(content);
    panel.append(buttons);
    buttons.append(finishButton);
    buttons.append(cancelButton);

    panel.css({
        "margin": "10px",
        "width": "220px"
    });

    return panel.hide();
};


/**
 * Sets to the select_center mode to user select the center point of radius filter.
 * Emits center_selected event when done.
 * @param {number} [opt_radius]
 * @param {function} [opt_callBack] Optional callback function. The callback parameters are latLng and circle.
 *                   latLng receives a google.maps.LatLng object. circle receives google.maps.Circle object.
 */
komoo.Map.prototype.selectCenter = function (opt_radius, opt_callBack) {
    var komooMap = this;
    this.setMode(komoo.Mode.SELECT_CENTER);
    var handler = function (e, latLng, circle) {
        if (typeof opt_radius == "number") {
            circle.setRadius(opt_radius);
        }
        if (typeof opt_callBack == "function") {
            opt_callBack(latLng, circle);
        }
        komooMap.event.unbind("center_selected", handler);
    };
    this.event.bind("center_selected", handler);
};


/**
 * @param {string} featureType
 * @param {number} id
 * @returns {feature}
 */
komoo.Map.prototype.getFeature = function (featureType, id) {
    return this.loadedFeatures[featureType + "_" + id];
};


/**
 * @param {feature | string} feature
 * @param {number} id
 * @returns {boolean}
 */
komoo.Map.prototype.centerFeature = function (feature, id) {
    var featureType;
    if (typeof feature == "string") {
        featureType = feature;
        feature = this.getFeature(featureType, id);
    }
    if (!feature) {
        return false;
    }

    this.panTo(feature.getCenter(), false);
    return true;
}


/**
 * @param {Feature | string} feature
 * @param {number} id
 * @returns {boolean}
 */
komoo.Map.prototype.highlightFeature = function (feature, id) {
    var featureType;
    if (typeof feature == "string") {
        featureType = feature;
        feature = this.getFeature(featureType, id);
    }

    if (!feature) return false;
    if (feature.isHighlighted()) return true;

    if (this.featureHighlighted) this.featureHighlighted.setHighlight(false);
    feature.setHighlight(true);
    this.closeInfoWindow();
    this.openInfoWindow({feature:feature, position:feature.getCenter()});

    this.featureHighlighted = feature;
    return true;
};


komoo.Map.prototype._emit_geojson_loaded = function (e) {
    /**
     * @name komoo.Map#geojson_loaded
     * @event
     */
    this.updateClusterers();
    this.event.trigger("geojson_loaded", e);
};


komoo.Map.prototype._emit_mapclick = function (e) {
    /**
     * @name komoo.Map#mapclick
     * @event
     */
    this.event.trigger("mapclick", e);
};


komoo.Map.prototype._emit_featureclick = function (e) {
    /**
     * @name komoo.Map#featureclick
     * @event
     */
    this.event.trigger("featureclick", e);
};


komoo.Map.prototype._emit_center_selected = function (latLng) {
    var komooMap = this;
    if (!this.radiusCircle) {
        this.radiusCircle = new google.maps.Circle({
                visible: true,
                radius: 100,
                fillColor: "white",
                fillOpacity: 0.0,
                strokeColor: "#ffbda8",
                zIndex: -1
        });

        google.maps.event.addListener(this.radiusCircle, "click", function(e) {
            if (komooMap.mode == komoo.Mode.SELECT_CENTER) {
                komooMap._emit_center_selected(e.latLng);
            }
        });
        this.radiusCircle.setMap(this.googleMap);
    }
    if (!this.centerMarker) {
        this.centerMarker = new google.maps.Marker({
                visible: true,
                icon: "/static/img/marker.png",
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
    this.event.trigger("center_selected", [latLng, this.radiusCircle]);
    this.setMode(komoo.Mode.NAVIGATE);
};


komoo.Map.prototype._emit_changed = function (e) {
    /**
     * @name komoo.Map#changed
     * @event
     */
    this.event.trigger("changed", e);
};


/**
 * @returns {JQuery}
 */
komoo.createMapButton = function (name, title, onClick) {
    var selector = $("<div>").text(name).addClass("map-button");
    selector.attr("title", title);
    selector.bind("click", onClick);
    return selector;
};


/**
 * @returns {JQuery}
 */
komoo.createMapMenu = function (name, items) {
    var selector = $("<div>").text(name).addClass("map-menu");
    var container = $("<div>").addClass("map-container").hide();
    items.forEach(function (item, index, orig) {
        container.append(item);
        item.css({"clear": "both", "float": "none"});
        item.bind("click", function () { container.hide(); });
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
        selector: $("<div>"),
        tabsSelector: $("<div>").addClass("map-tabs"),
        containersSelector: $("<div>").addClass("map-container")
    };
    tabs.selector.append(tabs.tabsSelector, tabs.containersSelector);
    items.forEach(function (item, index, orig) {
        var tab = {
            tabSelector: $("<div>").text(item.title).addClass("map-tab").css({"border": "0px"}),
            containerSelector: $("<div>").addClass("map-tab-container").hide()
        };
        if (item.content) tab.containerSelector.append(item.content);
        tab.tabSelector.click(function () {
            if (tabs.current && tabs.current != tab) {
                tabs.current.tabSelector.removeClass("selected");
                tabs.current.containerSelector.hide();
            }
            tabs.current = tab;
            tab.tabSelector.toggleClass("selected");
            tab.containerSelector.toggle();
        });

        tabs.items[item.title] = tab;
        tab.tabSelector.css({"width": 100 / items.length + "%"});
        tabs.tabsSelector.append(tab.tabSelector);
        tabs.containersSelector.append(tab.containerSelector);
    });
    return tabs;
};
