/**
 * controls.js
 * requires compat.js
 */


if (!window.komoo) komoo = {};
if (!komoo.event) komoo.event = google.maps.event;
if (!komoo.controls) komoo.controls = {};


/** Generic Balloon widget **/

komoo.controls.Balloon = function (opts) {
    var options = opts || {};
    this.width_ = options.width || '250px';
    this.createInfoBox_(options);
    this.setMap(options.map);
    this.customize_();
};

komoo.controls.Balloon.prototype.createInfoBox_ = function (opts) {
    var options = opts || {};
    var infoWindowOptions = {
        pixelOffset: new google.maps.Size(0, -20),
        enableEventPropagation: true,
        closeBoxMargin: '10px',
        boxStyle: {
            cursor: 'pointer',
            background: 'url(/static/img/infowindow-arrow.png) no-repeat 0 10px',  // FIXME: Hardcode is evil
            width: this.width_
        }
    };
    this.setInfoBox(new InfoBox(infoWindowOptions));
};

komoo.controls.Balloon.prototype.setInfoBox = function (infoBox) {
    this.infoBox_ = infoBox;
};

komoo.controls.Balloon.prototype.setMap = function (map) {
    this.map_ = map;
};

komoo.controls.Balloon.prototype.open = function (opts) {
    if (this.map_.mode != komoo.Mode.NAVIGATE) return;
    var options = opts || {};
    var content = options.content;
    if (!content) {
        if (options.features)
            content = this.createClusterContent_(options);
        else
            content = this.createFeatureContent_(options);
    }
    this.setContent(content);
    var position = options.position || feature.getCenter();
    // Translate 5 px to right to fix #2111
    var point = komoo.utils.latLngToPoint(this.map_, position);
    point.x += 5;
    var newPosition = komoo.utils.pointToLatLng(this.map_, point);
    this.infoBox_.setPosition(newPosition);

    this.feature = options.feature || options.features[0];
    this.infoBox_.open(this.map_.googleMap ? this.map_.googleMap : this.map_);
    this.options_ = options;
};

komoo.controls.Balloon.prototype.setContent = function (content) {
    if (typeof content == 'string') content = {title: '', url: '', body: content};
    if (content) {
        if (content.url)
            this.title.html('<a href="' + content.url + '">' +
                    content.title + '</a>');
        else
            this.title.text(content.title);
        this.body.html(content.body);
    }
};

komoo.controls.Balloon.prototype.close = function () {
    this.infoBox_.close();
    if (this.feature && this.feature.isHighlighted()) {
        this.feature.updateIcon();
        this.feature.setHighlight(false);
    }
    this.feature = undefined;
    this.isMouseover = false;
};

/* Private methods */

komoo.controls.Balloon.prototype.customize_ = function () {
    var that = this;
    google.maps.event.addDomListener(this.infoBox_, 'domready', function (e) {
        var div = that.infoBox_.div_;
        google.maps.event.addDomListener(div, 'mousemove', function (e) {
            that.isMouseover = (e.offsetX > 10 || e.toElement != div);
            if (that.isMouseover) {
                e.cancelBubble = true;
                if (e.preventDefault) e.preventDefault();
                if (e.stopPropagation) e.stopPropagation();
                that.map_.closeTooltip();
            }
        });
        google.maps.event.addDomListener(div, 'click', function (e) {
                e.cancelBubble = true;
                if (e.stopPropagation) e.stopPropagation();
        });
        google.maps.event.addDomListener(div, 'mouseout', function (e) {
            that.isMouseover = false;
        });
        var closeBox = div.firstChild;
        google.maps.event.addDomListener(closeBox, 'click', function (e) {
            that.close();
        });
        google.maps.event.addDomListener(closeBox, 'mouseover', function (e) {
            that.isMouseover = true;
        });
        komoo.event.trigger(that, 'domready');
    });
    this.initDomElements_();
};

