(function() {
  var $, HelpCenter,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  $ = jQuery;

  HelpCenter = (function() {

    function HelpCenter(btn_selector, content_ids) {
      this.content_ids = content_ids;
      this.show = __bind(this.show, this);
      alert('constructor');
      this.button = $(btn_selector);
      this.button.on('click', this.show);
    }

    HelpCenter.prototype.show = function() {
      return console.log(this.content_ids);
    };

    return HelpCenter;

  })();

  window.HelpCenter = HelpCenter;

}).call(this);
