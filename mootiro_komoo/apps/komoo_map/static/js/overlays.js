if (typeof Object.create !== 'function') {
    Object.create = function (o) {
        function F() {}
        F.prototype = o;
        return new F();
    };
}

if (!window.komoo) komoo = {};

komoo.OverlayType = {};
komoo.OverlayType.POINT = 'marker';
komoo.OverlayType.MULTIPOINT = 'multimarker';
komoo.OverlayType.POLYGON = 'polygon';
komoo.OverlayType.POLYLINE = 'polyline';

komoo.overlays = {};

/** Default values **/

komoo.overlays.defaults = {};
komoo.overlays.defaults.BACKGROUND_COLOR = '#000';
komoo.overlays.defaults.BACKGROUND_OPACITY = 0.6;
komoo.overlays.defaults.BORDER_COLOR = '#000';
komoo.overlays.defaults.BORDER_OPACITY = 0.6;
komoo.overlays.defaults.BORDER_SIZE = 5;
komoo.overlays.defaults.ZINDEX = 1;

/** Overlay Factory **/

komoo.overlays.makeOverlay = function (feature) {
    var geometryType = feature.geometry.type;
    var overlay;
    if (geometryType == 'Point') {
        overlay = new komoo.overlays.Point();
    } else if (geometryType == 'MultiPoint') {
        overlay = new komoo.overlays.MultiPoint();
    } else if (geometryType == 'LineString') {
        overlay = new komoo.overlays.Polyline();
    } else if (geometryType == 'Polygon') {
        overlay = new komoo.overlays.Polygon();
    }
    return overlay;
};


/** Abstract Overlay **/

komoo.overlays.Overlay = function (opts) {
    this.initGoogleObject(opts);
    this.initEvents();
};

komoo.overlays.Overlay.prototype.initEvents = function () {
    var that = this;
    var eventsNames = ['click', 'dblclick', 'mousedown', 'mousemove',
        'mouseout', 'mouseover', 'mouseup', 'rightclick'];
    $.each(eventsNames, function(i, eventName) {
        google.maps.event.addListener(that.googleObject_,
                eventName, function (args) {
            google.maps.event.trigger(that, eventName, args);
        });
    });
};

komoo.overlays.Overlay.prototype.initGoogleObject = function () {
};

komoo.overlays.Overlay.prototype.setType = function (type) {
    this.type_ = type;
};

komoo.overlays.Overlay.prototype.getType = function () {
    return this.type_;
};

komoo.overlays.Overlay.prototype.getGeometryType = function () {
    return this.geometryType_;
};

komoo.overlays.Overlay.prototype.getGeometry = function () {
    return {
        'type': this.getGeometryType(),
        'coordinates': this.getCoordinates()
    };
};

komoo.overlays.Overlay.prototype.getProperties = function () {
    return null;
};

komoo.overlays.Overlay.prototype.setProperties = function (properties) {
};

komoo.overlays.Overlay.prototype.getFeature = function () {
    return {
        'type': 'Feature',
        'geometry': this.getGeometry(),
        'properties': this.getProperties()
    };
};

komoo.overlays.Overlay.prototype.getDefaultZIndex = function () {
    return this.type_ ? this.type_.getDefaultZIndex() :
        komoo.overlays.defaults.ZINDEX;
};

komoo.overlays.Overlay.prototype.setCoordinates = function (coordinates) {
    throw new Error('Not Implemented');
};

komoo.overlays.Overlay.prototype.getCoordinates = function () {
    throw new Error('Not Implemented');
};

komoo.overlays.Overlay.prototype.getLatLngFromArray = function (pos) {
    if (!pos) return null;
    return new google.maps.LatLng(pos[0], pos[1]);
};

komoo.overlays.Overlay.prototype.getArrayFromLatLng = function (latLng) {
    if (!latLng) return null;
    return [latLng.lat(), latLng.lng()];
};

/* Delegations */
komoo.overlays.Overlay.prototype.setMap = function (map) {
    return this.googleObject_.setMap(map);
};

komoo.overlays.Overlay.prototype.getMap = function () {
    return this.googleObject_.getMap();
};

komoo.overlays.Overlay.prototype.setVisible = function (visible) {
    return this.googleObject_.setVisible(visible);
};

