(function() {

  require(['jquery', 'sinon', 'widgets/autocomplete'], function($, sinon, AutocompleteView) {
    var $input, ac,
      _this = this;
    ac = null;
    $input = null;
    module('Autocomplete', {
      setup: function() {
        ac = new AutocompleteView('ac_name', '/url/to/request/');
        ac.render();
        return $input = ac.$input;
      },
      teardown: function() {
        ac = null;
        return $input = null;
      }
    });
    test('constructor', function() {
      ac = new AutocompleteView('ac_name', '/url/to/request/');
      ok(ac.$el);
      ok($input);
      equal($input.prop('tagName'), 'INPUT');
      equal($input.attr('type'), 'text');
      equal($input.attr('id'), 'id_ac_name_autocomplete');
      return ok($input.hasClass('ui-autocomplete-input'));
    });
    return test('ajax request on keydown', function() {
      var event;
      sinon.stub($, 'ajax');
      $input.val('test');
      event = $.Event('keydown');
      event.keyCode = 40;
      $input.trigger(event);
      equal($.ajax.getCall(0).args[0].url, '/url/to/request/');
      deepEqual($.ajax.getCall(0).args[0].data, {
        term: 'test'
      });
      return $.ajax.restore();
    });
  });

}).call(this);
