require [
    'jquery', 
    'underscore', 
    'backbone', 
    'text!templates/authentication/_login.html'
  ], ($, _, Backbone, tplt) ->

    loginData = Backbone.Model.extend {}

    loginForm = Backbone.View.extend {}

    socialButton = Backbone.View.extend {}

    loginBox = Backbone.View.extend {}

    console.log tplt


