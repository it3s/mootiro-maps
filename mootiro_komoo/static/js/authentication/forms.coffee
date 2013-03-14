define (require) ->
  'use strict'

  reForm = require 'reForm'

  # underscore templates
  signup_tpl = require 'text!templates/widgets/_signup.html'
  signin_tpl = require 'text!templates/widgets/_signin.html'


  # Simple widget for the Sign Up link
  # Used with reForm
  class SignupWidget extends reForm.Widget
    template: signup_tpl
    get: -> ''


  # Simple widget for the Sign In link
  # Used with reForm
  class SigninWidget extends reForm.Widget
    template: signin_tpl
    get: -> ''


  # Form for Login, used internally on the LoginView
  class LoginForm extends reForm.Form
    fields: [
      {
        name: 'email',
        widget: reForm.commonWidgets.TextWidget,
        label: i18n 'Email'
      }
      {
        name: 'password',
        widget: reForm.commonWidgets.PasswordWidget,
        label: i18n 'Password'
      }
      {
        name: 'signup',
        widget: SignupWidget,
      }
    ]
    render: ->
      super
      @$el.find('.auth-register').bind 'click', (evt) =>
        evt.preventDefault()
        @trigger 'register-link:click'
        return false
      this


  #
  # Register Form
  class RegisterForm extends reForm.Form
    fields: [
      {
        name: 'name'
        widget: reForm.commonWidgets.TextWidget
        label: i18n 'Name'
      }
      {
        name: 'email'
        widget: reForm.commonWidgets.TextWidget
        label: i18n 'Email'
      }
      {
        name: 'password'
        widget: reForm.commonWidgets.PasswordWidget
        label: i18n 'Password'
        container_class: 'half-box-left'
      }
      {
        name: 'password_confirm'
        widget: reForm.commonWidgets.PasswordWidget
        label: i18n 'Password Confirmation'
        container_class: 'half-box-right'
      }
      {
        name: 'license'
        widget: reForm.commonWidgets.CheckboxWidget
        args:
          choices: [
            {value: 'agree', title: i18n 'I\'ve read and accept the <a href="http://mootiro.org/terms">License Terms.</a>' }
          ]
      }
      {
        name: 'signin'
        widget: SigninWidget
      }
    ]
    render: ->
      super
      @$el.find('.auth-login').bind 'click', (evt) =>
        evt.preventDefault()
        @trigger 'login-link:click'
        return false
      this


  return {
    LoginForm: LoginForm
    RegisterForm: RegisterForm
  }
