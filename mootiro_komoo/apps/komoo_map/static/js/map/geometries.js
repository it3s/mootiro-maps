/**
 * geometries.js
 * requires compat.js
 */


if (!window.komoo) komoo = {};
if (!komoo.event) komoo.event = google.maps.event;

/** Geometry Types **/

komoo.GeometryType = {};
komoo.GeometryType.POINT = 'Point';
komoo.GeometryType.MULTIPOINT = 'MultiPoint';
komoo.GeometryType.POLYGON = 'Polygon';
komoo.GeometryType.POLYLINE = 'LineString';
komoo.GeometryType.MULTIPOLYLINE = 'MultiLineString';

komoo.geometries = {};

/** Default values **/

komoo.geometries.defaults = {};
komoo.geometries.defaults.BACKGROUND_COLOR = '#000';
komoo.geometries.defaults.BACKGROUND_OPACITY = 0.6;
komoo.geometries.defaults.BORDER_COLOR = '#000';
komoo.geometries.defaults.BORDER_OPACITY = 0.6;
komoo.geometries.defaults.BORDER_SIZE = 1.5;
komoo.geometries.defaults.ZINDEX = 1;


/** Geometry Factory **/

komoo.geometries.makeGeometry = function (feature) {
    if (!feature.geometry) return;
    var geometryType = feature.geometry.type;
    var geometry;
    if (geometryType == 'Point' || geometryType == 'MultiPoint' || geometryType == 'marker') {
        geometry = new komoo.geometries.MultiPoint();
    } else if (geometryType == 'LineString') {
        if(feature.geometry.coordinates) feature.geometry.coordinates = [feature.geometry.coordinates];
        geometry = new komoo.geometries.MultiPolyline();
    } else if (geometryType == 'MultiLineString' || geometryType == 'polyline') {
        geometry = new komoo.geometries.MultiPolyline();
    } else if (geometryType == 'Polygon' || geometryType == 'polygon') {
        geometry = new komoo.geometries.Polygon();
    }

    if (geometry && feature.geometry.coordinates) geometry.setCoordinates(feature.geometry.coordinates);

    return geometry;
};


/** Abstract Geometry **/

komoo.geometries.Geometry = function (opts) {
    this.initGoogleObject(opts);
};

komoo.geometries.Geometry.prototype.initEvents = function () {
    var that = this;
    var eventsNames = ['click', 'dblclick', 'mousedown', 'mousemove',
        'mouseout', 'mouseover', 'mouseup', 'rightclick'];
    eventsNames.forEach(function(eventName, index, orig) {
        google.maps.event.addListener(that.object_,
                eventName, function (e, args) {
            komoo.event.trigger(that, eventName, e, args);
        });
    });
};

komoo.geometries.Geometry.prototype.calculateBounds = function () {
    var that = this;
    var bounds;
    var n, w, s, e;
    var getBounds = function (pos) {
        if (n === undefined) {
            n = s = pos[0];
            w = e = pos[1];
        }
        n = Math.max(pos[0], n);
        s = Math.min(pos[0], s);
        w = Math.min(pos[1], w);
        e = Math.max(pos[1], e);
        return [[s, w], [n, e]];
    };
    var coordinates = this.getCoordinates();
    if (this.getGeometryType() != komoo.GeometryType.POLYGON &&
        this.getGeometryType() != komoo.GeometryType.MULTIPOLYLINE)
        coordinates = [coordinates];
    coordinates.forEach(function (path, index, orig) {
        path.forEach(function (pos, index_, orig_) {
            bounds = getBounds(pos);
        });
    });
    this.bounds_ = new google.maps.LatLngBounds(
            this.getLatLngFromArray(bounds[0]),
            this.getLatLngFromArray(bounds[1])
        );
    this.bounds = this.bounds_; // TODO: This should be removed
    return this.bounds_;
};

komoo.geometries.Geometry.prototype.getBounds = function () {
    if (this.bounds_ == undefined)
        this.calculateBounds();
    return this.bounds_;
};

komoo.geometries.Geometry.prototype.getCenter = function () {
    var overlayCenter;
    if (this.object_.getCenter) {
        overlayCenter = this.object_.getCenter();
    } else if (this.object_.getPosition) {
        overlayCenter = this.object_.getPosition();
    } else if (this.getBounds) {
        overlayCenter = this.getBounds().getCenter();
    }
    return overlayCenter;
};

komoo.geometries.Geometry.prototype.initGoogleObject = function () {
};

komoo.geometries.Geometry.prototype.setObject = function (object) {
    this.object_ = object;
    this.initEvents();
};

