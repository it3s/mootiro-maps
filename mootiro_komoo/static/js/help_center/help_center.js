(function() {
  var $, HelpCenter,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  $ = jQuery;

  HelpCenter = (function() {

    function HelpCenter(btn_selector, content_ids) {
      this.show = __bind(this.show, this);
      this.tutorials_setup = __bind(this.tutorials_setup, this);
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
      this.tutorials_setup();
    }

    HelpCenter.prototype.question_tpl = "        <article>            <h3><%= question %></h3>            <p><%= answer %></p>        </article>        ";

    HelpCenter.prototype.tutorials_tpl = "        <% for (var i = 0; i < contents.length; i++) { %>          <!--!--------- TUTORIAL ----------->          <% if (contents[i].type == 'tutorial') { %>            <ol id='joyride<%= i %>' class=''>              <% for (var j = 0; j < contents[i].slides.length; j++) { %>              <li data-id='<%= contents[i].slides[j].target_id %>' data-button='Next' data-options='<%= contents[i].slides[j].options %>'>                <h2><%= contents[i].slides[j].title %></h2>                <p><%= contents[i].slides[j].body %></p>              </li>              <% } %>            </ol>          <% } %>          <!--!------------------------------>        <% } %>        ";

    HelpCenter.prototype.modal_tpl = "        <div id='help_center' class='modal hide fade'>          <div class='modal-header'>            <button type='button' class='close' data-dismiss='modal'>×</button>            <h2>Help Center</h2>          </div>          <section class='modal-body'>            <ul>              <% for (var i = 0; i < contents.length; i++) { %>              <li class='<%= contents[i].type %>'>                <!--!--------- QUESTION ----------->                <% if (contents[i].type == 'question') { %>                <article>                  <h3><%= contents[i].title %></h3>                  <p><%= contents[i].body %></p>                </article>                <% } %>                <!--!--------- TUTORIAL ----------->                <% if (contents[i].type == 'tutorial') { %>                  <article data-tutorial-id='<%= i %>'>                    <h3><%= contents[i].title %></h3>                    <p><%= contents[i].body %></p>                  </article>                <% } %>                <!--!------------------------------>              </li>              <% } %>            </ul>          </section>        </div>        ";

    HelpCenter.prototype.modal_setup = function() {
      var html;
      html = _.template(this.modal_tpl, {
        contents: this.contents
      });
      this.$modal = $(html);
      this.$modal.modal({
        show: false
      });
      return $('body').append(this.$modal);
    };

    HelpCenter.prototype.tutorials_setup = function() {
      var html, modal_wrap;
      html = _.template(this.tutorials_tpl, {
        contents: this.contents
      });
      this.$tutorials = $(html);
      $('body').append(this.$tutorials);
      modal_wrap = this.$modal;
      return $('li.tutorial', this.$modal).on('click', function() {
        var tutorial_id;
        modal_wrap.modal('hide');
        tutorial_id = $('article', this).attr('data-tutorial-id');
        console.log($('#joyride' + tutorial_id));
        return $('#joyride' + tutorial_id).joyride({});
      });
    };

    HelpCenter.prototype.show = function() {
      return this.$modal.modal('show');
    };

    HelpCenter.prototype.contents_config = {
      "maps:initial_tour": {
        "type": "tutorial",
        "title": "Initial Tour",
        "body": "Take the tour.",
        "slides": [
          {
            "title": "MootiroMaps",
            "body": "This is the logo.",
            "target_id": "logo",
            "options": "tipLocation:bottom"
          }, {
            "title": "End",
            "body": "Feel free... stay around...",
            "target_id": "",
            "options": ""
          }
        ]
      },
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
            "title": "Welcome to the tour!",
            "body": "It's a pleasure to meet you.",
            "target_id": "",
            "options": ""
          }, {
            "title": "MootiroMaps",
            "body": "This is the MootiroMaps logo. You can click it anytime to get into website's homepage.",
            "target_id": "logo",
            "options": "tipLocation:bottom"
          }, {
            "title": "Map preview",
            "body": "Here is the organization in the map.",
            "target_id": "map-container-preview",
            "options": "tipLocation:bottom"
          }, {
            "title": "Footer",
            "body": "Can I <strong>bold this</strong>? <em>Yes</em>!",
            "target_id": "footer",
            "options": "tipLocation:top"
          }, {
            "title": "End",
            "body": "Feel free... stay around...",
            "target_id": "",
            "options": ""
          }
        ]
      }
    };

    return HelpCenter;

  })();

  window.HelpCenter = HelpCenter;

}).call(this);
