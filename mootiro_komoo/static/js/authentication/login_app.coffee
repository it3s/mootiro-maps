require [
    'jquery',
    'authentication/login'
  ], ($, login) ->

    $ -> 
      loginView = new  login.LoginView {}

      $('#main-content').html loginView.render().el 

