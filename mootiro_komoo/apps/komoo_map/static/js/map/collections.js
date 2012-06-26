/**
 * collections.js
 * requires compat.js
 */


if (!window.komoo) komoo = {};
if (!komoo.event) komoo.event = google.maps.event;

if (!komoo.collections) komoo.collections = {};

/** FeatureCollection Factory **/

komoo.collections.makeFeatureCollection = function (opts) {
    var options = opts || {};
    var features = options.features || [];

    var featureCollection = new komoo.collections.FeatureCollection();

    if (features) features.forEach(function (feature, index, orig) {
        featureCollections.push(feature);
    });

    return featureCollection;
};


/** Feature Collection **/

komoo.collections.FeatureCollection = function (opts) {
    this.features_ = [];
    this.length = 0;
};

komoo.collections.FeatureCollection.prototype.getGeoJson = function () {
    var features = [];
    var geoJSON = {
        'type': 'FeatureCollection',
        'features': features
    };
    this.features_.forEach(function (feature, index, orig) {
        features.push(feature.getGeoJsonFeature());
    });
    return geoJSON;
};

komoo.collections.FeatureCollection.prototype.clear = function () {
    this.features_ = [];
    this.updateLength_();
};

komoo.collections.FeatureCollection.prototype.removeAllFromMap = function () {
    this.features_.forEach(function (feature, index, orig) {
        feature.removeFromMap();
    });
};

komoo.collections.FeatureCollection.prototype.getAt = function (index) {
    return this.features_[index];
};

/* Private methods */

komoo.collections.FeatureCollection.prototype.updateLength_ = function () {
    this.length = this.features_.length;
}


/* Delegations */

komoo.collections.FeatureCollection.prototype.push = function (feature) {
   this.features_.push(feature); 
   this.updateLength_();
};

komoo.collections.FeatureCollection.prototype.pop = function () {
   var element = this.features_.pop(); 
   this.updateLength_();
   return element;
};

komoo.collections.FeatureCollection.prototype.forEach = function (callback, thisArg) {
   this.features_.forEach(callback, thisArg); 
};
