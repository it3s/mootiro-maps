/**
 * features.js
 * requires compat.js
 */


if (!window.komoo) komoo = {};
if (!komoo.event) komoo.event = google.maps.event;

komoo.features = {};


/** Feature Factory **/

komoo.features.makeFeature = function (feature) {
    var feature_ = new komoo.features.Feature();
    if (feature) {
        feature_.setProperties(feature.properties);
        var geometry = komoo.geometries.makeGeometry(feature);
        feature_.setGeometry(geometry);
    }

    return feature_;
};


/** Abstract feature **/

komoo.features.Feature = function (opts) {
    var options = opts || {};
    if (options.geometry) this.setGeometry(options.geometry)
};

komoo.features.Feature.prototype.initEvents = function (opt_object) {
    var that = this;
    var object = opt_object || this.getGeometry();
    var eventsNames = ['click', 'dblclick', 'mousedown', 'mousemove',
        'mouseout', 'mouseover', 'mouseup', 'rightclick',
        'drag', 'dragend', 'daggable_changed', 'dragstart',
        'coordinates_changed'];
    eventsNames.forEach(function(eventName, index, orig) {
        komoo.event.addListener(object, eventName, function (e, args) {
            komoo.event.trigger(that, eventName, e, args);
        });
    });
};


komoo.features.Feature.prototype.setGeometry = function (geometry) {
    this.geometry_ = geometry;
    this.initEvents();
};

komoo.features.Feature.prototype.getGeometry = function () {
    return this.geometry_;
};

komoo.features.Feature.prototype.getGeometryType = function () {
    return this.geometry_.getGeometryType();
};

komoo.features.Feature.prototype.setMarker = function (marker) {
    if (!this.getGeometry() || 
            this.getGeometry() instanceof komoo.geometries.MultiPoint) 
        return;
    this.marker_ = marker;
    this.initEvents(marker);
};

komoo.features.Feature.prototype.getMarker = function () {
    return this.marker_;
};

komoo.features.Feature.prototype.handleGeometryEvents = function () {
    var that = this;
    komoo.event.addListener(this.geometry_, 'coordinates_changed',
            this.onGeometryCoordinatesChanged);
};

komoo.features.Feature.prototype.onGeometryCoordinatesChanged = function (args) {
    this.updateIcon();
    komoo.event.trigger(this, 'coordinates_changed', args);
};

komoo.features.Feature.prototype.getUrl = function () {
    var url;
    if (this.properties_.type == 'Community') {
        url = dutils.urls.resolve('view_community',
                {community_slug: this.properties_.community_slug});
    } else if (this.properties_.type == 'Resource') {
        url = dutils.urls.resolve('view_resource', {
                    resource_id: this.properties_.id
                }).replace('//', '/');
    }  else if (this.properties_.type == 'OrganizationBranch') {
        url = dutils.urls.resolve('view_organization', {
                    organization_slug: this.properties_.organization_slug || ''
                }).replace('//', '/');
    }  else {
        var slugname = this.properties_.type.toLowerCase() + '_slug';
        var params = {'community_slug': this.properties_.community_slug};
        params[slugname] = this.properties_[slugname];
        url = dutils.urls.resolve('view_' + this.properties_.type.toLowerCase(), params).replace('//', '/');
    }
    return url;
};

komoo.features.Feature.prototype.isHighlighted = function () {
    return this.highlighted;
};

komoo.features.Feature.prototype.setHighlight = function (flag) {
    this.highlighted = flag;
    this.updateIcon();
    komoo.event.trigger(this, 'highlight_changed', flag);
};

komoo.features.Feature.prototype.getIconUrl = function (optZoom) {
    if (!this.getProperties()) return;
    var zoom = optZoom || 10;
    var url = '/static/img/';
    if (zoom >= 15) {
        url += 'near';
    } else {
        url += 'far';
    }
    url += '/';
    if (this.isHighlighted()) {
        url += 'highlighted/';
    }

    if (this.getProperties().categories && this.getProperties().categories[0]) {
        url += this.getProperties().categories[0].name.toLowerCase();
        if (this.getProperties().categories.length > 1) {
            url += '-plus';
        }
    } else {
        url += this.getProperties().type.toLowerCase();
    }
    url += '.png';
    url = url.replace(' ', '-');
    return url;
};

