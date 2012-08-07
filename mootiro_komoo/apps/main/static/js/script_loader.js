(function() {
  var ScriptLoader,
    __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  ScriptLoader = (function() {

    function ScriptLoader() {
      this.waitting = {};
      this.loading = [];
      this.loaded = [];
    }

    ScriptLoader.prototype.load = function(name, url, callback) {
      var _this = this;
      if (__indexOf.call(this.loaded, name) >= 0) {
        if (typeof console !== "undefined" && console !== null) {
          console.log("" + name + " (" + url + ") already loaded.");
        }
        return typeof callback === "function" ? callback(name) : void 0;
      } else if (__indexOf.call(this.loading, name) >= 0) {
        if (typeof console !== "undefined" && console !== null) {
          console.log("" + name + " (" + url + ") is been loaded.");
        }
        return this.waitFor(name, callback);
      } else {
        this.loading.push(name);
        return $.ajax({
          url: url,
          dataType: "script",
          cache: true
        }).done(function(script, status) {
          var cb, _ref, _results;
          _this.loaded.push(name);
          if (typeof console !== "undefined" && console !== null) {
            console.log("" + name + " (" + url + ") loaded.");
          }
          if (typeof callback === "function") callback(name);
          _results = [];
          while (cb = (_ref = _this.waitting[name]) != null ? _ref.pop() : void 0) {
            if (typeof console !== "undefined" && console !== null) {
              console.log("calling callback for " + name);
            }
            _results.push(cb(name));
          }
          return _results;
        }).fail(function(jqxhr, settings, exception) {
          return console.log(exception);
        });
      }
    };

    ScriptLoader.prototype.waitFor = function(name, callback) {
      var _base;
      if ((_base = this.waitting)[name] == null) _base[name] = [];
      this.waitting[name].push(callback);
      if (__indexOf.call(this.loaded, name) >= 0) {
        return typeof callback === "function" ? callback(name) : void 0;
      }
    };

    return ScriptLoader;

  })();

  if (window.scriptLoader == null) window.scriptLoader = new ScriptLoader();

}).call(this);
