define (require) ->
  'use strict'

  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  urls = require 'urls'

  class LoginModel extends Backbone.Model
    urlRoot: urls.resolve 'login_api'

  class LogoutModel extends Backbone.Model
    urlRoot: urls.resolve 'logout_api'
    initialize: ->
      _.bindAll this
    doLogout: (next) ->
      @set {next: next}
      Backbone.sync 'read', this,
        data:
          next: next
        success: (model, resp, xhr) =>
          if resp.redirect
            if window.location.pathname is resp.redirect
              window.location.reload()
            else
              window.location = resp.redirect

  class User extends Backbone.Model
    urlRoot: urls.resolve 'user_api'

  return {
    LoginModel: LoginModel
    LogoutModel: LogoutModel
    User: User
  }
