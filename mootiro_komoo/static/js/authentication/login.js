(function() {

  require(['jquery', 'underscore', 'backbone', 'text!templates/authentication/_login.html', 'text!templates/authentication/_social_button.html'], function($, _, Backbone, login_template, social_button_template) {
    var LoginView, SocialButton, SocialButtonsList;
    SocialButton = Backbone.View.extend({
      tagName: 'li',
      template: _.template(social_button_template),
      initialize: function() {
        _.bindAll(this, 'render');
        this.className = this.options.provider;
        this.url = this.options.url;
        this.image_url = this.options.image_url;
        this.msg = this.options.message;
        return this.provider = this.options.provider;
      },
      render: function() {
        var renderedContent;
        renderedContent = this.template({
          provider: this.provider,
          url: this.url,
          image_url: this.image_url,
          msg: this.msg
        });
        this.$el.html(renderedContent);
        this.$el.addClass(this.className);
        return this;
      }
    });
    SocialButtonsList = Backbone.View.extend({
      tagName: 'ul',
      id: 'external_providers',
      initialize: function() {
        _.bindAll(this, 'render', 'toString');
        return this.buttons = this.options.buttons;
      },
      render: function() {
        var buttons,
          _this = this;
        buttons = this.buttons;
        $(this.el).html('');
        _.each(buttons, function(btn) {
          var btnView;
          btnView = new SocialButton(btn);
          return $(_this.el).append(btnView.render().el);
        });
        return this;
      }
    });
    LoginView = Backbone.View.extend({
      id: 'login_box',
      tagName: 'section',
      template: _.template(login_template),
      initialize: function() {
        var facebookButton, googleButton;
        _.bindAll(this, 'render');
        googleButton = {
          provider: 'google',
          url: dutils.urls.resolve('login_google'),
          image_url: '/static/img/login-google.png',
          message: 'Log In with Google'
        };
        facebookButton = {
          provider: 'facebook',
          url: dutils.urls.resolve('login_facebook'),
          image_url: '/static/img/login-facebook.png',
          message: 'Log In with Facebook'
        };
        return this.socialButtonsList = new SocialButtonsList({
          buttons: [googleButton, facebookButton]
        });
      },
      render: function() {
        var renderedContent, socialButtonsView;
        socialButtonsView = this.socialButtonsList.render().el;
        renderedContent = this.template({
          login_form: 'LOGIN FORM GOES HERE'
        });
        $(this.el).html(renderedContent);
        this.$el.find('.social_buttons').append(socialButtonsView);
        return this;
      }
    });
    $(function() {
      var loginView;
      loginView = new LoginView({});
      return $('#main-content').html(loginView.render().el);
    });
    return {
      LoginView: LoginView
    };
  });

}).call(this);
