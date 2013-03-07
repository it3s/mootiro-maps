(function() {

  $(function() {
    var cl, csrftoken, doSearch, form_search, hash, hidePopover, search_field, showPopover, showResults, titles;
    form_search = $('#search form');
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
      'user': gettext('User'),
      'project': gettext('Project')
    };
    showPopover = function() {
      window.is_search_results_open = true;
      return $('#search-results-box').popover('show');
    };
    hidePopover = function() {
      window.is_search_results_open = false;
      return $('#search-results-box').popover('hide');
    };
    window.seeOnMap = function(hashlink) {
      var itvl;
      if (hashlink === '#map-panel-add') return;
      if (window.location.pathname === dutils.urls.resolve('map')) {
        if (hashlink[0] === 'g') {
          itvl = setInterval(function() {
            var desc;
            try {
              desc = hashlink.substring(1, hashlink.length);
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
        return hidePopover();
      } else {
        return window.location = dutils.urls.resolve('map') + ("#" + hashlink);
      }
    };
    showResults = function(result, search_term) {
      var google_results, has_results, idx, obj, results_count, results_list, _ref, _ref2, _ref3, _ref4;
      if (search_term == null) search_term = "";
      results_list = '';
      results_count = 0;
      has_results = false;
      if (result != null ? (_ref = result.komoo) != null ? _ref.length : void 0 : void 0) {
        results_list += "<li>\n<ul class='search-result-entries'>";
        _ref2 = result.komoo;
        for (idx in _ref2) {
          obj = _ref2[idx];
          results_list += "<li class=\"search-result\">\n    <img class=\"model-icon\" alt=\"icon " + obj.model + "\" title=\"icon " + obj.model + "\" src=\"/static/img/" + obj.model + ".png\">\n    <a class=\"search-result-title\" href='" + obj.link + "'> " + obj.name + " </a>\n    <div class=\"right\">\n        <a href=\"/map/#" + obj.hashlink + "\" hashlink=\"" + obj.hashlink + "\" class=\"search-map-link " + obj.disabled + "\" title=\"ver no mapa\"><i class=\"icon-see-on-map\"></i></a>\n    </div>\n</li>";
          results_count++;
        }
        results_list += "<li class='search-results-see-all'><a href='/search/all?term=" + search_term + "'> ver todos &raquo;</a> </li></ul></li>";
        has_results |= true;
      } else {
        has_results |= false;
      }
      if (!has_results) {
        results_list = "<div class=\"search-no-results\"> " + (gettext('No results found on our database!')) + "</div>";
      }
      google_results = JSON.parse(result.google);
      if ((_ref3 = google_results.predictions) != null ? _ref3.length : void 0) {
        results_list += "<li>\n<ul class='search-result-entries google'>\n<li class=\"search-header google\">\n  <img class=\"model-icon\" alt=\"icon google\" title=\"icon google\" src=\"/static/img/google.png\">\n  <span class=\"search-type-header\">Resultados do Google:</span>\n</li>";
        _ref4 = google_results.predictions;
        for (idx in _ref4) {
          obj = _ref4[idx];
          results_list += "<li class=\"search-result\">\n    <!--img class=\"model-icon\" alt=\"icon google\" title=\"icon google\" src=\"/static/img/google.png\"-->\n    <a class=\"search-result-title\" href='#'> " + obj.description + " </a>\n    <div class=\"right\">\n        <a href=\"/map/#g" + obj.description + "\" hashlink=\"g" + obj.description + "\" class=\"search-map-link\" title=\"ver no mapa\"><i class=\"icon-see-on-map\"></i></a>\n    </div>\n</li>";
        }
        results_list += "</ul></li>";
      }
      $('#search-results-box').data('popover').options.content = results_list;
      showPopover();
      return cl.hide();
    };
    doSearch = function() {
      var search_term;
      window.komoo_search_timeout_fn = null;
      search_term = search_field.val();
      if (!search_term) return;
      cl.show();
      return $.ajax({
        type: 'POST',
        url: dutils.urls.resolve('komoo_search'),
        data: {
          term: search_term,
          'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function(data) {
          return showResults(data.result, search_term);
        }
      });
    };
    form_search.submit(function(evt) {
      evt.preventDefault();
      if (window.komoo_search_timeout_fn) {
        clearTimeout(window.komoo_search_timeout_fn);
      }
      return doSearch();
    });
    window.komoo_search_timeout_fn = null;
    search_field.bind('keydown', function() {
      if (search_field.val().length > 2) {
        if (window.komoo_search_timeout_fn) {
          clearTimeout(window.komoo_search_timeout_fn);
        }
        return window.komoo_search_timeout_fn = setTimeout(doSearch, 500);
      }
    });
    $('#search-results-box').popover({
      placement: 'bottom',
      selector: search_field,
      trigger: 'manual',
      animation: true
    });
    $('body').live('click', function(evt) {
      var result_box;
      result_box = $('.popover');
      if (window.is_search_results_open && result_box.has(evt.target).length === 0) {
        return hidePopover();
      }
    });
    $('.search-map-link').live('click', function(evt) {
      var _this;
      evt.preventDefault();
      _this = $(this);
      if (!_this.is('.disabled')) {
        return seeOnMap(_this.attr('hashlink'));
      } else {
        return false;
      }
    });
    if (window.location.pathname === dutils.urls.resolve('map')) {
      hash = window.location.hash;
      if (hash) return seeOnMap(hash.substring(1, hash.length));
    }
  });

}).call(this);
