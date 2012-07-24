(function() {
  var CleanMapType, _base;

  if (window.komoo == null) window.komoo = {};

  if ((_base = window.komoo).event == null) _base.event = google.maps.event;

  CleanMapType = (function() {

    CleanMapType.prototype.id = 'clean';

    function CleanMapType() {
      this.mapType = new google.maps.StyledMapType([
        {
          featureType: 'poi',
          elementType: 'all',
          stylers: [
            {
              visibility: "off"
            }
          ]
        }, {
          featureType: 'road',
          elementType: 'all',
          stylers: [
            {
              lightness: 70
            }
          ]
        }, {
          featureType: 'transit',
          elementType: 'all',
          stylers: [
            {
              lightness: 50
            }
          ]
        }, {
          featureType: 'water',
          elementType: 'all',
          stylers: [
            {
              lightness: 50
            }
          ]
        }, {
          featureType: 'administrative',
          elementType: 'labels',
          stylers: [
            {
              lightness: 30
            }
          ]
        }
      ], {
        name: gettext('Clean')
      });
    }

    CleanMapType.prototype.setMap = function(map) {
      this.map = map;
      return this.map.googleMap.mapTypes.set(this.id, this.mapType);
    };

    return CleanMapType;

  })();

  window.komoo.maptypes = {
    CleanMapType: CleanMapType,
    makeCleanMapType: function() {
      return new CleanMapType();
    }
  };

}).call(this);
