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

    HelpCenter.prototype.modal_tpl = "        <div id='help_center' class='modal hide fade'>          <div class='modal-header'>            <button type='button' class='close' data-dismiss='modal'>×</button>            <h2>Central de Ajuda</h2>          </div>          <section class='modal-body'>            <ul id='questions'>              <% for (var i = 0; i < questions.length; i++) { %>              <li class='<%= questions[i].type %>'>                <!------------ QUESTION ----------->                <article>                  <h3><%= questions[i].title %></h3>                  <p><%= questions[i].body %></p>                </article>                <!--------------------------------->              </li>              <% } %>            </ul>            <% if (hasTour) { %><button id='tour_button'>Faça o tour desta página</button><% } %>          </section>        </div>        ";

    HelpCenter.prototype.modal_setup = function() {
      var html;
      html = _.template(this.modal_tpl, {
        questions: this.questions,
        hasTour: this.tour != null
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
      "home": {
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
      },
      "map": {
        "slides": [
          {
            "title": "Localização do ponto",
            "body": "Escolha entre endereço (insira rua, número e município ou insira o CEP) ou coordenada (latitude e longitude) para encontrar a localização.",
            "selector": "#map-searchbox"
          }, {
            "title": "Filtrar por raio",
            "body": "Selecione um ponto no mapa e estabeleça a distância (raio) em que deseja que apareçam os objetos mapeados no território.",
            "selector": "#map-panel-filter-tab"
          }, {
            "title": "Adicionar um objeto",
            "body": 'Escolha o objeto que melhor se aplica ao que será mapeado e adicione ao mapa uma linha, um ponto ou uma área. Conclua o mapeamento pressionando o botão "avançar".',
            "selector": "#map-panel-add-tab"
          }, {
            "title": "Filtrar por camada",
            "body": "Estabeleça a camada e filtre os objetos a serem apresentados no mapa.",
            "selector": "#map-panel-layers-tab"
          }
        ]
      },
      "community_list": {
        "slides": [
          {
            "title": "Lista de comunidades",
            "body": "Aqui estão listadas  com uma curta descrição todas as comunidades cadastradas no MootiroMaps. Clique no nome da comunidade para acessar o cadastro completo.",
            "selector": "div.view-list-item > h4 > span > a"
          }, {
            "title": "Ponto no mapa",
            "body": "Clique para visualizar previamente o objeto no mapa.",
            "selector": "div.view-list-item > h4 > a.list-map-preview",
            "options": "tipLocation:right;",
            "offsetY": -20
          }, {
            "title": "Visualização e filtragem",
            "body": "Você pode escolher como deseja visualizar a listagem: por ordem alfabética ou data de cadastro. Também pode filtrar por palavras-chave.",
            "selector": "div.view-list-visualization-header i",
            "options": "tipLocation:right;",
            "offsetX": 20,
            "offsetY": -28
          }
        ]
      },
      "organization_list": {
        "slides": [
          {
            "title": "Lista de organizações",
            "body": "Aqui estão listadas com uma curta descrição todas as organizações cadastradas no MootiroMaps. Clique no nome da organização para acessar o cadastro completo.",
            "selector": "div.view-list-item a.org-list-name"
          }, {
            "title": "Visualização e filtragem",
            "body": "Você pode escolher como deseja visualizar a listagem: por ordem alfabética ou data de cadastro. Também pode filtrar por palavras-chave.",
            "selector": "div.view-list-visualization-header i",
            "options": "tipLocation:right;",
            "offsetX": 20,
            "offsetY": -28
          }, {
            "title": "Adicionar uma organização",
            "body": "Clique aqui e cadastre no MootiroMaps uma nova organização.",
            "selector": "div.button-new"
          }
        ]
      },
      "need_list": {
        "slides": [
          {
            "title": "Lista de necessidades",
            "body": "Aqui estão listadas com uma curta descrição todas as necessidades cadastradas no MootiroMaps. Clique no nome da necessidade para acessar o cadastro completo.",
            "selector": "div.view-list-item > h4 > span > a"
          }, {
            "title": "Ponto no mapa",
            "body": "Clique para visualizar previamente o objeto no mapa.",
            "selector": "div.view-list-item > h4 > a.list-map-preview",
            "options": "tipLocation:right;",
            "offsetY": -20
          }, {
            "title": "Visualização e filtragem",
            "body": "Você pode escolher como deseja visualizar a listagem: por ordem alfabética ou data de cadastro. Também pode filtrar por palavras-chave.",
            "selector": "div.view-list-visualization-header i",
            "options": "tipLocation:right;",
            "offsetX": 20,
            "offsetY": -28
          }, {
            "title": "Adicionar uma necessidade",
            "body": "Clique aqui e cadastre no MootiroMaps uma nova necessidade.",
            "selector": "div.button-new"
          }
        ]
      },
      "resource_list": {
        "slides": [
          {
            "title": "Lista de recursos",
            "body": "Aqui estão listados com uma curta descrição todos os recursos cadastrados no MootiroMaps. Clique no nome do recurso para acessar o cadastro completo.",
            "selector": "div.view-list-item > h4 > span > a"
          }, {
            "title": "Ponto no mapa",
            "body": "Clique aqui para visualizar previamente o objeto desejado no mapa.",
            "selector": "div.view-list-item > h4 > a.list-map-preview",
            "options": "tipLocation:right;",
            "offsetY": -20
          }, {
            "title": "Visualização e filtragem",
            "body": "Você pode escolher como deseja visualizar a listagem: por ordem alfabética ou data de cadastro. Também pode filtrar por palavras-chave.",
            "selector": "div.view-list-visualization-header i",
            "options": "tipLocation:right;",
            "offsetX": 20,
            "offsetY": -28
          }, {
            "title": "Adicionar um recurso",
            "body": "Clique aqui e cadastre no MootiroMaps um novo recurso.",
            "selector": "div.button-new"
          }
        ]
      },
      "investment_list": {
        "slides": [
          {
            "title": "Lista de investimentos",
            "body": "Aqui estão listados  com uma curta descrição todos os investimentos cadastrados no MootiroMaps. Clique no nome do investimentos para acessar o cadastro completo.",
            "selector": "div.view-list-item > h4 > span > a"
          }, {
            "title": "Ponto no mapa",
            "body": "Clique aqui para visualizar previamente o objeto no mapa.",
            "selector": "div.view-list-item > h4 > a.list-map-preview",
            "options": "tipLocation:right;",
            "offsetY": -20
          }, {
            "title": "Visualização e filtragem",
            "body": "Você pode escolher como deseja visualizar a listagem: por ordem alfabética ou data de cadastro. Também pode filtrar por palavras-chave.",
            "selector": "div.view-list-visualization-header",
            "options": "tipLocation:right;",
            "offsetX": 20
          }
        ]
      },
      "project_list": {
        "slides": [
          {
            "title": "Lista de projetos",
            "body": "Aqui estão listados com uma curta descrição todos os projetos cadastrados no MootiroMaps. Clique no nome do projetos para acessar o cadastro completo.",
            "selector": "div.view-list-item span > a"
          }, {
            "title": "Visualização e filtragem",
            "body": "Você pode filtrar a busca por palavras-chave.",
            "selector": "div.view-list-visualization-header i",
            "options": "tipLocation:right;",
            "offsetX": 20,
            "offsetY": -28
          }, {
            "title": "Adicionar um projeto",
            "body": "Clique aqui e comece um novo projeto de mapeamento no MootiroMaps.",
            "selector": "div.button-new"
          }
        ]
      },
      "community_show": {
        "slides": [
          {
            "title": "Título da comunidade",
            "body": "Este é o nome com o qual o território foi cadastrado.",
            "selector": ".main-column h2.title"
          }, {
            "title": "Edição do conteúdo",
            "body": "Para editar o conteúdo dessa página o usuário deve clicar neste botão.",
            "selector": "div.view-edit-btn",
            "options": "tipLocation:bottom;nubPosition:top-right;",
            "offsetX": -135
          }, {
            "title": "Perfil da comunidade",
            "body": "O preenchimento deste campo mostra uma descrição da comunidade, como a localização, histórico, perfil socioeconômico da população etc.",
            "selector": ".main-column .mark-down",
            "options": "tipLocation:left;"
          }, {
            "title": "No mapa",
            "body": "O mapa traz uma prévia visualização da comunidade.",
            "selector": "#map-preview",
            "options": "tipLocation:left;"
          }, {
            "title": "Comunidades próximas",
            "body": "O campo mostra outras comunidades cadastradas no MootiroMaps que estão próximas a esta.",
            "selector": ".right-bar .nearby-communities",
            "options": "tipLocation:left;"
          }
        ]
      },
      "organization_show": {
        "slides": [
          {
            "title": "Título da organização",
            "body": "Este é o nome com o qual a organização foi cadastrada.",
            "selector": ".organization-header"
          }, {
            "title": "Edição do conteúdo",
            "body": "Para editar o conteúdo dessa página, o usuário deve clicar neste botão.",
            "selector": "div.view-edit-btn",
            "options": "tipLocation:bottom;nubPosition:top-right;",
            "offsetX": -135
          }, {
            "title": "Descrição da organização",
            "body": "O preenchimento deste campo mostra a descrição da organização, como temática de atuação, objetivos, projetos e serviços, parceiros, financiadores etc.",
            "selector": ".main-column .mark-down",
            "options": "tipLocation:left;"
          }, {
            "title": "No mapa",
            "body": "O mapa traz uma prévia visualização da organização no território.",
            "selector": "#map-preview",
            "options": "tipLocation:left;"
          }, {
            "title": "Projetos",
            "body": "O campo apresenta a quais projetos de mapeamento esta organização está relacionada.",
            "selector": ".projects-tag-header",
            "options": "tipLocation:left;"
          }
        ]
      },
      "need_show": {
        "slides": [
          {
            "title": "Título da necessidade",
            "body": "Este é o nome com o qual a necessidade foi cadastrada.",
            "selector": ".need-title"
          }, {
            "title": "Edição do conteúdo",
            "body": "Para editar o conteúdo dessa página, o usuário deve clicar neste botão.",
            "selector": "div.view-edit-btn",
            "options": "tipLocation:bottom;nubPosition:top-right;",
            "offsetX": -135
          }, {
            "title": "Descrição da necessidade",
            "body": "O preenchimento deste campo mostra a descrição da necessidade e permite que os usuários consigam compreender a natureza da problemática.",
            "selector": ".main-column .mark-down",
            "options": "tipLocation:right;"
          }, {
            "title": "No mapa",
            "body": "O mapa traz uma prévia visualização da necessidade no território.",
            "selector": "#map-preview",
            "options": "tipLocation:left;"
          }, {
            "title": "Proposta de resolução",
            "body": "Neste campo é possível inserir novas propostas de resolução da necessidade.",
            "selector": ".need-proposals",
            "options": "tipLocation:left;"
          }, {
            "title": "Necessidades semelhantes",
            "body": "O MootiroMaps relaciona necessidades semelhantes ou próximas para facilitar que os usuários troquem experiências e discutam como resolvê-las.",
            "selector": "#related-needs",
            "options": "tipLocation:left;"
          }
        ]
      },
      "resource_show": {
        "slides": [
          {
            "title": "Título do recurso",
            "body": "Este é o nome com o qual o recurso foi cadastrado.",
            "selector": "h2.title"
          }, {
            "title": "Edição do conteúdo",
            "body": "Para editar o conteúdo dessa página, o usuário deve clicar neste botão.",
            "selector": "div.view-edit-btn",
            "options": "tipLocation:bottom;nubPosition:top-right;",
            "offsetX": -135
          }, {
            "title": "Descrição do recurso",
            "body": "O preenchimento deste campo mostra a descrição do recurso, como localização, horários de atendimento, temática, projetos e serviços etc.",
            "selector": ".main-column .mark-down",
            "options": "tipLocation:right;"
          }, {
            "title": "No mapa",
            "body": "O mapa traz uma prévia visualização do recurso no território.",
            "selector": "#map-preview",
            "options": "tipLocation:left;"
          }, {
            "title": "Recursos semelhantes",
            "body": "O campo permite que os usuários identifiquem recursos semelhantes ou próximos.",
            "selector": ".related-resource",
            "options": "tipLocation:left;",
            "offsetX": -10,
            "offsetY": -25
          }
        ]
      },
      "investment_show": {
        "slides": [
          {
            "title": "Título do investimento",
            "body": "Este é o nome com o qual o investimento foi cadastrado.",
            "selector": "h2.title"
          }, {
            "title": "Edição do conteúdo",
            "body": "Para editar o conteúdo dessa página, o usuário deve clicar neste botão.",
            "selector": "div.view-edit-btn",
            "options": "tipLocation:bottom;nubPosition:top-right;",
            "offsetX": -135
          }, {
            "title": "Descrição do investimento",
            "body": "O preenchimento deste campo mostra a descrição do investimento, como o objetivo, localização, temática, público-alvo etc.",
            "selector": ".main-column .mark-down",
            "options": "tipLocation:right;"
          }
        ]
      },
      "project_show": {
        "slides": [
          {
            "title": "Título do projeto",
            "body": "Este é o nome com o qual o projeto foi cadastrado.",
            "selector": "h2.title"
          }, {
            "title": "Edição do conteúdo",
            "body": "Para editar o conteúdo dessa página, o usuário deve clicar neste botão.",
            "selector": "div.view-edit-btn",
            "options": "tipLocation:bottom;nubPosition:top-right;",
            "offsetX": -135
          }, {
            "title": "Descrição do projeto",
            "body": "O preenchimento deste campo mostra a descrição do projeto, como o objetivo, localização, temática, público-alvo, apoiadores etc.",
            "selector": ".main-column .mark-down",
            "options": "tipLocation:right;"
          }, {
            "title": "Objetos relacionados",
            "body": "A listagem mostra objetos (organizações, recursos, necessidades etc) que foram cadastrados e relacionados a esse projeto.",
            "selector": ".view-info-buttons",
            "options": "tipLocation:top;",
            "offsetX": 50
          }, {
            "title": "No mapa",
            "body": "O mapa traz uma prévia visualização do recurso no território.",
            "selector": "#map-preview",
            "options": "tipLocation:left;"
          }, {
            "title": "Participantes",
            "body": "O campo mostra o usuário administrador e os colaboradores.",
            "selector": ".view-info-btn:last"
          }
        ]
      }
    };

    return HelpCenter;

  })();

  window.HelpCenter = HelpCenter;

}).call(this);
