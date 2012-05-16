if (typeof Object.create !== 'function') {
    Object.create = function (o) {
        function F() {}
        F.prototype = o;
        return new F();
    };
}

if (!window.komoo) komoo = {};

komoo.OverlayType = {
    POINT: "marker",
    MULTIPOINT: "multimarker",
    POLYGON: "polygon",
    POLYLINE: "polyline"
};

komoo.Overlays = {};

/** Default values **/

komoo.Overlays.defaults = {};

komoo.Overlays.defaults.BACKGROUND_COLOR = "#000";
komoo.Overlays.defaults.BACKGROUND_OPACITY = 0.6;
komoo.Overlays.defaults.BORDER_COLOR = "#000";
komoo.Overlays.defaults.BORDER_OPACITY = 0.6;
komoo.Overlays.defaults.BORDER_SIZE = 5;
komoo.Overlays.defaults.ZINDEX = 1;

/** Overlay Factory **/

komoo.Overlays.makeOverlay = function (feature) {
    var geometryType = feature.geometry.type;
    var overlay;
    if (geometryType == "Point") {
        overlay = new komoo.Overlays.Point();
    } else if (geometryType == "MultiPoint") {
        overlay = new komoo.Overlays.MultiPoint();
    } else if (geometryType == "LineString") {
        overlay = new komoo.Overlays.Polyline();
    } else if (geometryType == "Polygon") {
        overlay = new komoo.Overlays.Polygon();
    }
    return overlay;
};

/** Abstract Overlay **/

komoo.Overlays.Overlay = function (opts) {
    this.initGoogleObject(opts);
    this.initEvents();
};

komoo.Overlays.Overlay.prototype.initEvents = function () {
    var that = this;
    var eventsNames = [
        "click",
        "dblclick",
        "mousedown",
        "mousemove",
        "mouseout",
        "mouseover",
        "mouseup",
        "rightclick"
    ];
    $.each(eventsNames, function(i, eventName) {
        google.maps.event.addListener(that.googleObject_,
                eventName, function (args) {
            google.maps.event.trigger(that, eventName, args);
        });
    });
};

komoo.Overlays.Overlay.prototype.initGoogleObject = function () {
};

komoo.Overlays.Overlay.prototype.setType = function (type) {
    this.type_ = type;
};

komoo.Overlays.Overlay.prototype.getType = function () {
    return this.type_;
};

komoo.Overlays.Overlay.prototype.getGeometryType = function () {
    return this.geometryType_;
};

komoo.Overlays.Overlay.prototype.getGeometry = function () {
    return {
        "type": this.getGeometryType(),
        "coordinates": this.getCoordinates()
    };
};

komoo.Overlays.Overlay.prototype.getProperties = function () {
    return null;
};

komoo.Overlays.Overlay.prototype.setProperties = function (properties) {
};

komoo.Overlays.Overlay.prototype.getFeature = function () {
    return {
        "type": "Feature",
        "geometry": this.getGeometry(),
        "properties": this.getProperties()
    };
};

komoo.Overlays.Overlay.prototype.getDefaultZIndex = function () {
    return this.type_ ? this.type_.getDefaultZIndex() :
        komoo.Overlays.defaults.ZINDEX;
};

komoo.Overlays.Overlay.prototype.setCoordinates = function (coordinates) {
    throw new Error("Not Implemented");
};

komoo.Overlays.Overlay.prototype.getCoordinates = function () {
    throw new Error("Not Implemented");
};

komoo.Overlays.Overlay.prototype.getLatLngFromArray = function (pos) {
    if (!pos) return null;
    return new google.maps.LatLng(pos[0], pos[1]);
};

komoo.Overlays.Overlay.prototype.getArrayFromLatLng = function (latLng) {
    if (!latLng) return null;
    return [latLng.lat(), latLng.lng()];
};

/* Delegations */
komoo.Overlays.Overlay.prototype.setMap = function (map) {
    return this.googleObject_.setMap(map);
};

komoo.Overlays.Overlay.prototype.getMap = function () {
    return this.googleObject_.getMap();
};

komoo.Overlays.Overlay.prototype.setVisible = function (visible) {
    return this.googleObject_.setVisible(visible);
};

komoo.Overlays.Overlay.prototype.getVisible = function () {
    return this.googleObject_.getVisible();
}

komoo.Overlays.Overlay.prototype.setOptions = function (options) {
    return this.googleObject_.setOptions(options);
};

