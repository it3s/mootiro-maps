require [
    'jquery',
    'authentication/views'
  ], ($, login_views) ->

    $ ->
      loginView = new  login_views.LoginView {}

      $('#main-content').html loginView.render().el


