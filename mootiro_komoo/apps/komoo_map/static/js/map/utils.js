/**
 * utils.js
 * requires compat.js
 */


if (!window.komoo) komoo = {};
komoo.utils = {};

/**
 * Creates a cookie and save it.
 * @param {String} name
 * @param {String | number} value
 * @param {number} days
 */
komoo.utils.createCookie = function (name, value, days) {
    var expires;
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    }
    else {
        expires = "";
    }
    document.cookie = name + "=" + value + expires + "; path=/";
};

/**
 * Reads a cookie.
 * @param {String} name
 * @returns {String}
 */
komoo.utils.readCookie = function (name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(";");
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == " ") {
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
komoo.utils.eraseCookie = function (name) {
    createCookie(name, "", -1);
};

/**
 * Verify if a point is inside a closed path.
 * @param {google.maps.LatLng} point
 * @param {google.maps.MVCArray(google.maps.LatLng)} path
 * @returns {boolean}
 */
komoo.utils.isPointInside = function (point, path) {
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
 * @param {google.maps.Map} map
 * @param {google.maps.LatLng} latlng
 * @param {int} z
 * @return {google.maps.Point}
 */
komoo.utils.latLngToPoint = function (map, latLng, opt_zoom) {
    if (map.googleMap) map = map.googleMap;
    var zoom = opt_zoom || map.getZoom();
    var normalizedPoint = map.getProjection().fromLatLngToPoint(latLng); // returns x,y normalized to 0~255
    var scale = Math.pow(2, zoom);
    var pixelCoordinate = new google.maps.Point(normalizedPoint.x * scale, normalizedPoint.y * scale);
    return pixelCoordinate;
};

/**
 * @param {google.maps.Map} map
 * @param {google.maps.Point} point
 * @param {int} z
 * @return {google.maps.LatLng}
 */
komoo.utils.pointToLatLng = function (map, point, opt_zoom) {
    if (map.googleMap) map = map.googleMap;
    var zoom = opt_zoom || map.getZoom();
    var scale = Math.pow(2, zoom);
    var normalizedPoint = new google.maps.Point(point.x / scale, point.y / scale);
    var latlng = map.getProjection().fromPointToLatLng(normalizedPoint);
    return latlng;
};