komoo.geometries.Geometry.prototype.getObject = function () {
    return this.object_;
};

komoo.geometries.Geometry.prototype.setFeature = function (feature) {
    this.feature_ = feature;
};

komoo.geometries.Geometry.prototype.getFeature = function () {
    return this.feature_;
};

komoo.geometries.Geometry.prototype.getGeometryType = function () {
    return this.geometryType_;
};

komoo.geometries.Geometry.prototype.getDefaultZIndex = function () {
    return this.feature_ ? this.feature_.getDefaultZIndex() :
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

komoo.geometries.Geometry.prototype.getLatLngArrayFromArray = function (pos) {
    if (!pos) return null;
    var that = this;
    var pos_ = [];
    pos.forEach(function (p, index, orig) {
        pos_.push(that.getLatLngFromArray(p));
    });
    return pos_;
};

komoo.geometries.Geometry.prototype.getArrayFromLatLngArray = function (latLngs) {
    if (!latLngs) return null;
    var that = this;
    var latLngs_ = [];
    latLngs.forEach(function (latLng, index, orig) {
        latLngs_.push(that.getArrayFromLatLng(latLng));
    });
    return latLngs_;
};

komoo.geometries.Geometry.prototype.getArrayFromLatLng = function (latLng) {
    if (!latLng) return null;
    return [latLng.lat(), latLng.lng()];
};

/* Delegations */
komoo.geometries.Geometry.prototype.setMap = function (map) {
    if (map instanceof komoo.Map)
        return this.object_.setMap(map.googleMap);
    else
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
    this.geometryType_ = komoo.GeometryType.POINT;
};

komoo.geometries.Point.prototype = Object.create(
        komoo.geometries.Geometry.prototype);

komoo.geometries.Point.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        zIndex: this.getDefaultZIndex(),
    };
    this.setObject(new google.maps.Marker(options));
};

komoo.geometries.Point.prototype.initEvents = function () {
    komoo.geometries.Geometry.prototype.initEvents.call(this);
    var that = this;
    var eventsNames = ['animation_changed', 'clickable_changed',
        'cursor_changed', 'drag', 'dragend', 'daggable_changed', 'dragstart',
        'flat_changed', 'icon_changed', 'position_changed', 'shadow_changed',
        'shape_changed', 'title_changed', 'visible_changed', 'zindex_changed'];
    eventsNames.forEach(function(eventName, index, orig) {
        google.maps.event.addListener(that.object_,
                eventName, function (e, args) {
            komoo.event.trigger(that, eventName, e, args);
        });
    });
};

komoo.geometries.Point.prototype.setCoordinates = function (coordinates) {
    this.bounds_ = undefined;
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
    this.geometryType_ = komoo.GeometryType.MULTIPOINT;
};

komoo.geometries.MultiPoint.prototype = Object.create(
        komoo.geometries.Geometry.prototype);

komoo.geometries.MultiPoint.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        visible: true,
        zIndex: this.getDefaultZIndex(),
    };
    this.setObject(new MultiMarker(options));
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
    this._guaranteePoints(coords.length);
    this.bounds_ = undefined;
    this.getPoints().forEach(function (point, index, orig) {
        point.setPosition(that.getLatLngFromArray(coords[index]));
    });
    komoo.event.trigger(this, 'coordinates_changed');
};

