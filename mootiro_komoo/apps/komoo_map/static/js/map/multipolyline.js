/**
 * MultiPolyline for Google Maps.
 *
 * @name multipolyline.js
 * @fileOverview Group Google Maps Polylines together.
 * @version 0.1.0
 * @author Luiz Armesto
 * @copyright (c) 2012 it3s
 */

define(['googlemaps'], function (googleMaps) {
/**
 * @name MultiPolyineOptions
 * @class
 * @property {google.maps.Polyline[]} [polylines]
 * @property {google.maps.MVCArray[]} [paths]
 * @property {google.maps.Map} [map]
 * @property {boolean} [visible]
 * @property {boolean} [clickable]
 * @property {number} [zIndex]
 */

/**
 * @class
 * @param {MultiPolylineOptions} [opt_options]
 */
MultiPolyline = function (opt_options) {
    opt_options = opt_options || {};
    this.polylines_ = new googleMaps.MVCArray(opt_options.polylines || []);
    this.paths_ = new googleMaps.MVCArray(opt_options.paths || []);
    this.map_ = opt_options.map;
    this.visible_ = opt_options.visible;
    this.clickable_ = opt_options.clickable;
    this.zIndex = opt_options.zIndex || 0;
    this.strokeColor_ = opt_options.strokeColor || 'black';
    this.strokOpacity_ = opt_options.strokeOpacity || 1;
    this.strokeWeight_ = opt_options.strokeWeight || 3;
};


/**
 * @return {google.maps.LatLng[][]}
 */
MultiPolyline.prototype.getPaths = function () {
    this.paths_.clear();
    for (var i=0; i<this.polylines_.getLength(); i++) {
        this.paths_.push(this.polylines_.getAt(i).getPath());
    }
    return this.paths_
};


/**
 * @param {google.maps.LatLng[][]} paths The lines paths
 */
MultiPolyline.prototype.setPaths = function (paths) {
    if (paths.length != this.polylines_.getLength()) {
        // FIXME: Use a constant as exception.
        throw "Invalid length.";
    }
    this.paths_.clear();
    for (var i=0; i<this.polylines_.getLength(); i++) {
        this.polylines_.getAt(i).setPath(paths[i]);
        this.paths_.push(paths[i]);
    }
};


/**
 * @param {google.maps.Polyline} polyline
 * @param {boolean} [opt_keep=false]
 */
MultiPolyline.prototype.addPolyline = function (polyline, opt_keep) {
    var me = this;
    // TODO: verify if we already have added this polyline.
    this.polylines_.push(polyline);
    if (opt_keep != true) {
        polyline.setOptions({
            clickable: this.clickable_,
            zIndex: this.zIndex,
            strokeColor: this.strokeColor_,
            strokeOpacity: this.strokOpacity_,
            strokeWeight: this.strokeWeight_
        });
    }
    /**
     * @name komoo.MultiLine#click
     * @event
     */
    googleMaps.event.addListener(polyline, 'click', function (e) {
        googleMaps.event.trigger(me, 'click', e, polyline);
        });
    /**
     * @name komoo.MultiLine#mouseover
     * @event
     */
    googleMaps.event.addListener(polyline, 'mouseover', function (e) {
        googleMaps.event.trigger(me, 'mouseover', e, polyline);
    });
    /**
     * @name komoo.MultiLine#mouseout
     * @event
     */
    googleMaps.event.addListener(polyline, 'mouseout', function (e) {
        googleMaps.event.trigger(me, 'mouseout', e, polyline);
    });
    /**
     * @name komoo.MultiLine#mousemove
     * @event
     */
    googleMaps.event.addListener(polyline, 'mousemove', function (e) {
        googleMaps.event.trigger(me, 'mousemove', e, polyline);
    });
};


/**
 * @param {google.maps.Polyline[]} polylines
 * @param {boolean} [opt_keep=false]
 */
MultiPolyline.prototype.addPolylines = function (polylines, opt_keep) {
    for (var i=0; i<polylines.length; i++) {
        this.addPolyline(polylines[i], opt_keep);
    }
};


/**
 * @returns {google.maps.Polyline[]}
 */
MultiPolyline.prototype.getPolylines = function () {
    return this.polylines_;
};

/**
 * @param {google.maps.Map} map
 */
MultiPolyline.prototype.setMap = function (map) {
    for (var i=0; i<this.polylines_.getLength(); i++) {
        this.polylines_.getAt(i).setMap(map);
    }
    this.map_ = map;
};


/**
 * @returns {google.maps.Map}
 */
MultiPolyline.prototype.getMap = function () {
    return this.map_;
};

/**
 * @param {boolean} flag
 */
MultiPolyline.prototype.setVisible = function (flag) {
    for (var i=0; i<this.polylines_.getLength(); i++) {
        this.polylines_.getAt(i).setVisible(flag);
    }
    this.visible_ = flag;
};

/**
 * @param {boolean} flag
 */
MultiPolyline.prototype.setEditable = function (flag) {
    for (var i=0; i<this.polylines_.getLength(); i++) {
        this.polylines_.getAt(i).setEditable(flag);
    }
    this.visible_ = flag;
};

/**
 * @param {boolean} options
 */
MultiPolyline.prototype.setOptions = function (options) {
    for (var i=0; i<this.polylines_.getLength(); i++) {
        this.polylines_.getAt(i).setOptions(options);
    }
    this.options_ = options;
};


/**
 * @returns {boolean}
 */
MultiPolyline.prototype.getVisible = function () {
    return this.visible_;
};

return MultiPolyline;

});
