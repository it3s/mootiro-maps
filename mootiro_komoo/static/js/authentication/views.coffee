define (require) ->
  'use strict'

  _ = require 'underscore'
  Backbone = require 'backbone'

  models = require './models'
  forms = require './forms'
  urls = require 'urls'

  #
  # View for Social Login Buttons (like Google or Facebook)
  # usage:
  #   socialBtn = new SocialButton
  #       provider: 'provider-name'
  #       url: 'provider/login/url/'
  #       msg: 'message on the button, consider i18n'
  #
  class SocialButton extends Backbone.View
    tagName: 'li'

    initialize: ->
      _.bindAll this
      @template = _.template require 'text!templates/authentication/_social_button.html'
      @className = @options.provider
      @url = "#{@options.url}?next=#{@options.next or ''}"
      @msg = @options.message
      @provider = @options.provider

    render: ->
      @$el.html @template
        provider: @provider
        url: @url
        msg: @msg

      @$el.addClass @className
      this


  #
  # Receives a list of objects to be passed to SocialButton constructor and
  # render these on a nice list.
  # usage:
  #     btnsList = new SocialButtonsList
  #         buttons: [
  #           {provider: ..., url: ..., msg: ...}
  #           {provider: ..., url: ..., msg: ...}
  #         ]
  class SocialButtonsList extends Backbone.View
    tagName: 'ul'
    className: 'external_providers'

    initialize: ->
      _.bindAll this, 'render'
      @buttons = @options.buttons

    render: ->
      @$el.html ''

      _.each @buttons, (btn) =>
        btnView = new SocialButton btn
        @$el.append btnView.render().el
      this


  #
  # Public login view, it encapsulates the LoginForm and SocialButtonsList
  # Its intended to be rendered in a ModalBox, but works normally outside it.
  #
  class LoginView extends Backbone.View
    className: 'login_box'
    tagName: 'section'

    initialize: ->
      _.bindAll this
      @template = _.template require 'text!templates/authentication/_login.html'

      next = @options?.next or ''
      @buildButtons(next)

      @model = new models.LoginModel({})

      @form = new forms.LoginForm
        formId: 'form_login'
        model: @model

    render: ->
      @$el.html @template {}
      @$('.social_buttons').append @socialBtnsView.render().el
      @$('.login_form').append @form.render().el
      this

    buildButtons: (next='') ->
      googleButton =
        provider: 'google',
        url: urls.resolve 'login_google'
        next: next
        message: i18n 'Log In with Google'

      facebookButton =
        provider: 'facebook',
        url: urls.resolve 'login_facebook'
        next: next
        message: i18n 'Log In with Facebook'

      @socialBtnsView = new SocialButtonsList
        buttons: [googleButton, facebookButton]
      this

    updateUrls: (next='') ->
      @model.set {next: next}
      @buildButtons(next)
      @render()
      this


  #
  # Logout View to bind the .logout-btn on upper-bar.html
  class LogoutView extends Backbone.View
    initialize: (@options) ->
      _.bindAll this
      @model = new models.LogoutModel {}
      window.logoutmodel = @model

    logout: (next) ->
      @model.doLogout next


  #
  # RegisterView to be used with the LoginBox
  #
  class RegisterView extends Backbone.View
    className: 'register'
    tagName: 'section'

    initialize: ->
      _.bindAll this
      @template = _.template require 'text!templates/authentication/_register.html'
      user = new models.User {}

      @form = new forms.RegisterForm
        formId: 'form_register'
        submit_label: i18n 'Register'
        model: user

    render: ->
      @$el.html @template {}
      @$('.form-wrapper').append @form.render().el
      this


  #
  # Verification view for user email confirmation
  # can receive a `verified` boolean that determines which template
  # it renders.
  # usage:
  #     verifiedView = new VerificationView({verified: true})
  #     notVerifiedView = new VerificationView({verified: false})
  #
  class VerificationView extends Backbone.View
    initialize: ->
      _.bindAll this
      @verified = @options.verified
      if @verified
        @template = _.template require 'text!templates/authentication/_verified.html'
        @loginModel = new models.LoginModel({})
        @loginForm = new forms.LoginForm
          model: @loginModel
      else
        @template = _.template require 'text!templates/authentication/_not_verified.html'

    render: ->
      @$el.html @template {}
      if @verified
        @$('.login-form-box').append @loginForm.render().el
      this


  return {
    LoginView: LoginView
    LogoutView: LogoutView
    RegisterView: RegisterView
    VerificationView: VerificationView
  }