komoo.overlays.Overlay.prototype.getVisible = function () {
    return this.googleObject_.getVisible();
}

komoo.overlays.Overlay.prototype.setOptions = function (options) {
    return this.googleObject_.setOptions(options);
};


/** Point Overlay **/

komoo.overlays.Point = function (opts) {
    komoo.overlays.Overlay.call(this, opts);
    this.geometryType_ = 'Point';
};

komoo.overlays.Point.prototype = Object.create(
        komoo.overlays.Overlay.prototype);

komoo.overlays.Point.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        zIndex: this.getDefaultZIndex(),
    };
    this.googleObject_ = new google.maps.Marker(options);
};

komoo.overlays.Point.prototype.initEvents = function () {
    komoo.overlays.Overlay.prototype.initEvents.call(this);
    var that = this;
    var eventsNames = ['animation_changed', 'clickable_changed',
        'cursor_changed', 'drag', 'dragend', 'daggable_changed', 'dragstart',
        'flat_changed', 'icon_changed', 'position_changed', 'shadow_changed',
        'shape_changed', 'title_changed', 'visible_changed', 'zindex_changed'];
    $.each(eventsNames, function(i, eventName) {
        google.maps.event.addListener(that.googleObject_,
                eventName, function (args) {
            google.maps.event.trigger(that, eventName, args);
        });
    });
};

komoo.overlays.Point.prototype.setCoordinates = function (coordinates) {
    this.setPosition(this.getLatLngFromArray(coordinates));
};

komoo.overlays.Point.prototype.getCoordinates = function () {
    return this.getArrayFromLatLng(this.getPosition());
};

/* Delegations */
komoo.overlays.Point.prototype.setPosition = function (latlng) {
    return this.googleObject_.setPosition(latlng);
};

komoo.overlays.Point.prototype.getPosition = function () {
    return this.googleObject_.getPosition();
};

komoo.overlays.Point.prototype.setIcon = function (icon) {
    return this.googleObject_.setIcon(icon);
};

komoo.overlays.Point.prototype.getIcon = function () {
    return this.googleObject_.getIcon();
};

komoo.overlays.Point.prototype.setDraggable = function (draggable) {
    return this.googleObject_.setDraggable(draggable);
};

komoo.overlays.Point.prototype.getDraggable = function () {
    return this.googleObject_.getDraggable();
};


/** Multipoint Overlay **/

komoo.overlays.MultiPoint = function (opts) {
    komoo.overlays.Overlay.call(this, opts);
    this.geometryType_ = 'MultiPoint';
};

komoo.overlays.MultiPoint.prototype = Object.create(
        komoo.overlays.Overlay.prototype);

komoo.overlays.MultiPoint.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        visible: true,
        zIndex: this.getDefaultZIndex(),
    };
    this.googleObject_ = new MultiMarker(options);
};

komoo.overlays.MultiPoint.prototype.setPoints = function (points) {
    this.googleObject_.addMarkers(points);
};

komoo.overlays.MultiPoint.prototype.getPoints = function () {
    return this.googleObject_.getMarkers().getArray();
};

komoo.overlays.MultiPoint.prototype._guaranteePoints = function (len) {
    var points = this.googleObject_.getMarkers();
    var missing;
    if (points.length > len) {
        missing = points.length - len;
        console.log(missing);
        for (var i=0; i<missing; i++) {
             points.pop();
        }
    } else if (points.length < len) {
        missing = len - points.length;
        for (var i=0; i<missing; i++) {
            this.googleObject_.addMarker(new komoo.overlays.Point());
        }
    }
};

komoo.overlays.MultiPoint.prototype.setCoordinates = function (coordinates) {
    var that = this;
    var coords = coordinates;
    if (!coords[0].pop) coords = [coords];
    console.log(coords);
    this._guaranteePoints(coords.length);
    $.each(this.getPoints(), function (i, point) {
        point.setPosition(that.getLatLngFromArray(coords[i]));
    });
};

komoo.overlays.MultiPoint.prototype.getCoordinates = function () {
    var that = this;
    var coords = [];
    $.each(this.getPoints(), function (i, point) {
        coords.push(that.getArrayFromLatLng(point.getPosition()));
    });
    return coords;
};

