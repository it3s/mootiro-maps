if (typeof Object.create !== 'function') {
    Object.create = function (o) {
        function F() {}
        F.prototype = o;
        return new F();
    };
}

if (!window.komoo) komoo = {};

komoo.GeometryType = {};
komoo.GeometryType.POINT = 'marker';
komoo.GeometryType.MULTIPOINT = 'multimarker';
komoo.GeometryType.POLYGON = 'polygon';
komoo.GeometryType.POLYLINE = 'polyline';

komoo.geometries = {};

/** Default values **/

komoo.geometries.defaults = {};
komoo.geometries.defaults.BACKGROUND_COLOR = '#000';
komoo.geometries.defaults.BACKGROUND_OPACITY = 0.6;
komoo.geometries.defaults.BORDER_COLOR = '#000';
komoo.geometries.defaults.BORDER_OPACITY = 0.6;
komoo.geometries.defaults.BORDER_SIZE = 5;
komoo.geometries.defaults.ZINDEX = 1;

/** Geometry Factory **/

komoo.geometries.makeGeometry = function (feature) {
    var geometryType = feature.geometry.type;
    var geometry;
    if (geometryType == 'Point') {
        geometry = new komoo.geometries.Point();
    } else if (geometryType == 'MultiPoint') {
        geometry = new komoo.geometries.MultiPoint();
    } else if (geometryType == 'LineString') {
        geometry = new komoo.geometries.Polyline();
    } else if (geometryType == 'Polygon') {
        geometry = new komoo.geometries.Polygon();
    }
    return geometry;
};


/** Abstract Geometry **/

komoo.geometries.Geometry = function (opts) {
    this.initGoogleObject(opts);
    this.initEvents();
};

komoo.geometries.Geometry.prototype.initEvents = function () {
    var that = this;
    var eventsNames = ['click', 'dblclick', 'mousedown', 'mousemove',
        'mouseout', 'mouseover', 'mouseup', 'rightclick'];
    $.each(eventsNames, function(i, eventName) {
        google.maps.event.addListener(that.object_,
                eventName, function (args) {
            google.maps.event.trigger(that, eventName, args);
        });
    });
};

komoo.geometries.Geometry.prototype.initGoogleObject = function () {
};

komoo.geometries.Geometry.prototype.setObject = function (object) {
    this.object_ = object;
};

komoo.geometries.Geometry.prototype.setType = function (type) {
    this.type_ = type;
};

komoo.geometries.Geometry.prototype.getType = function () {
    return this.type_;
};

komoo.geometries.Geometry.prototype.getGeometryType = function () {
    return this.geometryType_;
};

komoo.geometries.Geometry.prototype.getGeometry = function () {
    return {
        'type': this.getGeometryType(),
        'coordinates': this.getCoordinates()
    };
};

komoo.geometries.Geometry.prototype.getProperties = function () {
    return null;
};

komoo.geometries.Geometry.prototype.setProperties = function (properties) {
};

komoo.geometries.Geometry.prototype.getFeature = function () {
    return {
        'type': 'Feature',
        'geometry': this.getGeometry(),
        'properties': this.getProperties()
    };
};

komoo.geometries.Geometry.prototype.getDefaultZIndex = function () {
    return this.type_ ? this.type_.getDefaultZIndex() :
        komoo.geometries.defaults.ZINDEX;
};

komoo.geometries.Geometry.prototype.setCoordinates = function (coordinates) {
    throw new Error('Not Implemented');
};

komoo.geometries.Geometry.prototype.getCoordinates = function () {
    throw new Error('Not Implemented');
};

komoo.geometries.Geometry.prototype.getLatLngFromArray = function (pos) {
    if (!pos) return null;
    return new google.maps.LatLng(pos[0], pos[1]);
};

komoo.geometries.Geometry.prototype.getArrayFromLatLng = function (latLng) {
    if (!latLng) return null;
    return [latLng.lat(), latLng.lng()];
};

/* Delegations */
komoo.geometries.Geometry.prototype.setMap = function (map) {
    return this.object_.setMap(map);
};

