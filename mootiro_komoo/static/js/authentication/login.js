(function() {

  require(['jquery', 'underscore', 'backbone', 'text!templates/authentication/_login.html'], function($, _, Backbone, tplt) {
    var loginBox, loginData, loginForm, socialButton;
    loginData = Backbone.Model.extend({});
    loginForm = Backbone.View.extend({});
    socialButton = Backbone.View.extend({});
    loginBox = Backbone.View.extend({});
    return console.log(tplt);
  });

}).call(this);