komoo.controls.Balloon.prototype.createClusterContent_ = function (opts) {
    var options = opts || {};
    var features = options.features || [];
    var msg = ngettext('%s Community', '%s Communities', features.length);
    var title = interpolate(msg, [features.length]);
    var body = '<ul>'
    features.forEach(function (feature, index, orig) {
        body += '<li>' + feature.getProperty('name') + '</li>';
    });
    body += '</ul>';
    return {title: title, url: '',  body: body};
};

komoo.controls.Balloon.prototype.createFeatureContent_ = function (opts) {
    var options = opts || {};
    var title = '';

    var feature = options.feature;
    if (feature) {
        if (feature.getProperty('type') == 'OrganizationBranch') {
            title = feature.getProperty('organization_name') +
                    ' - ' + feature.getProperty('name');
        } else {
            title = feature.getProperty('name');
        }
    }

    return {title: title, url: '', body: ''};
};

komoo.controls.Balloon.prototype.initDomElements_ = function () {
    var that = this;
    this.title = $('<div>');
    this.body = $('<div>');
    this.content = $('<div>').addClass('map-infowindow-content');
    this.content.append(this.title);
    this.content.append(this.body);
    this.infoBox_.setContent(this.content.get(0));
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


/** Generic Balloon Widget using ajax to get content **/

komoo.controls.BalloonAjax = function (opts) {
    komoo.controls.Balloon.call(this, opts);
};

komoo.controls.BalloonAjax.prototype = Object.create(
        komoo.controls.Balloon.prototype);

komoo.controls.BalloonAjax.prototype.createFeatureContent_ = function (opts) {
    var that = this;
    var options = opts || {};
    var feature = options.feature || {};
    if (feature[this.contentViewName_]) return feature[this.contentViewName_];

    var zoom = this.map_.getZoom();
    var featureType = this.map_.featureOptions[feature.getProperty('type')];
    var appName = featureType.appLabel;
    var modelName = featureType.modelName;
    var id = feature.getProperty('id');

    var url = dutils.urls.resolve(this.contentViewName_,
            {zoom: zoom, app_label: appName, model_name: modelName, obj_id: id});
    // Loads via ajax
    $.get(url, function (data, textStatus, jqXHR) {
        feature[that.contentViewName_] = data;
        that.setContent(data);
    });

    return gettext('Loading...');
};


/** Info Window Factory **/

komoo.controls.makeInfoWindow = function (opts) {
    var options = opts || {};
    var infoWindow = new komoo.controls.InfoWindow(options);
    return infoWindow;
};


/** Info Window **/

komoo.controls.InfoWindow = function (opts) {
    var options = opts || {};
    options.width = opts.width || '350px';
    komoo.controls.BalloonAjax.call(this, options);
    this.contentViewName_ = 'info_window';
};

komoo.controls.InfoWindow.prototype = Object.create(
        komoo.controls.BalloonAjax.prototype);


/** Tooltip Window Factory **/

komoo.controls.makeTooltip = function (opts) {
    var options = opts || {};
    var tooltip = new komoo.controls.Tooltip(options);
    return tooltip;
};


/** Tooltip **/

komoo.controls.Tooltip = function (opts) {
    komoo.controls.BalloonAjax.call(this, opts);
    this.contentViewName_ = 'tooltip';
};

komoo.controls.Tooltip.prototype = Object.create(
        komoo.controls.BalloonAjax.prototype);

komoo.controls.Tooltip.prototype.customize_ = function () {
    komoo.controls.BalloonAjax.prototype.customize_.call(this);
    var that = this;
    google.maps.event.addDomListener(this.infoBox_, 'domready', function (e) {
        var div = that.infoBox_.div_;
        google.maps.event.addDomListener(div, 'click', function (e) {
            that.map_.openInfoWindow(that.options_);
        });
        var closeBox = that.infoBox_.div_.firstChild;
        $(closeBox).hide();  // Removes the close button.
    });
};

