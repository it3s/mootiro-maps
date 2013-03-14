(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define(function(require) {
    'use strict';
    var LoginForm, RegisterForm, SigninWidget, SignupWidget, reForm, signin_tpl, signup_tpl;
    reForm = require('reForm');
    signup_tpl = require('text!templates/widgets/_signup.html');
    signin_tpl = require('text!templates/widgets/_signin.html');
    SignupWidget = (function(_super) {

      __extends(SignupWidget, _super);

      function SignupWidget() {
        SignupWidget.__super__.constructor.apply(this, arguments);
      }

      SignupWidget.prototype.template = signup_tpl;

      SignupWidget.prototype.get = function() {
        return '';
      };

      return SignupWidget;

    })(reForm.Widget);
    SigninWidget = (function(_super) {

      __extends(SigninWidget, _super);

      function SigninWidget() {
        SigninWidget.__super__.constructor.apply(this, arguments);
      }

      SigninWidget.prototype.template = signin_tpl;

      SigninWidget.prototype.get = function() {
        return '';
      };

      return SigninWidget;

    })(reForm.Widget);
    LoginForm = (function(_super) {

      __extends(LoginForm, _super);

      function LoginForm() {
        LoginForm.__super__.constructor.apply(this, arguments);
      }

      LoginForm.prototype.fields = [
        {
          name: 'email',
          widget: reForm.commonWidgets.TextWidget,
          label: i18n('Email')
        }, {
          name: 'password',
          widget: reForm.commonWidgets.PasswordWidget,
          label: i18n('Password')
        }, {
          name: 'signup',
          widget: SignupWidget
        }
      ];

      LoginForm.prototype.render = function() {
        var _this = this;
        LoginForm.__super__.render.apply(this, arguments);
        this.$el.find('.auth-register').bind('click', function(evt) {
          evt.preventDefault();
          _this.trigger('register-link:click');
          return false;
        });
        return this;
      };

      return LoginForm;

    })(reForm.Form);
    RegisterForm = (function(_super) {

      __extends(RegisterForm, _super);

      function RegisterForm() {
        RegisterForm.__super__.constructor.apply(this, arguments);
      }

      RegisterForm.prototype.fields = [
        {
          name: 'name',
          widget: reForm.commonWidgets.TextWidget,
          label: i18n('Name')
        }, {
          name: 'email',
          widget: reForm.commonWidgets.TextWidget,
          label: i18n('Email')
        }, {
          name: 'password',
          widget: reForm.commonWidgets.PasswordWidget,
          label: i18n('Password'),
          container_class: 'half-box-left'
        }, {
          name: 'password_confirm',
          widget: reForm.commonWidgets.PasswordWidget,
          label: i18n('Password Confirmation'),
          container_class: 'half-box-right'
        }, {
          name: 'license',
          widget: reForm.commonWidgets.CheckboxWidget,
          args: {
            choices: [
              {
                value: 'agree',
                title: i18n('I\'ve read and accept the <a href="http://mootiro.org/terms">License Terms.</a>')
              }
            ]
          }
        }, {
          name: 'signin',
          widget: SigninWidget
        }
      ];

      RegisterForm.prototype.render = function() {
        var _this = this;
        RegisterForm.__super__.render.apply(this, arguments);
        this.$el.find('.auth-login').bind('click', function(evt) {
          evt.preventDefault();
          _this.trigger('login-link:click');
          return false;
        });
        return this;
      };

      return RegisterForm;

    })(reForm.Form);
    return {
      LoginForm: LoginForm,
      RegisterForm: RegisterForm
    };
  });

}).call(this);
