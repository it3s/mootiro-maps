/**
 * controls.js
 * requires compat.js
 */


if (!window.komoo) komoo = {};
if (!komoo.event) komoo.event = google.maps.event;
if (!komoo.controls) komoo.controls = {};


/** FeatureCollection Factory **/

komoo.controls.makeInfoWindow = function (opts) {
    var options = opts || {};

    var infoWindow = new komoo.controls.InfoWindow(options);

    return infoWindow;
};


/** Info Window **/

komoo.controls.InfoWindow = function (opts) {
    var options = opts || {};
    var infoWindowOptions = {
        pixelOffset: new google.maps.Size(0, -20),
        closeBoxMargin: '10px',
        boxStyle: {
            cursor: 'pointer',
            background: 'url(/static/img/infowindow-arrow.png) no-repeat 0 10px',  // FIXME: Hardcode is evil
            width: '200px'
        }
    };
    this.object_ = new InfoBox(infoWindowOptions);
    this.setMap(options.map);
    this.customize_();
};

komoo.controls.InfoWindow.prototype.setMap = function (map) {
    this.map_ = map;
};

komoo.controls.InfoWindow.prototype.open = function (opts) {
    var options = opts || {};
    var feature = options.feature;
    var content = options.content;
    if (this.map_.mode != komoo.Mode.NAVIGATE) return;
    var position = options.position || feature.getCenter();
    var url, population, msg;
    if (content) {
        this.title.attr('href', '#');
        this.title.text('');
        this.body.html(content);
    } else {
        url = feature.getUrl();
        this.title.text(feature.getProperties().name);
        this.body.html('');

        if (feature.getProperties().type == 'Community') {
            if (feature.getProperties().population) {
                msg = ngettext('%s resident', '%s residents', feature.getProperties().population);
                population = interpolate(msg, [feature.getProperties().population])
            } else {
                population = gettext('No population provided');
            }
            this.body.html('<ul><li>' + population + '</li></ul>');
        }  else if (feature.getProperties().type == 'OrganizationBranch') {
            this.title.text(feature.getProperties().organization_name + ' - ' + feature.getProperties().name);
        }
        this.title.attr('href', url);

        if (feature.getProperties().categories) {
            var categoriesIcons = feature.getCategoriesIcons();
            var icons = '<div class="categories-icons">';
            categoriesIcons.forEach(function (icon, index, orig) {
                icons += '<img src="' + icon + '">';
            });
            icons += '</div>';
            this.body.html(this.body.html() + icons);
        }

        this.feature = feature;
    }
    var point = komoo.utils.latLngToPoint(this.map_, position);
    point.x += 5;
    var newPosition = komoo.utils.pointToLatLng(this.map_, point);
    this.object_.setPosition(newPosition);
    this.object_.open(this.map_.googleMap ? this.map_.googleMap : this.map_);
};

komoo.controls.InfoWindow.prototype.close = function () {
    this.object_.close();
    if (this.feature && this.feature.isHighlighted()) {
        this.feature.updateIcon();
        this.feature.setHighlight(false);
    }
    this.feature = undefined;
    this.isMouseover = false;
};

/* Private methods */

komoo.controls.InfoWindow.prototype.customize_ = function () {
    var that = this;
    google.maps.event.addDomListener(this.object_, 'domready', function (e) {
        var closeBox = that.object_.div_.firstChild;
        google.maps.event.addDomListener(closeBox, 'click', function (e) {
            that.close();
        });
        google.maps.event.addDomListener(closeBox, 'mouseover', function (e) {
            that.isMouseover = true;
        });
        komoo.event.trigger(that, 'domready');
    });
    that.initDomElements_();

};

komoo.controls.InfoWindow.prototype.initDomElements_ = function () {
    var that = this;
    this.title = $('<a>');
    this.body = $('<div>');
    this.content = $('<div>').addClass('map-infowindow-content');
    this.content.append(this.title);
    this.content.append(this.body);
    this.object_.setContent(this.content.get(0));
    var css = {
        background: 'white',
        padding: '10px',
        margin: '0 0 0 15px'
    };
    this.content.css(css);
    this.content.hover(
        function (e) {
            that.isMouseover = true;
        },
        function (e) {
            that.isMouseover = false;
        }
    );
};

