define (require) ->

  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  login_tpl = require 'text!templates/authentication/_login.html'
  social_btn_tpl = require 'text!templates/authentication/_social_button.html'

  SocialButton = Backbone.View.extend
    tagName: 'li'
    template: _.template social_btn_tpl

    initialize: ->
      _.bindAll this, 'render'
      @className = @options.provider
      @url = @options.url
      @image_url = @options.image_url
      @msg = @options.message
      @provider = @options.provider


    render: ->
      renderedContent = @template {
        provider: @provider
        url: @url
        image_url: @image_url
        msg: @msg
      }
      @$el.html renderedContent
      @$el.addClass @className
      this

  SocialButtonsList = Backbone.View.extend
    tagName: 'ul'
    id: 'external_providers'

    initialize: ->
      _.bindAll this, 'render', 'toString'
      @buttons = @options.buttons

    render: ->
      buttons = @buttons
      $(@el).html ''

      _.each buttons, (btn) =>
        btnView = new SocialButton btn
        $(@el).append btnView.render().el
      this

  LoginView = Backbone.View.extend
    id: 'login_box'
    tagName: 'section'
    template: _.template login_tpl

    initialize: ->
      _.bindAll this, 'render'

      googleButton =
        provider: 'google',
        url: dutils.urls.resolve 'login_google'
        image_url: '/static/img/login-google.png'
        message: 'Log In with Google'

      facebookButton =
        provider: 'facebook',
        url: dutils.urls.resolve 'login_facebook'
        image_url: '/static/img/login-facebook.png'
        message: 'Log In with Facebook'

      @socialButtonsList = new SocialButtonsList
        buttons: [googleButton, facebookButton]

    render: ->
      socialButtonsView = @socialButtonsList.render().el
      renderedContent = @template {
        login_form: 'LOGIN FORM GOES HERE'
      }
      $(@el).html renderedContent
      @$el.find('.social_buttons').append socialButtonsView
      this

  return {
    LoginView: LoginView
  }






