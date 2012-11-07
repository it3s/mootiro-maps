(function() {

  require(['jquery', 'authentication/login'], function($, login) {
    return $(function() {
      var loginView;
      loginView = new login.LoginView({});
      return $('#main-content').html(loginView.render().el);
    });
  });

}).call(this);
