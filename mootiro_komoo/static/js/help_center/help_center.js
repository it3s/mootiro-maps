(function() {
  var $, HelpCenter,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  $ = jQuery;

  HelpCenter = (function() {

    function HelpCenter(btn_selector, content_ids) {
      this.show = __bind(this.show, this);
      this.modal_setup = __bind(this.modal_setup, this);
      var cid;
      this.button = $(btn_selector);
      this.button.on('click', this.show);
      this.contents = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = content_ids.length; _i < _len; _i++) {
          cid = content_ids[_i];
          _results.push(this.contents_config[cid]);
        }
        return _results;
      }).call(this);
      this.modal_setup();
    }

    HelpCenter.prototype.question_tpl = "        <article>            <h3><%= question %></h3>            <p><%= answer %></p>        </article>        ";

    HelpCenter.prototype.tutorial_tpl = "        tourtorial        ";

    HelpCenter.prototype.modal_tpl = "        <div id='help_center' class='modal hide fade'>            <div class='modal-header'>                <button type='button' class='close' data-dismiss='modal'>×</button>                <h2>Modal header</h2>            </div>            <section class='modal-body'>                <ul>                    <% for (var i = 0; i < contents.length; i++) { %>                        <li class='help_center_<%= contents[i].type %>'>                            <!--!--------- QUESTION ----------->                            <% if (contents[i].type == 'question') { %>                            <article>                                <h3><%= contents[i].title %></h3>                                <p><%= contents[i].body %></p>                            </article>                            <% } %>                                                        <!--!--------- TUTORIAL ----------->                            <% if (contents[i].type == 'tutorial') { %>                            <article>                                <h3><%= contents[i].title %></h3>                                <p><%= contents[i].body %></p>                            </article>                            <div class='tutorial'>                                <% for (var j = 0; j < contents[i].slides.length; j++) { %>                                <div data-target='<%= contents[i].slides[j].target %>' data-location='<%= contents[i].slides[j].location %>' data-arrow='<%= contents[i].slides[j].arrow %>'>                                    <h3><%= contents[i].slides[j].title %></h3>                                    <p><%= contents[i].slides[j].body %></p>                                </div>                                <% } %>                            </div>                            <!--!------------------------------>                            <% } %>                        </li>                    <% } %>                </ul>            </section>        </div>        ";

    HelpCenter.prototype.modal_setup = function() {
      var html, modal_wrap;
      html = _.template(this.modal_tpl, {
        contents: this.contents
      });
      this.$modal = $(html);
      modal_wrap = this.$modal;
      $('li.help_center_tutorial', this.$modal).on('click', function() {
        var li;
        console.log('TOUR START');
        li = this;
        modal_wrap.modal('hide');
        return $('.tutorial', li).tutorial();
      });
      this.$modal.modal({
        show: true
      });
      return $('body').append(this.$modal);
    };

    HelpCenter.prototype.show = function() {
      return this.$modal.modal('show');
    };

    HelpCenter.prototype.contents_config = {
      "organization:what_is": {
        "type": "question",
        "title": "What is an organization?",
        "body": "An organization is ... (markdown string)"
      },
      "organization:page_tour": {
        "type": "tutorial",
        "title": "Organization page tour",
        "body": "Take the tour of this page",
        "slides": [
          {
            "title": "Description",
            "body": "This is the organization description",
            "target": "#logo",
            "location": "tl",
            "arrow": "bc"
          }, {
            "title": "Contact information",
            "body": "Here you'll find contact",
            "target": ".view-list-visualization-header",
            "location": "tl",
            "arrow": "tc"
          }
        ]
      }
    };

    return HelpCenter;

  })();

  window.HelpCenter = HelpCenter;

}).call(this);
