/**
 * MultiMarker for Google Maps.
 *
 * @name multimarker.js
 * @fileOverview Group Google Maps Markers together.
 * @version 0.1.0
 * @author Luiz Armesto
 * @copyright (c) 2012 it3s
 */

/**
 * @name MultiMarkerOptions
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
 * @param {MultiMarkerOptions} [opt_options]
 */
MultiMarker = function (opt_options) {
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
 * @return {google.maps.LatLng}
 */
MultiMarker.prototype.getPosition = function () {
    return this.markers_.getAt(0).getPosition();
};


/**
 * @return {google.maps.LatLng[]}
 */
MultiMarker.prototype.getPositions = function () {
    this.positions_.clear();
    for (var i=0; i<this.markers_.getLength(); i++) {
        this.positions_.push(this.markers_.getAt(i).getPosition());
    }
    return this.positions_
};


/**
 * @param {google.maps.LatLng[]} positions The positions
 */
MultiMarker.prototype.setPositions = function (positions) {
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
MultiMarker.prototype.addMarker = function (marker, opt_keep) {
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
MultiMarker.prototype.addMarkers = function (markers, opt_keep) {
    for (var i=0; i<markers.length; i++) {
        this.addMarker(markers[i], opt_keep);
    }
};


/**
 * @returns {google.maps.Marker[]}
 */
MultiMarker.prototype.getMarkers = function () {
    return this.markers_;
};


/**
 * @param {boolean} flag
 */
MultiMarker.prototype.setDraggable = function (flag) {
    for (var i=0; i<this.markers_.getLength(); i++) {
        this.markers_.getAt(i).setDraggable(flag);
    }
    this.draggable_ = flag;
};


/**
 * @returns {boolean}
 */
MultiMarker.prototype.getDraggable = function () {
    return this.draggable_;
};


/**
 * @param {google.maps.Map} map
 */
MultiMarker.prototype.setMap = function (map) {
    for (var i=0; i<this.markers_.getLength(); i++) {
        this.markers_.getAt(i).setMap(map);
    }
    this.map_ = map;
};


/**
 * @returns {google.maps.Map}
 */
MultiMarker.prototype.getMap = function () {
    return this.map_;
};


/**
 * @param {string | google.maps.MarkerIcon} icon
 */
MultiMarker.prototype.setIcon = function (icon) {
    for (var i=0; i<this.markers_.getLength(); i++) {
        this.markers_.getAt(i).setIcon(icon);
    }
    this.icon_ = icon;
};


/**
 * @returns {string | google.maps.MarkerIcon}
 */
MultiMarker.prototype.getIcon = function () {
    return this.icon_;
};


/**
 * @param {boolean} flag
 */
MultiMarker.prototype.setVisible = function (flag) {
    for (var i=0; i<this.markers_.getLength(); i++) {
        this.markers_.getAt(i).setVisible(flag);
    }
    this.visible_ = flag;
};


/**
 * @returns {boolean}
 */
MultiMarker.prototype.getVisible = function () {
    return this.visible_;
};

