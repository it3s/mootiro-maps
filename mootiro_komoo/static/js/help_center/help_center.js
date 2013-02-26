(function() {
  var $, HelpCenter,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  $ = jQuery;

  HelpCenter = (function() {

    function HelpCenter(btn_selector, questions_ids, tour_id) {
      this.show = __bind(this.show, this);
      this.tour_setup = __bind(this.tour_setup, this);
      this.modal_setup = __bind(this.modal_setup, this);
      var cid;
      this.button = $(btn_selector);
      this.button.on('click', this.show);
      this.questions = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = questions_ids.length; _i < _len; _i++) {
          cid = questions_ids[_i];
          _results.push(this.questions_config[cid]);
        }
        return _results;
      }).call(this);
      if (tour_id) this.tour = this.tours_config[tour_id];
      this.modal_setup();
      this.tour_setup();
    }

    HelpCenter.prototype.tour_tpl = "        <!------------ PAGE TOUR ----------->        <ol id='joyride'>          <% for (var j = 0; j < tour.slides.length; j++) { %>          <li data-selector='<%= tour.slides[j].selector %>'            data-button=                <% if (j != tour.slides.length-1) { %>'Próximo'<% } else { %>'Fim'<% } %>            data-options='<%= tour.slides[j].options %>'            data-offsetX='<%= tour.slides[j].offsetX %>'            data-offsetY='<%= tour.slides[j].offsetY %>'          >            <h2><%= tour.slides[j].title %></h2>            <p><%= tour.slides[j].body %></p>          </li>          <% } %>        </ol>        <!--------------------------------->        ";

    HelpCenter.prototype.modal_tpl = "        <div id='help_center' class='modal hide fade'>          <div class='modal-header'>            <button type='button' class='close' data-dismiss='modal'>×</button>            <h2>Central de Ajuda</h2>          </div>          <section class='modal-body'>            <ul id='questions'>              <% for (var i = 0; i < questions.length; i++) { %>              <li class='<%= questions[i].type %>'>                <!------------ QUESTION ----------->                <article>                  <h3><%= questions[i].title %></h3>                  <p><%= questions[i].body %></p>                </article>                <!--------------------------------->              </li>              <% } %>            </ul>            <button id='tour_button'>Faça o tour desta página</button>          </section>        </div>        ";

    HelpCenter.prototype.modal_setup = function() {
      var html;
      html = _.template(this.modal_tpl, {
        questions: this.questions
      });
      this.$modal = $(html);
      this.$modal.modal({
        show: true
      });
      return $('body').append(this.$modal);
    };

    HelpCenter.prototype.tour_setup = function() {
      var html, modal_wrap;
      html = _.template(this.tour_tpl, {
        tour: this.tour
      });
      this.$tour_content = $(html);
      $('body').append(this.$tour_content);
      modal_wrap = this.$modal;
      return $('button#tour_button', this.$modal).on('click', function() {
        modal_wrap.modal('hide');
        return $('#joyride').joyride({
          'afterShowCallback': function() {
            var dx, dy, x, y;
            x = this.$current_tip.offset().left;
            y = this.$current_tip.offset().top;
            dx = this.$li.attr('data-offsetX');
            dy = this.$li.attr('data-offsetY');
            dx = dx === 'undefined' ? 0 : parseInt(dx);
            dy = dy === 'undefined' ? 0 : parseInt(dy);
            return this.$current_tip.offset({
              left: x + dx,
              top: y + dy
            });
          }
        });
      });
    };

    HelpCenter.prototype.show = function() {
      return this.$modal.modal('show');
    };

    HelpCenter.prototype.questions_config = {
      "organization:what_is": {
        "title": "What is an organization?",
        "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eu quam odio, ac sagittis nisi. Nam et scelerisque ligula. Ut id velit eu nulla interdum aliquam luctus sed odio. Suspendisse et nunc at ipsum sodales euismod. Vivamus scelerisque rutrum leo id blandit. Maecenas vel risus magna, at pulvinar turpis."
      }
    };

    HelpCenter.prototype.tours_config = {
      "maps:initial_tour": {
        "title": "Initial Tour",
        "body": "Take the tour.",
        "slides": [
          {
            "title": "MootiroMaps",
            "body": "This is the logo.",
            "selector": "#logo",
            "options": "tipLocation:bottom"
          }, {
            "title": "End",
            "body": "Feel free... stay around...",
            "selector": "",
            "options": ""
          }
        ]
      },
      "organization:page_tour": {
        "slides": [
          {
            "title": "MootiroMaps",
            "body": "Clique no logo do MootiroMaps e você será redirecionado para a página central.",
            "selector": "#logo"
          }, {
            "title": "Login",
            "body": "Para criar um perfil no MootiroMaps ou logar na plataforma, clique aqui.",
            "selector": "#login_button",
            "options": "tipLocation:left;nubPosition:top-right;",
            "offsetX": -230
          }, {
            "title": "Página do usuário",
            "body": "Clicando aqui você encontra informações sobre o usuário, contatos e últimas edições feitas.",
            "selector": "#user_menu",
            "options": "tipLocation:left;nubPosition:top-right;",
            "offsetX": -90
          }, {
            "title": "Visualize o mapa",
            "body": "Aqui você encontra no mapa os objetos já mapeados em todo o Brasil. ",
            "selector": "#menu .map"
          }, {
            "title": "Objetos cadastrados",
            "body": "Escolha o tipo de objeto cadastrado e veja as listas correspondentes em ordem alfabética.",
            "selector": "#menu .objects"
          }, {
            "title": "Projetos cadastrados",
            "body": "Visualize a lista em ordem alfabética de projetos cadastrados no MootiroMaps.",
            "selector": "#menu .projects"
          }, {
            "title": "Blog do IT3S",
            "body": "Em nosso Blog postamos análises e opinões sobre transparência, mobilização social e colaboração. Clique e leia.",
            "selector": ".news .blog",
            "options": "tipLocation:left;"
          }, {
            "title": "Edições recentes",
            "body": "Acompanhe as atualizações feitas pelos usuários do MootiroMaps. Os ícones mostram os tipos de objetos editados. Edite você também.",
            "selector": ".news .last_updates",
            "options": "tipLocation:right;"
          }
        ]
      }
    };

    return HelpCenter;

  })();

  window.HelpCenter = HelpCenter;

}).call(this);
