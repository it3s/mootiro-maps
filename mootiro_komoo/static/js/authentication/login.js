(function() {

  require(['jquery', 'authentication/views'], function($, login_views) {
    return $(function() {
      var loginView;
      loginView = new login_views.LoginView({});
      return $('#main-content').html(loginView.render().el);
    });
  });

}).call(this);