komoo.Overlays.Overlay.prototype.geOptions = function () {
    return this.googleObject_.getOptions();
}


/** Point Overlay **/

komoo.Overlays.Point = function (opts) {
    komoo.Overlays.Overlay.call(this, opts);
    this.geometryType_ = "Point";
};

komoo.Overlays.Point.prototype = Object.create(komoo.Overlays.Overlay.prototype);

komoo.Overlays.Point.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        zIndex: this.getDefaultZIndex(),
    };
    this.googleObject_ = new google.maps.Marker(options);
};

komoo.Overlays.Point.prototype.initEvents = function () {
    komoo.Overlays.Overlay.prototype.initEvents.call(this);
    var that = this;
    var eventsNames = [
        "animation_changed",
        "clickable_changed",
        "cursor_changed",
        "drag",
        "dragend",
        "draggable_changed",
        "dragstart",
        "flat_changed",
        "icon_changed",
        "position_changed",
        "shadow_changed",
        "shape_changed",
        "title_changed",
        "visible_changed",
        "zindex_changed"
    ];
    $.each(eventsNames, function(i, eventName) {
        google.maps.event.addListener(that.googleObject_,
                eventName, function (args) {
            google.maps.event.trigger(that, eventName, args);
        });
    });
};

komoo.Overlays.Point.prototype.setCoordinates = function (coordinates) {
    this.setPosition(this.getLatLngFromArray(coordinates));
};

komoo.Overlays.Point.prototype.getCoordinates = function () {
    return this.getArrayFromLatLng(this.getPosition());
};

/* Delegations */
komoo.Overlays.Point.prototype.setPosition = function (latlng) {
    return this.googleObject_.setPosition(latlng);
};

komoo.Overlays.Point.prototype.getPosition = function () {
    return this.googleObject_.getPosition();
};

komoo.Overlays.Point.prototype.setIcon = function (icon) {
    return this.googleObject_.setIcon(icon);
};

komoo.Overlays.Point.prototype.getIcon = function () {
    return this.googleObject_.getIcon();
};

komoo.Overlays.Point.prototype.setDraggable = function (draggable) {
    return this.googleObject_.setDraggable(draggable);
};

komoo.Overlays.Point.prototype.getDraggable = function () {
    return this.googleObject_.getDraggable();
};


/** Multipoint Overlay **/

komoo.Overlays.MultiPoint = function (opts) {
    komoo.Overlays.Overlay.call(this, opts);
    this.geometryType_ = "MultiPoint";
};

komoo.Overlays.MultiPoint.prototype = Object.create(komoo.Overlays.Overlay.prototype);

komoo.Overlays.MultiPoint.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        visible: true,
        zIndex: this.getDefaultZIndex(),
    };
    this.googleObject_ = new MultiMarker(options);
};

komoo.Overlays.MultiPoint.prototype.setPoints = function (points) {
    this.googleObject_.addMarkers(points);
};

komoo.Overlays.MultiPoint.prototype.getPoints = function () {
    return this.googleObject_.getMarkers().getArray();
};

komoo.Overlays.MultiPoint.prototype._guaranteePoints = function (len) {
    var points = this.googleObject_.getMarkers();
    var missing;
    if (points.length > len) {
        missing = points.length - len;
        console.log(missing);
        for (var i=0; i < missing; i++) {
             points.pop();
        }
    } else if (points.length < len) {
        missing = len - points.length;
        for (var i=0; i < missing; i++) {
            this.googleObject_.addMarker(new komoo.Overlays.Point());
        }
    }
};

komoo.Overlays.MultiPoint.prototype.setCoordinates = function (coordinates) {
    var that = this;
    var coords = coordinates;
    if (!coords[0].pop) coords = [coords];
    console.log(coords);
    this._guaranteePoints(coords.length);
    $.each(this.getPoints(), function (i, point) {
        point.setPosition(that.getLatLngFromArray(coords[i]));
    });
};

komoo.Overlays.MultiPoint.prototype.getCoordinates = function () {
    var that = this;
    var coords = [];
    $.each(this.getPoints(), function (i, point) {
        coords.push(that.getArrayFromLatLng(point.getPosition()));
    });
    return coords;
};

komoo.Overlays.MultiPoint.prototype.getPositions = function () {
    return this.googleObject_.getPositions().getArray();
};

/* Delegations */
komoo.Overlays.MultiPoint.prototype.addMarkers = function (markers) {
    this.googleObject_.addMarkers(markers);
};

