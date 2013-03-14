(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define(function(require) {
    'use strict';
    var $, Backbone, LoginModel, LogoutModel, User, urls, _;
    $ = require('jquery');
    _ = require('underscore');
    Backbone = require('backbone');
    urls = require('urls');
    LoginModel = (function(_super) {

      __extends(LoginModel, _super);

      function LoginModel() {
        LoginModel.__super__.constructor.apply(this, arguments);
      }

      LoginModel.prototype.urlRoot = urls.resolve('login_api');

      return LoginModel;

    })(Backbone.Model);
    LogoutModel = (function(_super) {

      __extends(LogoutModel, _super);

      function LogoutModel() {
        LogoutModel.__super__.constructor.apply(this, arguments);
      }

      LogoutModel.prototype.urlRoot = urls.resolve('logout_api');

      LogoutModel.prototype.initialize = function() {
        return _.bindAll(this);
      };

      LogoutModel.prototype.doLogout = function(next) {
        var _this = this;
        this.set({
          next: next
        });
        return Backbone.sync('read', this, {
          data: {
            next: next
          },
          success: function(model, resp, xhr) {
            if (resp.redirect) {
              if (window.location.pathname === resp.redirect) {
                return window.location.reload();
              } else {
                return window.location = resp.redirect;
              }
            }
          }
        });
      };

      return LogoutModel;

    })(Backbone.Model);
    User = (function(_super) {

      __extends(User, _super);

      function User() {
        User.__super__.constructor.apply(this, arguments);
      }

      User.prototype.urlRoot = urls.resolve('user_api');

      return User;

    })(Backbone.Model);
    return {
      LoginModel: LoginModel,
      LogoutModel: LogoutModel,
      User: User
    };
  });

}).call(this);
