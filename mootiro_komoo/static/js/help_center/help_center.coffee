$ = jQuery


class HelpCenter
    constructor: (btn_selector, questions_ids, tour_id) ->
        @button = $(btn_selector)
        @button.on 'click', @show
        @questions = (@questions_config[cid] for cid in questions_ids)
        @tour = @tours_config[tour_id] if tour_id
        @modal_setup()
        @tour_setup()

    # TODO: put these html templates into an html file
    tour_tpl:
        "
        <!------------ PAGE TOUR ----------->
        <ol id='joyride'>
          <% for (var j = 0; j < tour.slides.length; j++) { %>
          <li data-selector='<%= tour.slides[j].selector %>'
            data-button=
                <% if (j != tour.slides.length-1) { %>'Próximo'<% } else { %>'Fim'<% } %>
            data-options='<%= tour.slides[j].options %>'
            data-offsetX='<%= tour.slides[j].offsetX %>'
            data-offsetY='<%= tour.slides[j].offsetY %>'
          >
            <h2><%= tour.slides[j].title %></h2>
            <p><%= tour.slides[j].body %></p>
          </li>
          <% } %>
        </ol>
        <!--------------------------------->
        "

    modal_tpl:
        "
        <div id='help_center' class='modal hide fade'>
          <div class='modal-header'>
            <button type='button' class='close' data-dismiss='modal'>×</button>
            <h2>Central de Ajuda</h2>
          </div>
          <section class='modal-body'>
            <ul id='questions'>
              <% for (var i = 0; i < questions.length; i++) { %>
              <li class='<%= questions[i].type %>'>
                <!------------ QUESTION ----------->
                <article>
                  <h3><%= questions[i].title %></h3>
                  <p><%= questions[i].body %></p>
                </article>
                <!--------------------------------->
              </li>
              <% } %>
            </ul>
            <% if (hasTour) { %><button id='tour_button'>Faça o tour desta página</button><% } %>
          </section>
        </div>
        "

    modal_setup: =>
        html = _.template @modal_tpl, {questions: @questions, hasTour: @tour?}
        @$modal = $(html)
        @$modal.modal {show: true}
        $('body').append @$modal

    tour_setup: =>
        html = _.template @tour_tpl, {tour: @tour}
        @$tour_content = $(html)
        $('body').append @$tour_content

        modal_wrap = @$modal

        $('button#tour_button', @$modal).on 'click', () ->
            modal_wrap.modal 'hide'
            $('#joyride').joyride {
                # fix joyride tip positioning
                'afterShowCallback': () ->
                    x  = this.$current_tip.offset().left
                    y  = this.$current_tip.offset().top
                    dx = this.$li.attr('data-offsetX')
                    dy = this.$li.attr('data-offsetY')
                    dx = if dx == 'undefined' then 0 else parseInt dx
                    dy = if dy == 'undefined' then 0 else parseInt dy
                    this.$current_tip.offset({left: x+dx, top: y+dy})
            }

    show: () =>
        @$modal.modal('show')

    # TODO:use requires and put this json into other file
    questions_config:
        "organization:what_is":
            "title": "What is an organization?"
            "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eu quam odio, ac sagittis nisi. Nam et scelerisque ligula. Ut id velit eu nulla interdum aliquam luctus sed odio. Suspendisse et nunc at ipsum sodales euismod. Vivamus scelerisque rutrum leo id blandit. Maecenas vel risus magna, at pulvinar turpis."

    tours_config:
        "home:tour":
            "slides": [
                {
                "title": "MootiroMaps"
                "body": "Clique no logo do MootiroMaps e você será redirecionado para a página central."
                "selector": "#logo"
                },
                {
                "title": "Login"
                "body": "Para criar um perfil no MootiroMaps ou logar na plataforma, clique aqui."
                "selector": "#login_button"
                "options": "tipLocation:left;nubPosition:top-right;"
                "offsetX": -230
                },
                {
                "title": "Página do usuário"
                "body": "Clicando aqui você encontra informações sobre o usuário, contatos e últimas edições feitas."
                "selector": "#user_menu"
                "options": "tipLocation:left;nubPosition:top-right;"
                "offsetX": -90
                },
                {
                "title": "Visualize o mapa"
                "body": "Aqui você encontra no mapa os objetos já mapeados em todo o Brasil. "
                "selector": "#menu .map"
                },
                {
                "title": "Objetos cadastrados"
                "body": "Escolha o tipo de objeto cadastrado e veja as listas correspondentes em ordem alfabética."
                "selector": "#menu .objects"
                },
                {
                "title": "Projetos cadastrados"
                "body": "Visualize a lista em ordem alfabética de projetos cadastrados no MootiroMaps."
                "selector": "#menu .projects"
                },
                {
                "title": "Blog do IT3S"
                "body": "Em nosso Blog postamos análises e opinões sobre transparência, mobilização social e colaboração. Clique e leia."
                "selector": ".news .blog"
                "options": "tipLocation:left;"
                },
                {
                "title": "Edições recentes"
                "body": "Acompanhe as atualizações feitas pelos usuários do MootiroMaps. Os ícones mostram os tipos de objetos editados. Edite você também."
                "selector": ".news .last_updates"
                "options": "tipLocation:right;"
                },
            ]
        "map:tour":
            "slides": [
                {
                "title": "Localização do ponto"
                "body": "Escolha entre endereço (insira rua, número e município ou insira o CEP) ou coordenada (latitude e longitude) para encontrar a localização."
                "selector": "#map-searchbox"
                },
                {
                "title": "Filtrar por raio"
                "body": "Selecione um ponto no mapa e estabeleça a distância (raio) em que deseja que apareçam os objetos mapeados no território."
                "selector": "#map-panel-filter-tab"
                },
                {
                "title": "Adicionar um objeto"
                "body": 'Escolha o objeto que melhor se aplica ao que será mapeado e adicione ao mapa uma linha, um ponto ou uma área. Conclua o mapeamento pressionando o botão "avançar".'
                "selector": "#map-panel-add-tab"
                },
                {
                "title": "Filtrar por camada"
                "body": "Estabeleça a camada e filtre os objetos a serem apresentados no mapa."
                "selector": "#map-panel-layers-tab"
                },
            ]


window.HelpCenter = HelpCenter