komoo.geometries.Geometry.prototype.getMap = function () {
    return this.object_.getMap();
};

komoo.geometries.Geometry.prototype.setVisible = function (visible) {
    return this.object_.setVisible(visible);
};

komoo.geometries.Geometry.prototype.getVisible = function () {
    return this.object_.getVisible();
}

komoo.geometries.Geometry.prototype.setOptions = function (options) {
    return this.object_.setOptions(options);
};


/** Point Geometry **/

komoo.geometries.Point = function (opts) {
    komoo.geometries.Geometry.call(this, opts);
    this.geometryType_ = 'Point';
};

komoo.geometries.Point.prototype = Object.create(
        komoo.geometries.Geometry.prototype);

komoo.geometries.Point.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        zIndex: this.getDefaultZIndex(),
    };
    this.object_ = new google.maps.Marker(options);
};

komoo.geometries.Point.prototype.initEvents = function () {
    komoo.geometries.Geometry.prototype.initEvents.call(this);
    var that = this;
    var eventsNames = ['animation_changed', 'clickable_changed',
        'cursor_changed', 'drag', 'dragend', 'daggable_changed', 'dragstart',
        'flat_changed', 'icon_changed', 'position_changed', 'shadow_changed',
        'shape_changed', 'title_changed', 'visible_changed', 'zindex_changed'];
    $.each(eventsNames, function(i, eventName) {
        google.maps.event.addListener(that.object_,
                eventName, function (args) {
            google.maps.event.trigger(that, eventName, args);
        });
    });
};

komoo.geometries.Point.prototype.setCoordinates = function (coordinates) {
    this.setPosition(this.getLatLngFromArray(coordinates));
};

komoo.geometries.Point.prototype.getCoordinates = function () {
    return this.getArrayFromLatLng(this.getPosition());
};

/* Delegations */
komoo.geometries.Point.prototype.setPosition = function (latlng) {
    return this.object_.setPosition(latlng);
};

komoo.geometries.Point.prototype.getPosition = function () {
    return this.object_.getPosition();
};

komoo.geometries.Point.prototype.setIcon = function (icon) {
    return this.object_.setIcon(icon);
};

komoo.geometries.Point.prototype.getIcon = function () {
    return this.object_.getIcon();
};

komoo.geometries.Point.prototype.setDraggable = function (draggable) {
    return this.object_.setDraggable(draggable);
};

komoo.geometries.Point.prototype.getDraggable = function () {
    return this.object_.getDraggable();
};


/** Multipoint Geometry **/

komoo.geometries.MultiPoint = function (opts) {
    komoo.geometries.Geometry.call(this, opts);
    this.geometryType_ = 'MultiPoint';
};

komoo.geometries.MultiPoint.prototype = Object.create(
        komoo.geometries.Geometry.prototype);

komoo.geometries.MultiPoint.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        visible: true,
        zIndex: this.getDefaultZIndex(),
    };
    this.object_ = new MultiMarker(options);
};

komoo.geometries.MultiPoint.prototype.setPoints = function (points) {
    this.object_.addMarkers(points);
};

komoo.geometries.MultiPoint.prototype.getPoints = function () {
    return this.object_.getMarkers().getArray();
};

komoo.geometries.MultiPoint.prototype._guaranteePoints = function (len) {
    var points = this.object_.getMarkers();
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
            this.object_.addMarker(new komoo.geometries.Point());
        }
    }
};

komoo.geometries.MultiPoint.prototype.setCoordinates = function (coordinates) {
    var that = this;
    var coords = coordinates;
    if (!coords[0].pop) coords = [coords];
    console.log(coords);
    this._guaranteePoints(coords.length);
    $.each(this.getPoints(), function (i, point) {
        point.setPosition(that.getLatLngFromArray(coords[i]));
    });
};

komoo.geometries.MultiPoint.prototype.getCoordinates = function () {
    var that = this;
    var coords = [];
    $.each(this.getPoints(), function (i, point) {
        coords.push(that.getArrayFromLatLng(point.getPosition()));
    });
    return coords;
};