komoo.geometries.MultiPoint.prototype.getCoordinates = function () {
    var that = this;
    var coords = [];
    this.getPoints().forEach(function (point, index, orig) {
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

komoo.geometries.MultiPoint.prototype.getMarkers = function () {
    return this.object_.getMarkers();
};

komoo.geometries.MultiPoint.prototype.addMarker = function (marker) {
    this.object_.addMarker(marker);
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
    this.geometryType_ = komoo.GeometryType.POLYLINE;
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
    this.setObject(new google.maps.Polyline(options));
};

komoo.geometries.Polyline.prototype.setCoordinates = function (coordinates) {
    var that = this;
    var path = [];
    this.bounds_ = undefined;
    coordinates.forEach(function (pos, index, orig) {
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
    return this.feature_ ? this.feature_.getBorderColor() :
        komoo.geometries.defaults.BORDER_COLOR;
};

komoo.geometries.Polyline.prototype.getBorderOpacity = function () {
    return this.feature_ ? this.feature_.getBorderOpacity() :
        komoo.geometries.defaults.BORDER_OPACITY;
}

komoo.geometries.Polyline.prototype.getBorderSize = function () {
    return this.feature_ ? this.feature_.getBorderSize() :
        komoo.geometries.defaults.BORDER_SIZE;
};


komoo.geometries.Polyline.prototype.setIcon = function (icon) {
    if (this.marker) this.marker.setIcon(icon);
};

/* Delegations */
komoo.geometries.Polyline.prototype.setPath = function (path) {
    return this.object_.setPath(path);
}

komoo.geometries.Polyline.prototype.getPath = function () {
    return this.object_.getPath();
}

komoo.geometries.Polyline.prototype.setEditable = function (flag) {
    return this.object_.setEditable(flag);
}




/** MultiLineString Geometry **/

komoo.geometries.MultiPolyline = function (opts) {
    komoo.geometries.Geometry.call(this, opts);
    this.geometryType_ = komoo.GeometryType.MULTIPOLYLINE;
};

komoo.geometries.MultiPolyline.prototype = Object.create(
        komoo.geometries.Polyline.prototype);

komoo.geometries.MultiPolyline.prototype.initGoogleObject = function (opts) {
    var options = opts || {
        clickable: true,
        zIndex: this.getDefaultZIndex(),
        strokeColor: this.getBorderColor(),
        strockOpacity: this.getBorderOpacity(),
        strokeWeight: this.getBorderSize()
    };
    this.options_ = options;
    this.setObject(new MultiPolyline(options));
};

komoo.geometries.MultiPolyline.prototype.setLines = function (lines) {
    this.object_.addPolylines(lines);
};

komoo.geometries.MultiPolyline.prototype.getLines = function () {
    return this.object_.getPolylines().getArray();
};

komoo.geometries.MultiPolyline.prototype._guaranteeLines = function (len) {
    var lines = this.object_.getPolylines();
    var missing;
    if (lines.length > len) {
        missing = lines.length - len;
        for (var i=0; i<missing; i++) {
             lines.pop();
        }
    } else if (lines.length < len) {
        missing = len - lines.length;
        for (var i=0; i<missing; i++) {
            this.object_.addPolyline(new komoo.geometries.Polyline(this.options_));
        }
    }
};

komoo.geometries.MultiPolyline.prototype.setCoordinates = function (coordinates) {
    var that = this;
    var coords = coordinates;
    if (!coords[0].pop) coords = [coords];
    this._guaranteeLines(coords.length);
    this.bounds_ = undefined;
    this.getLines().forEach(function (line, index, orig) {
        line.setPath(that.getLatLngArrayFromArray(coords[index]));
    });
    komoo.event.trigger(this, 'coordinates_changed');
};

komoo.geometries.MultiPolyline.prototype.getCoordinates = function () {
    var that = this;
    var coords = [];
    this.getLines().forEach(function (line, index, orig) {
        coords.push(that.getArrayFromLatLngArray(line.getPath()));
    });
    return coords;
};

komoo.geometries.MultiPolyline.prototype.setPaths = function (paths) {
    return this.object_.setPaths(paths);
};

komoo.geometries.MultiPolyline.prototype.getPaths = function () {
    return this.object_.getPaths().getArray();
};

komoo.geometries.MultiPolyline.prototype.getPath = function () {
    return this.object_.getPaths().getAt(0);
}



/** Polygon Geometry **/

komoo.geometries.Polygon = function (opts) {
    komoo.geometries.Polyline.call(this, opts);
    this.geometryType_ = komoo.GeometryType.POLYGON;
    this.handleEvents();
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
    this.setObject(new google.maps.Polygon(options));
};

komoo.geometries.Polygon.prototype.handleEvents = function () {
    var that = this;
    komoo.event.addListener(this,'mousemove', function (e) {
        that.setOptions({strokeWeight: 2.5});
    });
    komoo.event.addListener(this, 'mouseout', function (e) {
        that.setOptions({strokeWeight: that.getBorderSize()});
    });
};

komoo.geometries.Polygon.prototype.getBackgroundColor = function () {
    return this.feature_ ? this.feature_.getBackgroundColor() :
        komoo.geometries.defaults.BACKGROUND_COLOR;
};

komoo.geometries.Polygon.prototype.getBackgroundOpacity = function () {
    return this.feature_ ? this.feature_.getBackgroundOpacity() :
        komoo.geometries.defaults.BACKGROUND_OPACITY;
};

komoo.geometries.Polygon.prototype.setCoordinates = function (coordinates) {
    var that = this;
    var paths = [];
    this.bounds_ = undefined;
    coordinates.forEach(function (coord, index, orig) {
        var path = [];
        coord.forEach(function (pos, index_, orig_) {
            path.push(that.getLatLngFromArray(pos));
        });
        // Removes the last point that closes th
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

