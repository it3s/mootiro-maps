(function() {

  require(['jquery', 'sinon', 'project/model', 'project/box', 'project/add_dialog'], function($, sinon, Model, BoxView, AddDialogView) {
    var _this = this;
    if (window.gettext == null) {
      window.gettext = function(s) {
        return s;
      };
    }
    module('Project', {
      setup: function() {},
      teardown: function() {}
    });
    test('BoxView constructor', function() {
      var $li, $ul, p;
      p = new BoxView({
        collection: new Model.Projects().reset([
          {
            name: 'first project'
          }, {
            name: 'second project'
          }, {
            name: 'last project'
          }
        ])
      });
      p.render();
      ok(p.$el);
      notEqual(p.$('.add').text(), '', 'Add button should have text');
      $ul = p.$('.list');
      $li = $ul.find('li');
      equal($li.eq(0).text(), 'first project', 'Should add project to list');
      equal($li.eq(1).text(), 'second project', 'Should add project to list');
      return equal($li.eq(2).text(), 'last project', 'Should add project to list');
    });
    test('BoxView Open dialog on button click', function() {
      var p, spy;
      p = new BoxView().render();
      spy = sinon.spy(p, 'openAddDialog');
      p.$('.add').click();
      return ok(spy.calledOnce);
    });
    test('AddDialogView constructor', function() {
      var d;
      d = new AddDialogView().render();
      ok(d.autocomplete, 'Should have autocoplete widget');
      return ok(!d.$('.dialog').is(':visible', 'Should init closed'));
    });
    return test('AddDialogView open', function() {
      var d;
      d = new AddDialogView().render();
      d.open();
      return ok(d.$('.dialog').is(':visible', 'Should be visible when opened'));
    });
  });

}).call(this);
