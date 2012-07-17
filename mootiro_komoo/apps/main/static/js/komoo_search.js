(function() {

  $(function() {
    var cl, csrftoken, form_search, geo_object, intvl, search_field, showPopover, showResults, titles, _ref;
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
    window.seeOnMap = function(type, geojson) {
      if (window.location.pathname === dutils.urls.resolve('map')) {
        if (type === 'google') {
          editor.goTo(geojson);
        } else {
          editor.loadGeoJSON(geojson, true);
        }
        $('#search-results-box').popover('hide');
      } else {
        localStorageSet('komoo_seeOnMap', {
          type: type,
          geo: geojson
        });
        window.location.pathname = dutils.urls.resolve('map');
      }
      return false;
    };
    showResults = function(result) {
      var google_results, has_results, idx, key, obj, result_order, results_count, results_list, val, _i, _j, _len, _len2;
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
            results_list += "<li>\n    <a href='" + obj.link + "'> " + obj.name + " </a>\n    <div class=\"right\">\n        <a href=\"#\" onclick=\"seeOnMap('" + key + "', JSON.parse(localStorageGet('komoo_search').results['" + key + "'][" + idx + "].geojson));return false;\"><i class=\"icon-see-on-map\"></i></a>\n    </div>\n</li>";
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
        for (_j = 0, _len2 = google_results.length; _j < _len2; _j++) {
          obj = google_results[_j];
          results_list += "<li>\n    <a href=\"#\" > " + obj.description + "</a>\n    <div class=\"right\">\n        <a href=\"#\" onclick=\"seeOnMap('google', '" + obj.description + "');return false;\"><i class=\"icon-see-on-map\"></i></a>\n    </div>\n</li>";
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
      cl.show();
      search_term = search_field.val();
      previous_search = localStorageGet('komoo_search');
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
    if (window.location.pathname === dutils.urls.resolve('map') && localStorageGet('komoo_seeOnMap')) {
      geo_object = localStorageGet('komoo_seeOnMap');
      intvl = setInterval(function() {
        try {
          if (geo_object.type === 'google') {
            editor.goTo(geo_object.geo);
          } else {
            editor.loadGeoJSON(geo_object.geo, true);
          }
          return clearInterval(intvl);
        } catch (_error) {}
      }, 50);
      return localStorageRemove('komoo_seeOnMap');
    }
  });

}).call(this);
