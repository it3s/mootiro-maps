(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define(function(require) {
    'use strict';
    var $, Backbone, LoginApp, ModalBox, app, reForm, views, _;
    $ = require('jquery');
    _ = require('underscore');
    Backbone = require('backbone');
    app = require('app');
    reForm = require('reForm');
    views = require('./views');
    ModalBox = require('widgets/modal');
    LoginApp = (function(_super) {

      __extends(LoginApp, _super);

      function LoginApp() {
        LoginApp.__super__.constructor.apply(this, arguments);
      }

      LoginApp.prototype.routes = {
        'login(/)': 'login',
        'register(/)': 'register',
        'not-verified(/)': 'not_verified',
        'verified(/)': 'verified'
      };

      LoginApp.prototype.initialize = function() {
        _.bindAll(this);
        return this.bindExternalEvents();
      };

      LoginApp.prototype.initializeLogin = function() {
        this.loginView = new views.LoginView({});
        this.loginView.form.on('register-link:click', this.registerLinkCB);
        return this.loginBox = new ModalBox({
          title: i18n('Login'),
          content: this.loginView.render().el,
          modal_id: 'login-modal-box'
        });
      };

      LoginApp.prototype.initializeLogout = function() {
        return this.logoutView = new views.LogoutView({});
      };

      LoginApp.prototype.initializeRegister = function() {
        this.registerView = new views.RegisterView({});
        this.registerView.form.on('success', this.registerFormOnSuccessCB);
        this.registerView.form.on('login-link:click', this.loginLinkCB);
        return this.registerBox = new ModalBox({
          title: i18n('Register'),
          width: '450px',
          content: this.registerView.render().el,
          modal_id: 'register-modal-box'
        });
      };

      LoginApp.prototype.initializeVerification = function() {
        this.notVerifiedView = new views.VerificationView({
          verified: false
        });
        this.verifiedView = new views.VerificationView({
          verified: true
        });
        this.verifiedView.loginForm.on('register-link:click', this.registerLinkCB);
        this.notVerifiedBox = new ModalBox({
          title: i18n('Verification'),
          content: this.notVerifiedView.render().el,
          modal_id: 'verification-modal-box'
        });
        return this.verifiedBox = new ModalBox({
          title: i18n('Verification'),
          content: this.verifiedView.render().el,
          modal_id: 'verification-modal-box'
        });
      };

      LoginApp.prototype.bindExternalEvents = function() {
        app.on('login', this._loginRequired);
        return app.on('logout', this.logout);
      };

      LoginApp.prototype.registerLinkCB = function() {
        return this.register();
      };

      LoginApp.prototype.loginLinkCB = function() {
        return this.login();
      };

      LoginApp.prototype.registerFormOnSuccessCB = function() {
        return this.not_verified();
      };

      LoginApp.prototype._loginRequired = function(next) {
        if (!(typeof KomooNS !== "undefined" && KomooNS !== null ? KomooNS.isAuthenticated : void 0)) {
          if (!(this.loginBox != null)) this.initializeLogin();
          if (next) this.loginView.updateUrls(next);
          return this.login();
        }
      };

      LoginApp.prototype.login = function() {
        this.closeModals();
        if (!(typeof KomooNS !== "undefined" && KomooNS !== null ? KomooNS.isAuthenticated : void 0)) {
          if (!(this.loginBox != null)) this.initializeLogin();
          return this.loginBox.open();
        }
      };

      LoginApp.prototype.logout = function() {
        if (!this.logoutView) this.initializeLogout();
        if (typeof console !== "undefined" && console !== null) {
          console.log('LOGOUT');
        }
        return this.logoutView.logout();
      };

      LoginApp.prototype.register = function() {
        this.closeModals();
        if (!(typeof KomooNS !== "undefined" && KomooNS !== null ? KomooNS.isAuthenticated : void 0)) {
          if (!(this.registerBox != null)) this.initializeRegister();
          return this.registerBox.open();
        }
      };

      LoginApp.prototype.not_verified = function() {
        this.closeModals();
        if (!(this.notVerifiedBox != null)) this.initializeVerification();
        return this.notVerifiedBox.open();
      };

      LoginApp.prototype.verified = function() {
        this.closeModals();
        if (!(this.verifiedBox != null)) this.initializeVerification();
        return this.verifiedBox.open();
      };

      LoginApp.prototype.closeModals = function() {
        var modal, _i, _len, _ref, _results;
        _ref = [this.loginBox, this.registerBox, this.verifiedBox, this.notVerifiedBox];
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          modal = _ref[_i];
          _results.push(modal != null ? modal.close() : void 0);
        }
        return _results;
      };

      return LoginApp;

    })(Backbone.Router);
    return LoginApp;
  });

}).call(this);
