(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define(function(require) {
    'use strict';
    var Backbone, LoginView, LogoutView, RegisterView, SocialButton, SocialButtonsList, VerificationView, forms, models, urls, _;
    _ = require('underscore');
    Backbone = require('backbone');
    models = require('./models');
    forms = require('./forms');
    urls = require('urls');
    SocialButton = (function(_super) {

      __extends(SocialButton, _super);

      function SocialButton() {
        SocialButton.__super__.constructor.apply(this, arguments);
      }

      SocialButton.prototype.tagName = 'li';

      SocialButton.prototype.initialize = function() {
        _.bindAll(this);
        this.template = _.template(require('text!templates/authentication/_social_button.html'));
        this.className = this.options.provider;
        this.url = "" + this.options.url + "?next=" + (this.options.next || '');
        this.msg = this.options.message;
        return this.provider = this.options.provider;
      };

      SocialButton.prototype.render = function() {
        this.$el.html(this.template({
          provider: this.provider,
          url: this.url,
          msg: this.msg
        }));
        this.$el.addClass(this.className);
        return this;
      };

      return SocialButton;

    })(Backbone.View);
    SocialButtonsList = (function(_super) {

      __extends(SocialButtonsList, _super);

      function SocialButtonsList() {
        SocialButtonsList.__super__.constructor.apply(this, arguments);
      }

      SocialButtonsList.prototype.tagName = 'ul';

      SocialButtonsList.prototype.className = 'external_providers';

      SocialButtonsList.prototype.initialize = function() {
        _.bindAll(this, 'render');
        return this.buttons = this.options.buttons;
      };

      SocialButtonsList.prototype.render = function() {
        var _this = this;
        this.$el.html('');
        _.each(this.buttons, function(btn) {
          var btnView;
          btnView = new SocialButton(btn);
          return _this.$el.append(btnView.render().el);
        });
        return this;
      };

      return SocialButtonsList;

    })(Backbone.View);
    LoginView = (function(_super) {

      __extends(LoginView, _super);

      function LoginView() {
        LoginView.__super__.constructor.apply(this, arguments);
      }

      LoginView.prototype.className = 'login_box';

      LoginView.prototype.tagName = 'section';

      LoginView.prototype.initialize = function() {
        var next, _ref;
        _.bindAll(this);
        this.template = _.template(require('text!templates/authentication/_login.html'));
        next = ((_ref = this.options) != null ? _ref.next : void 0) || '';
        this.buildButtons(next);
        this.model = new models.LoginModel({});
        return this.form = new forms.LoginForm({
          formId: 'form_login',
          model: this.model
        });
      };

      LoginView.prototype.render = function() {
        this.$el.html(this.template({}));
        this.$('.social_buttons').append(this.socialBtnsView.render().el);
        this.$('.login_form').append(this.form.render().el);
        return this;
      };

      LoginView.prototype.buildButtons = function(next) {
        var facebookButton, googleButton;
        if (next == null) next = '';
        googleButton = {
          provider: 'google',
          url: urls.resolve('login_google'),
          next: next,
          message: i18n('Log In with Google')
        };
        facebookButton = {
          provider: 'facebook',
          url: urls.resolve('login_facebook'),
          next: next,
          message: i18n('Log In with Facebook')
        };
        this.socialBtnsView = new SocialButtonsList({
          buttons: [googleButton, facebookButton]
        });
        return this;
      };

      LoginView.prototype.updateUrls = function(next) {
        if (next == null) next = '';
        this.model.set({
          next: next
        });
        this.buildButtons(next);
        this.render();
        return this;
      };

      return LoginView;

    })(Backbone.View);
    LogoutView = (function(_super) {

      __extends(LogoutView, _super);

      function LogoutView() {
        LogoutView.__super__.constructor.apply(this, arguments);
      }

      LogoutView.prototype.initialize = function(options) {
        this.options = options;
        _.bindAll(this);
        this.model = new models.LogoutModel({});
        return window.logoutmodel = this.model;
      };

      LogoutView.prototype.logout = function(next) {
        return this.model.doLogout(next);
      };

      return LogoutView;

    })(Backbone.View);
    RegisterView = (function(_super) {

      __extends(RegisterView, _super);

      function RegisterView() {
        RegisterView.__super__.constructor.apply(this, arguments);
      }

      RegisterView.prototype.className = 'register';

      RegisterView.prototype.tagName = 'section';

      RegisterView.prototype.initialize = function() {
        var user;
        _.bindAll(this);
        this.template = _.template(require('text!templates/authentication/_register.html'));
        user = new models.User({});
        return this.form = new forms.RegisterForm({
          formId: 'form_register',
          submit_label: i18n('Register'),
          model: user
        });
      };

      RegisterView.prototype.render = function() {
        this.$el.html(this.template({}));
        this.$('.form-wrapper').append(this.form.render().el);
        return this;
      };

      return RegisterView;

    })(Backbone.View);
    VerificationView = (function(_super) {

      __extends(VerificationView, _super);

      function VerificationView() {
        VerificationView.__super__.constructor.apply(this, arguments);
      }

      VerificationView.prototype.initialize = function() {
        _.bindAll(this);
        this.verified = this.options.verified;
        if (this.verified) {
          this.template = _.template(require('text!templates/authentication/_verified.html'));
          this.loginModel = new models.LoginModel({});
          return this.loginForm = new forms.LoginForm({
            model: this.loginModel
          });
        } else {
          return this.template = _.template(require('text!templates/authentication/_not_verified.html'));
        }
      };

      VerificationView.prototype.render = function() {
        this.$el.html(this.template({}));
        if (this.verified) {
          this.$('.login-form-box').append(this.loginForm.render().el);
        }
        return this;
      };

      return VerificationView;

    })(Backbone.View);
    return {
      LoginView: LoginView,
      LogoutView: LogoutView,
      RegisterView: RegisterView,
      VerificationView: VerificationView
    };
  });

}).call(this);