komoo.features.Feature.prototype.updateIcon = function (optZoom) {
    this.setIcon(this.getIconUrl(optZoom));
};

komoo.features.Feature.prototype.getCategoriesIcons = function () {
    var icons = [];
    var url = '/static/need_categories/';

    if (this.getProperties().categories)
        this.getProperties().categories.forEach(function (category, index, orig) {
            icons.push(url + category.name.toLowerCase() + '.png');
        });

    return icons;
};

komoo.features.Feature.prototype.setProperties = function (properties) {
    this.properties_ = properties;
};

komoo.features.Feature.prototype.getProperties = function () {
    return this.properties_;
};

komoo.features.Feature.prototype.getGeoJsonGeometry = function () {
    return {
        'type': this.geometry_.getGeometryType(),
        'coordinates': this.geometry_.getCoordinates()
    };
};

komoo.features.Feature.prototype.getGeoJsonFeature = function () {
    return {
        'type': 'Feature',
        'geometry': this.getGeoJsonGeometry(),
        'properties': this.getProperties()
    };
};

komoo.features.Feature.prototype.setEditable = function (flag) {
    if (this.geometry_.setEditable) {
        return this.geometry_.setEditable(flag);
    } else if (this.geometry_.setDraggable) {
        return this.geometry.setDraggable(flag);
    }
};

komoo.features.Feature.prototype.showGeometry = function () {
    this.geometry_.setMap(this.map_);
};

komoo.features.Feature.prototype.hideGeometry = function () {
    this.geometry_.setMap(null);
};

komoo.features.Feature.prototype.showMarker = function () {
    if (this.getMarker() && 
            !(this.getGeometry() instanceof komoo.geometries.MultiPoint)) 
        this.getMarker().setMap(this.map_);
};

komoo.features.Feature.prototype.hideMarker = function () {
    if (this.getMarker() && 
            !(this.getGeometry() instanceof komoo.geometries.MultiPoint)) 
        this.getMarker().setMap(null);
};

komoo.features.Feature.prototype.setMap = function (map, opt_force) {
    var force = opt_force != undefined ? opt_force : {geometries: false, markers: false};
    if (this.getProperties().alwaysVisible) force = {geometries: true, markers: false};
    var zoom = 0;
    if (map) zoom = map.getZoom();
    if (map && ((zoom <= this.maxZoomGeometry && zoom >= this.minZoomGeometry) || force.geometries)) {
        this.geometry_.setMap(map);
    } else {
        this.geometry_.setMap(null);
    }
    if (this.getMarker() && 
            !(this.getGeometry() instanceof komoo.geometries.MultiPoint)) { 
        if (map && ((zoom <= this.maxZoomMarker && zoom >= this.minZoomMarker) || force.markers)) {
            this.getMarker().setMap(map);
        } else {
            this.getMarker().setMap(null);
        }
    }
    this.map_ = map;
};

komoo.features.Feature.prototype.getMap = function () {
    return this.map_;
};

/* Delegations */

komoo.features.Feature.prototype.getBounds = function () {
    return this.geometry_.getBounds();
};

komoo.features.Feature.prototype.removeFromMap = function () {
    this.setMap(null);
    if (this.marker_) this.marker_.setMap(null);
};

komoo.features.Feature.prototype.setVisible = function (flag) {
    if (this.getMarker() && 
            !(this.getGeometry() instanceof komoo.geometries.MultiPoint)) { 
        this.marker_.setVisible(flag);
    }
    return this.geometry_.setVisible(flag);
};

komoo.features.Feature.prototype.getCenter = function () {
    return this.geometry_.getCenter();
};

/* Temporary methods */

komoo.features.Feature.prototype.setOptions = function (options) {
    return this.geometry_.setOptions(options);
};

komoo.features.Feature.prototype.setIcon = function (icon) {
    return this.geometry_.setIcon(icon);
};

komoo.features.Feature.prototype.getIcon = function () {
    return this.geometry_.getIcon();
};

