(function() {

  $(function() {
    var cl, csrftoken, form_search, hash, search_field, showPopover, showResults, titles, _ref;
    form_search = $('#search');
    search_field = $('#search-bar');
    csrftoken = getCookie('csrftoken') || window.csrf_token;
    cl = new CanvasLoader('search-canvasloader-container');
    cl.setColor('#3ebac2');
    cl.setShape('rect');
    cl.setDiameter(22);
    cl.setDensity(43);
    cl.setRange(1.2);
    cl.setFPS(22);
    titles = {
      'community': gettext('Communities'),
      'need': gettext('Needs'),
      'organization': gettext('Organizations'),
      'resource': gettext('Resources'),
      'investiment': gettext('Investments'),
      'google': gettext('Google Results')
    };
    showPopover = function() {
      $('#search-results-box').popover('show');
      $('.popover').css('top', parseInt($('.popover').css('top'), 10) - 10);
      return $('.popover').css('left', parseInt($('.popover').css('left'), 10) - 75);
    };
    window.seeOnMap = function(hashlink) {
      var idx, itvl;
      if (window.location.pathname === dutils.urls.resolve('map')) {
        if (hashlink[0] === 'g') {
          idx = parseInt(hashlink.substring(1, hashlink.length), 10);
          itvl = setInterval(function() {
            var desc;
            try {
              desc = JSON.parse(localStorageGet('komoo_search').results['google']).predictions[idx].description;
              editor.goTo(desc);
              return clearInterval(itvl);
            } catch (_error) {}
          }, 500);
        } else {
          $.get('/map/get_geojson_from_hashlink/', {
            hashlink: hashlink
          }, function(data) {
            var geojson;
            geojson = JSON.parse(data.geojson);
            return itvl = setInterval(function() {
              try {
                editor.loadGeoJSON(geojson, true);
                return clearInterval(itvl);
              } catch (_error) {}
            }, 500);
          }, 'json');
        }
        return $('#search-results-box').popover('hide');
      } else {
        return window.location = dutils.urls.resolve('map') + ("#" + hashlink);
      }
    };
    showResults = function(result) {
      var disabled, geojson, google_results, has_results, hashlink, idx, key, obj, result_order, results_count, results_list, val, _i, _len, _ref, _ref2;
      results_list = '';
      results_count = 0;
      has_results = false;
      result_order = ['community', 'organization', 'need', 'resource'];
      for (_i = 0, _len = result_order.length; _i < _len; _i++) {
        key = result_order[_i];
        val = result[key];
        if ((val != null ? val.length : void 0) && key !== 'google') {
          results_list += "<li>\n<div class='search-header " + key + "' >\n    <img src='/static/img/" + key + ".png' >\n    <div class='search-type-header' >\n        " + titles[key] + "\n        <span class='search-results-count'>\n            " + (interpolate(ngettext('%s result', '%s results', val.length), [val.length])) + "\n        </span>\n    </div>\n</div>\n<ul class='search-result-entries'>";
          for (idx in val) {
            obj = val[idx];
            geojson = JSON.parse((_ref = obj != null ? obj.geojson : void 0) != null ? _ref : {});
            disabled = !(geojson != null ? (_ref2 = geojson.features[0]) != null ? _ref2.geometry : void 0 : void 0) ? 'disabled' : '';
            hashlink = key[0] + obj.id;
            results_list += "<li>\n    <a href='" + obj.link + "'> " + obj.name + " </a>\n    <div class=\"right\">\n        <a href=\"/map/#" + hashlink + "\" onclick=\"seeOnMap('" + hashlink + "')\" class=\"" + disabled + "\"><i class=\"icon-see-on-map\"></i></a>\n    </div>\n</li>";
            results_count++;
          }
          results_list += '</ul></li>';
          has_results |= true;
        } else {
          has_results |= false;
        }
      }
      google_results = JSON.parse(result.google).predictions;
      if (google_results != null ? google_results.length : void 0) {
        key = 'google';
        results_list += "<li>\n<div class=\"search-header google\">\n    <img src=\"/static/img/" + key + ".png\" >\n    <div class=\"search-type-header\" >\n        " + titles[key] + "\n        <span class=\"search-results-count\">\n            " + (interpolate(ngettext("%s result", "%s results", google_results.length), [google_results.length])) + "\n        </span>\n    </div>\n</div>\n<ul class=\"search-result-entries\">";
        for (idx in google_results) {
          obj = google_results[idx];
          hashlink = "g" + idx;
          results_list += "<li>\n    <a href=\"#\" > " + obj.description + "</a>\n    <div class=\"right\">\n        <a href=\"#" + hashlink + "\" onclick=seeOnMap('" + hashlink + "')><i class=\"icon-see-on-map\"></i></a>\n    </div>\n</li>";
          results_count++;
        }
        results_list += '</ul></li>';
        has_results |= true;
      } else {
        has_results |= false;
      }
      if (!has_results) {
        results_list = "<div class=\"search-no-results\"> " + (gettext('No results found!')) + "</div>";
      }
      $('#search-results-box').data('popover').options.title = "" + results_count + " Results <span id=\"search-box-close\" >x</span>";
      $('#search-results-box').data('popover').options.content = results_list;
      showPopover();
      return cl.hide();
    };
    form_search.submit(function(evt) {
      var previous_search, search_term;
      evt.preventDefault();
      search_term = search_field.val();
      previous_search = localStorageGet('komoo_search');
      if (!search_term) return;
      cl.show();
      if ((previous_search != null ? previous_search.term : void 0) === search_term) {
        return showResults(previous_search.results);
      } else {
        return $.ajax({
          type: 'POST',
          url: dutils.urls.resolve('komoo_search'),
          data: {
            term: search_term,
            'csrfmiddlewaretoken': csrftoken
          },
          dataType: 'json',
          success: function(data) {
            localStorageSet('komoo_search', {
              term: search_term,
              results: data.result
            });
            return showResults(data.result);
          }
        });
      }
    });
    $('#search-results-box').popover({
      placement: 'bottom',
      selector: search_field,
      trigger: 'manual'
    });
    $('#search-box-close').live('click', function() {
      return $('#search-results-box').popover('hide');
    });
    search_field.val(((_ref = localStorageGet('komoo_search')) != null ? _ref.term : void 0) || '');
    if (window.location.pathname === dutils.urls.resolve('map')) {
      hash = window.location.hash;
      if (hash) return seeOnMap(hash.substring(1, hash.length));
    }
  });

}).call(this);