komoo.Overlays.MultiPoint.prototype.setIcon = function (icon) {
    return this.googleObject_.setIcon(icon);
};

komoo.Overlays.MultiPoint.prototype.getIcon = function () {
    return this.googleObject_.getIcon();
};


/** Polyline Overlay **/

komoo.Overlays.Polyline = function (opts) {
    komoo.Overlays.Overlay.call(this, opts);
    this.geometryType_ = "LineString";
};

komoo.Overlays.Polyline.prototype = Object.create(komoo.Overlays.Overlay.prototype);

komoo.Overlays.Polyline.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        zIndex: this.getDefaultZIndex(),
        strokeColor: this.getBorderColor(),
        strockOpacity: this.getBorderOpacity(),
        strokeWeight: this.getBorderSize()
    };
    this.googleObject_ = new google.maps.Polyline(options);
};

komoo.Overlays.Polyline.prototype.setCoordinates = function (coordinates) {
    var that = this;
    var path = [];
    $.each(coordinates, function (k, pos) {
        path.push(that.getLatLngFromArray(pos));
    });
    this.setPath(path);
};

komoo.Overlays.Polyline.prototype.getCoordinates = function () {
    var that = this;
    var coords = [];
    this.getPath().forEach(function (latLng, i) {
        coords.push(that.getArrayFromLatLng(latLng));
    });
    return coords;
};

komoo.Overlays.Polyline.prototype.getBorderColor = function () {
    return this.type_ ? this.type_.getBorderColor() :
        komoo.Overlays.defaults.BORDER_COLOR;
};

komoo.Overlays.Polyline.prototype.getBorderOpacity = function () {
    return this.type_ ? this.type_.getBorderOpacity() :
        komoo.Overlays.defaults.BORDER_OPACITY;
}

komoo.Overlays.Polyline.prototype.getBorderSize = function () {
    return this.type_ ? this.type_.getBorderSize() :
        komoo.Overlays.defaults.BORDER_SIZE;
};

/* Delegations */
komoo.Overlays.Polyline.prototype.setPath = function (path) {
    return this.googleObject_.setPath(path);
}

komoo.Overlays.Polyline.prototype.getPath = function () {
    return this.googleObject_.getPath();
}


/** Polygon Overlay **/

komoo.Overlays.Polygon = function (opts) {
    komoo.Overlays.Polyline.call(this, opts);
    this.geometryType_ = "Polygon";
};

komoo.Overlays.Polygon.prototype = Object.create(komoo.Overlays.Polyline.prototype);

komoo.Overlays.Polygon.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        zIndex: this.getDefaultZIndex(),
        fillColor: this.getBackgroundColor(),
        fillOpacity: this.getBackgroundOpacity(),
        strokeColor: this.getBorderColor(),
        strockOpacity: this.getBorderOpacity(),
        strokeWeight: this.getBorderSize()
    };
    this.googleObject_ = new google.maps.Polygon(options);
};

komoo.Overlays.Polygon.prototype.getBackgroundColor = function () {
    return this.type_ ? this.type_.getBackgroundColor() :
        komoo.Overlays.defaults.BACKGROUND_COLOR;
};

komoo.Overlays.Polygon.prototype.getBackgroundOpacity = function () {
    return this.type_ ? this.type_.getBackgroundOpacity() :
        komoo.Overlays.defaults.BACKGROUND_OPACITY;
};

komoo.Overlays.Polygon.prototype.setCoordinates = function (coordinates) {
    var that = this;
    var paths = [];
    $.each(coordinates, function (j, coord) {
        var path = [];
        $.each(coord, function (k, pos) {
            path.push(that.getLatLngFromArray(pos));
        });
        // Removes the last point that closes the loop
        path.pop()
        paths.push(path);
    });
    this.setPaths(paths);
};

komoo.Overlays.Polygon.prototype.getCoordinates = function () {
    var that = this;
    var coords = [];
    this.getPaths().forEach(function (path, i) {
        var subCoords = [];
        path.forEach(function (latLng, j) {
            subCoords.push(that.getArrayFromLatLng(latLng));
        });
        // Copy the first point as the last one to close the loop
        if (subCoords.length) subCoords.push(subCoords[0]);
        coords.push(subCoords);
    });
    return coords;
};

/* Delegations */
komoo.Overlays.Polygon.prototype.setPaths = function (paths) {
    return this.googleObject_.setPaths(paths);
}

komoo.Overlays.Polygon.prototype.getPaths = function () {
    return this.googleObject_.getPaths();
}

