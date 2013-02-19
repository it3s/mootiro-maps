(function() {
  var $, HelpCenter,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  $ = jQuery;

  HelpCenter = (function() {

    function HelpCenter(btn_selector, content_ids) {
      this.content_ids = content_ids;
      this.show = __bind(this.show, this);
      this.modal_setup = __bind(this.modal_setup, this);
      this.button = $(btn_selector);
      this.button.on('click', this.show);
      this.modal_setup();
    }

    HelpCenter.prototype.modal_setup = function() {
      var html;
      html = "            <div id='help_center' class='modal hide fade'>                <div class='modal-header'>                    <button type='button' class='close' data-dismiss='modal'>×</button>                    <h3>Modal header</h3>                </div>                <div class='modal-body'>                    <p>One fine body…</p>                </div>            </div>        ";
      this.$modal = $(html).modal({
        show: false
      });
      return $('body').append(this.$modal);
    };

    HelpCenter.prototype.show = function() {
      console.log(this.content_ids);
      console.log(this.contents);
      return this.$modal.modal('show');
    };

    HelpCenter.prototype.contents = {
      "organization:what_is": {
        "type": "question",
        "data": {
          "question": "What is an organization?",
          "answer": "An organization is ... (markdown string)"
        }
      },
      "organization:page_tour": {
        "type": "tour",
        "data": {
          "slides": [
            {
              "title": "Description",
              "body": "This is the organization description",
              "target": "#organization-description"
            }, {
              "title": "Contact information",
              "body": "Here you'll find contact",
              "target": "#organization-contact"
            }
          ]
        }
      }
    };

    return HelpCenter;

  })();

  window.HelpCenter = HelpCenter;

}).call(this);