komoo.overlays.MultiPoint.prototype.setPositions = function (positions) {
    return this.googleObject_.setPositions(positions);
};

komoo.overlays.MultiPoint.prototype.getPositions = function () {
    return this.googleObject_.getPositions().getArray();
};

/* Delegations */
komoo.overlays.MultiPoint.prototype.addMarkers = function (markers) {
    this.googleObject_.addMarkers(markers);
};

komoo.overlays.MultiPoint.prototype.setIcon = function (icon) {
    return this.googleObject_.setIcon(icon);
};

komoo.overlays.MultiPoint.prototype.getIcon = function () {
    return this.googleObject_.getIcon();
};


/** Polyline Overlay **/

komoo.overlays.Polyline = function (opts) {
    komoo.overlays.Overlay.call(this, opts);
    this.geometryType_ = 'LineString';
};

komoo.overlays.Polyline.prototype = Object.create(
        komoo.overlays.Overlay.prototype);

komoo.overlays.Polyline.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        zIndex: this.getDefaultZIndex(),
        strokeColor: this.getBorderColor(),
        strockOpacity: this.getBorderOpacity(),
        strokeWeight: this.getBorderSize()
    };
    this.googleObject_ = new google.maps.Polyline(options);
};

komoo.overlays.Polyline.prototype.setCoordinates = function (coordinates) {
    var that = this;
    var path = [];
    $.each(coordinates, function (k, pos) {
        path.push(that.getLatLngFromArray(pos));
    });
    this.setPath(path);
};

komoo.overlays.Polyline.prototype.getCoordinates = function () {
    var that = this;
    var coords = [];
    this.getPath().forEach(function (latLng, i) {
        coords.push(that.getArrayFromLatLng(latLng));
    });
    return coords;
};

komoo.overlays.Polyline.prototype.getBorderColor = function () {
    return this.type_ ? this.type_.getBorderColor() :
        komoo.overlays.defaults.BORDER_COLOR;
};

komoo.overlays.Polyline.prototype.getBorderOpacity = function () {
    return this.type_ ? this.type_.getBorderOpacity() :
        komoo.overlays.defaults.BORDER_OPACITY;
}

komoo.overlays.Polyline.prototype.getBorderSize = function () {
    return this.type_ ? this.type_.getBorderSize() :
        komoo.overlays.defaults.BORDER_SIZE;
};

/* Delegations */
komoo.overlays.Polyline.prototype.setPath = function (path) {
    return this.googleObject_.setPath(path);
}

komoo.overlays.Polyline.prototype.getPath = function () {
    return this.googleObject_.getPath();
}


/** Polygon Overlay **/

komoo.overlays.Polygon = function (opts) {
    komoo.overlays.Polyline.call(this, opts);
    this.geometryType_ = 'Polygon';
};

komoo.overlays.Polygon.prototype = Object.create(
        komoo.overlays.Polyline.prototype);

komoo.overlays.Polygon.prototype.initGoogleObject = function (opts) {
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

komoo.overlays.Polygon.prototype.getBackgroundColor = function () {
    return this.type_ ? this.type_.getBackgroundColor() :
        komoo.overlays.defaults.BACKGROUND_COLOR;
};

komoo.overlays.Polygon.prototype.getBackgroundOpacity = function () {
    return this.type_ ? this.type_.getBackgroundOpacity() :
        komoo.overlays.defaults.BACKGROUND_OPACITY;
};

komoo.overlays.Polygon.prototype.setCoordinates = function (coordinates) {
    var that = this;
    var paths = [];
    $.each(coordinates, function (i, coord) {
        var path = [];
        $.each(coord, function (j, pos) {
            path.push(that.getLatLngFromArray(pos));
        });
        // Removes the last point that closes the loop
        // This point is not used by google maps
        path.pop()
        paths.push(path);
    });
    this.setPaths(paths);
};

komoo.overlays.Polygon.prototype.getCoordinates = function () {
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
komoo.overlays.Polygon.prototype.setPaths = function (paths) {
    return this.googleObject_.setPaths(paths);
}

komoo.overlays.Polygon.prototype.getPaths = function () {
    return this.googleObject_.getPaths();
}