komoo.geometries.MultiPoint.prototype.setPositions = function (positions) {
    return this.object_.setPositions(positions);
};

komoo.geometries.MultiPoint.prototype.getPositions = function () {
    return this.object_.getPositions().getArray();
};

/* Delegations */
komoo.geometries.MultiPoint.prototype.addMarkers = function (markers) {
    this.object_.addMarkers(markers);
};

komoo.geometries.MultiPoint.prototype.setIcon = function (icon) {
    return this.object_.setIcon(icon);
};

komoo.geometries.MultiPoint.prototype.getIcon = function () {
    return this.object_.getIcon();
};


/** Polyline Geometry **/

komoo.geometries.Polyline = function (opts) {
    komoo.geometries.Geometry.call(this, opts);
    this.geometryType_ = 'LineString';
};

komoo.geometries.Polyline.prototype = Object.create(
        komoo.geometries.Geometry.prototype);

komoo.geometries.Polyline.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        zIndex: this.getDefaultZIndex(),
        strokeColor: this.getBorderColor(),
        strockOpacity: this.getBorderOpacity(),
        strokeWeight: this.getBorderSize()
    };
    this.object_ = new google.maps.Polyline(options);
};

komoo.geometries.Polyline.prototype.setCoordinates = function (coordinates) {
    var that = this;
    var path = [];
    $.each(coordinates, function (k, pos) {
        path.push(that.getLatLngFromArray(pos));
    });
    this.setPath(path);
};

komoo.geometries.Polyline.prototype.getCoordinates = function () {
    var that = this;
    var coords = [];
    this.getPath().forEach(function (latLng, i) {
        coords.push(that.getArrayFromLatLng(latLng));
    });
    return coords;
};

komoo.geometries.Polyline.prototype.getBorderColor = function () {
    return this.type_ ? this.type_.getBorderColor() :
        komoo.geometries.defaults.BORDER_COLOR;
};

komoo.geometries.Polyline.prototype.getBorderOpacity = function () {
    return this.type_ ? this.type_.getBorderOpacity() :
        komoo.geometries.defaults.BORDER_OPACITY;
}

komoo.geometries.Polyline.prototype.getBorderSize = function () {
    return this.type_ ? this.type_.getBorderSize() :
        komoo.geometries.defaults.BORDER_SIZE;
};

/* Delegations */
komoo.geometries.Polyline.prototype.setPath = function (path) {
    return this.object_.setPath(path);
}

komoo.geometries.Polyline.prototype.getPath = function () {
    return this.object_.getPath();
}


/** Polygon Geometry **/

komoo.geometries.Polygon = function (opts) {
    komoo.geometries.Polyline.call(this, opts);
    this.geometryType_ = 'Polygon';
};

komoo.geometries.Polygon.prototype = Object.create(
        komoo.geometries.Polyline.prototype);

komoo.geometries.Polygon.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        zIndex: this.getDefaultZIndex(),
        fillColor: this.getBackgroundColor(),
        fillOpacity: this.getBackgroundOpacity(),
        strokeColor: this.getBorderColor(),
        strockOpacity: this.getBorderOpacity(),
        strokeWeight: this.getBorderSize()
    };
    this.object_ = new google.maps.Polygon(options);
};

komoo.geometries.Polygon.prototype.getBackgroundColor = function () {
    return this.type_ ? this.type_.getBackgroundColor() :
        komoo.geometries.defaults.BACKGROUND_COLOR;
};

komoo.geometries.Polygon.prototype.getBackgroundOpacity = function () {
    return this.type_ ? this.type_.getBackgroundOpacity() :
        komoo.geometries.defaults.BACKGROUND_OPACITY;
};

komoo.geometries.Polygon.prototype.setCoordinates = function (coordinates) {
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

komoo.geometries.Polygon.prototype.getCoordinates = function () {
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
komoo.geometries.Polygon.prototype.setPaths = function (paths) {
    return this.object_.setPaths(paths);
}

komoo.geometries.Polygon.prototype.getPaths = function () {
    return this.object_.getPaths();
}

