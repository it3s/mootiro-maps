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
            data-button='<% if (j != tour.slides.length-1) { print(gettext('Next')); } else { print(gettext('Finish')); } %>'
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
            <h2><%= gettext('Help Center') %></h2>
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
            <% if (hasTour) { %><button id='tour_button'><%= gettext('Take the guided tour') %></button><% } %>
            <a id='help_center_about' href='/about/'><%= gettext('About') %></a>
            <a id='help_center_usecases' href='/use_cases/'><%= gettext('Use Cases') %></a>
          </section>
        </div>
        "

    modal_setup: =>
        html = _.template @modal_tpl, {questions: @questions, hasTour: @tour?}
        @$modal = $(html)
        @$modal.modal {show: false}
        $('body').append @$modal

    tour_setup: =>
        if not @tour?
            return
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
        {"home:others_edition": {"body": "Na p\u00e1gina de cada objeto cadastrado o bot\u00e3o \"Hist\u00f3rico\" apresenta informa\u00e7\u00f5es sobre a cria\u00e7\u00e3o e edi\u00e7\u00f5es recentes.", "title": "Como eu posso saber se outro usu\u00e1rio editou um cadastro?"}, "community:what_is": {"body": "Comunidade pode ser uma rua, bairro, favela, cidade, aldeia ind\u00edgena etc., ou seja, um determinado territ\u00f3rio. Mapear uma comunidade \u00e9 o primeiro passo para o desenvolvimento local e permite que sejam realizados diagn\u00f3sticos territoriais.", "title": "O que \u00e9 uma \"comunidade\" e por que mape\u00e1-la?"}, "user:name_edition": {"body": "Sim. Na p\u00e1gina do usu\u00e1rio clique no campo \"Nome\" e edite. Para tanto \u00e9 preciso estar logado.", "title": "Posso editar meu nome?"}, "user:password": {"body": "N\u00e3o h\u00e1 limite de caracteres para a senha, mas quanto mais letras e n\u00fameros misturados mais segura ser\u00e1 sua senha.", "title": "Como deve ser a minha senha?"}, "home:mootiro_maps": {"body": "\u00c9 uma plataforma de mapeamento colaborativo de comunidades, suas organiza\u00e7\u00f5es, recursos e necessidades voltada para o desenvolvimento comunit\u00e1rio.", "title": "O que \u00e9 o MootiroMaps?"}, "user:data": {"body": "O MootiroMaps tem como um de seus objetivos conectar mapeadores possibilitando que troquem experi\u00eancias, conhe\u00e7am outros projetos e colaborem entre si. Informa\u00e7\u00f5es de contato e de localiza\u00e7\u00e3o s\u00e3o importantes para que outros usu\u00e1rios possam entrar em contato com voc\u00ea.", "title": "Por que informar meus dados?"}, "community:geometry_edition": {"body": "Sim! Para voc\u00ea editar os pontos no mapa de uma comunidade, abra o cadastro da comunidade. L\u00e1, clique no bot\u00e3o \"editar\" (l\u00e1pis). Dentro do cadastro voc\u00ea encontrar\u00e1 uma op\u00e7\u00e3o para abrir o editor de mapas. Arraste os pontos e salve sua edi\u00e7\u00e3o.", "title": "Posso editar os pontos no mapa de uma comunidade?"}, "need:proposal": {"body": "Para que os usu\u00e1rios, principalmente os moradores daquela regi\u00e3o, possam juntos debater as necessidades e como resolv\u00ea-las.", "title": "Para que servem as propostas?"}, "need:discuss": {"body": "Basta clicar no bot\u00e3o [[[tal]]] e inserir sua opini\u00e3o e reflex\u00e3o sobre a necessidade.", "title": "Como discutir uma necessidade?"}, "investment:what_is": {"body": "Trata-se de um investimento social que envolve ou n\u00e3o dinheiro, feito por empresas, funda\u00e7\u00f5es, pessoas f\u00edsicas. O cadastro \u00e9 fundamental para gerar transpar\u00eancia e apresentar a rela\u00e7\u00e3o entre investidores e organiza\u00e7\u00f5es que receberam o investimento.", "title": "O que \u00e9 um \"investimento\" e por que cadastr\u00e1-lo?"}, "map:radius_search": {"body": "Usando essa ferramenta \u00e9 poss\u00edvel escolher um ponto central no mapa e estabelecer o raio de dist\u00e2ncia em que voc\u00ea deseja visualizar os objetos mapeados. Trata-se de um modo pr\u00e1tico para o diagn\u00f3stico territorial.", "title": "O que significa a \"Busca por raio\"?"}, "project:what_is": {"body": "Projetos s\u00e3o a\u00e7\u00f5es de mapeamento que est\u00e3o acontecendo no MootiroMaps. Dentro do projeto podem ser reaproveitados todos os objetos e informa\u00e7\u00f5es j\u00e1 criados no mapa.", "title": "O que \u00e9 um \"projeto\" e por que cadastr\u00e1-lo?"}, "home:search": {"body": "A principal ferramenta de busca est\u00e1 localizada no cabe\u00e7alho do MootiroMaps, onde podem ser inseridos endere\u00e7os ou nomes de organiza\u00e7\u00f5es, comunidades etc. \u00c9 poss\u00edvel tamb\u00e9m acessar no menu superior a p\u00e1gina de cada tipo de objeto e inserir palavras-chaves no campo \"Op\u00e7\u00f5es de Visualiza\u00e7\u00e3o e Filtragem\" para uma busca mais espec\u00edfica nas listas.", "title": "Como posso buscar um objeto no MootiroMaps?"}, "resource:acronym": {"body": "Ao criar ou editar um cadastro \u00e9 importante usar sigla e nome do recurso para facilitar a busca. Existem recursos que s\u00e3o mais conhecidas pela sua sigla. Exemplo: Centro da Juventude - CJ.", "title": "Por que \u00e9 importante inserir a sigla junto ao nome do recurso?"}, "organization:transparency": {"body": "Para atender ativamente a Lei de Acesso \u00e0 Informa\u00e7\u00e3o (Lei 12.527) e permitir que os cidad\u00e3os acessem com facilidade informa\u00e7\u00f5es como CNPJ, financiamento, parceiros etc.", "title": "Por que a transpar\u00eancia das informa\u00e7\u00f5es sobre uma organiza\u00e7\u00e3o \u00e9 importante?"}, "home:denounce_content": {"body": "Sim. Ao final da p\u00e1gina de cada objeto cadastrado o bot\u00e3o \"Denunciar\" permite que o usu\u00e1rio registre sua den\u00fancia.", "title": "Eu posso denunciar um cadastro?"}, "project:batch_upload": {"body": "A importa\u00e7\u00e3o de dados \u00e9 importante, para disponibilizar no mapa informa\u00e7\u00f5es que voc\u00ea j\u00e1 coletou ou tem dispon\u00edvel em planilhas. Para adicionar dados em lote, voc\u00ea deve clicar no bot\u00e3o \"importar dados\" e criar uma nova planilha de importa\u00e7\u00e3o.", "title": "Por que e como adicionar dados em lote?"}, "home:who_can_use": {"body": "Qualquer pessoa ou organiza\u00e7\u00e3o pode navegar e utilizar a plataforma.", "title": "Quem pode usar o MootiroMaps?"}, "user:name": {"body": "Voc\u00ea pode escolher qualquer nome, mas preferimos que use seu primeiro nome e sobrenome.", "title": "Como deve ser o meu nome?"}, "need:name": {"body": "O t\u00edtulo deve descrever, de forma precisa e atrav\u00e9s de palavras-chaves, do que se trata a necessidade. Exemplos: \"buraco na rua\", \"falta de computador\", \"constru\u00e7\u00e3o de escola\" etc.", "title": "O t\u00edtulo da necessidade deve conter quais informa\u00e7\u00f5es?"}, "resource:difference_organization": {"body": "Organiza\u00e7\u00e3o \u00e9 uma entidade que normalmente apresenta estrutura f\u00edsica, CNPJ, colaboradores. Recurso pode ser entendido como o projeto desenvolvido por uma organiza\u00e7\u00e3o, equipamentos, materiais ou espa\u00e7os existentes na comunidade ou como um grupo de pessoas (coletivo) promovendo o desenvolvimento comunit\u00e1rio.", "title": "Qual \u00e9 a diferen\u00e7a entre um recurso e uma organiza\u00e7\u00e3o?"}, "organization:what_is": {"body": "S\u00e3o ONGs, associa\u00e7\u00f5es de bairro, entidades em geral que atuam no Terceiro Setor, empresas, prefeituras. O cadastro ajuda a gerar visibilidade e a criar rela\u00e7\u00e3o com outras ONGs, al\u00e9m de associar recursos, necessidades, investimentos etc.", "title": "O que \u00e9 uma \"organiza\u00e7\u00e3o\" e por que cadastr\u00e1-la?"}, "need:description": {"body": "A descri\u00e7\u00e3o deve explicar do melhor modo poss\u00edvel a situa\u00e7\u00e3o da necessidade: sua localiza\u00e7\u00e3o, materiais ou recursos \u00fateis para resolv\u00ea-la, se uma pessoa ou organiza\u00e7\u00e3o j\u00e1 est\u00e1 cuidando disso etc.", "title": "O que devo inserir no campo \"descri\u00e7\u00e3o\"?"}, "need:categories": {"body": "Classificar as \u00e1reas facilita a busca mais espec\u00edfica na p\u00e1gina das necessidades. Al\u00e9m disso, \u00e9 \u00fatil para os investidores escolherem a \u00e1rea onde desejam aplicar seus recursos. ", "title": "O que s\u00e3o as \"\u00e1reas\" e para que servem?"}, "home:collaborative_mapping": {"body": "Com o mapeamento moradores e organiza\u00e7\u00f5es sociais - atuando colaborativamente - georreferenciam situa\u00e7\u00f5es de vulnerabilidade em suas comunidades, geram de forma aut\u00f4noma indicadores e buscam mudan\u00e7as para as realidades locais propondo solu\u00e7\u00f5es.", "title": "O que significa \"mapeamento colaborativo\"?"}, "investment:name": {"body": "Deve ser inserido o nome do projeto apoioda pelo investimento.", "title": "O que devo inserir no campo \"T\u00edtulo\"?"}, "user:location": {"body": "Para possibilitar que outros mapeadores que atuam ou moram perto de voc\u00ea conhe\u00e7am sua localiza\u00e7\u00e3o e possam entrar em contato.", "title": "Por que informar minha localiza\u00e7\u00e3o? "}, "community:search_data": {"body": "Em sites como o do IBGE (http://www.ibge.gov.br/) ou da prefeitura/subprefeitura de sua cidade.", "title": "Como posso encontrar dados sobre a comunidade?"}, "user:public_contact": {"body": "S\u00e3o informa\u00e7\u00f5es como email, Skype, contas de redes sociais, por onde outros usu\u00e1rios poder\u00e3o entrar em contato com voc\u00ea.", "title": "O que significa o contato p\u00fablico?"}, "community:description (copy)": {"body": "Informa\u00e7\u00f5es como localiza\u00e7\u00e3o, infra-estrutura, hist\u00f3rico, popula\u00e7\u00e3o, perfil s\u00f3cio-econ\u00f4mico, economia, caracter\u00edsticas principais, fontes das informa\u00e7\u00f5es (site da prefeitura etc.)", "title": "O que devo informar no campo \"descri\u00e7\u00e3o\"?"}, "investment:transparency": {"body": "Para atender \u00e0 Lei de Acesso \u00e0 Informa\u00e7\u00e3o, informar os moradores locais sobre quais as empresas e investidores que est\u00e3o ajudando a comunidade ou a organiza\u00e7\u00e3o com recursos.", "title": "Por que a transpar\u00eancia das informa\u00e7\u00f5es sobre um investimento \u00e9 importante?"}, "home:cost": {"body": "N\u00e3o.  O MootiroMaps \u00e9 um software livre e gratuito. Voc\u00ea pode tanto criar uma conta ou tamb\u00e9m baixar o c\u00f3digo de nosso reposit\u00f3rio e instalar em seu servidor.", "title": "Preciso pagar para usar o MootiroMaps?"}, "organization:acronym": {"body": "Ao criar ou editar um cadastro \u00e9 importante usar a sigla e o nome da organiza\u00e7\u00e3o para facilitar a busca. Existem organiza\u00e7\u00f5es que s\u00e3o mais conhecidas por sua sigla. Exemplo: Instituto de Fomento \u00e0 Tecnologia do Terceiro Setor - IT3S.", "title": "Por que \u00e9 importante inserir a sigla junto ao nome da organiza\u00e7\u00e3o?"}, "user:delete": {"body": "Atualmente \u00e9 preciso solicitar ao administrador que sua conta seja apagada.", "title": "Posso apagar minha conta?"}, "community:related_info": {"body": "\u00c9 legal voc\u00ea inserir imagens que representam bem sua comunidade, tais como fotos de ruas principais, centros comunit\u00e1rios ou parques centrais etc. Se houver coloque refer\u00eancias que voc\u00ea usou.", "title": "Que tipo de arquivos ou links s\u00e3o importantes para inserir no cadastro?"}, "project:description": {"body": "Objetivos e finalidades do mapeamento, territ\u00f3rios de atua\u00e7\u00e3o, coordenadores, hist\u00f3rico, estrat\u00e9gias de pesquisa, resultados de pesquisa, fontes das informa\u00e7\u00f5es etc.", "title": "Que tipo de informa\u00e7\u00f5es devo adicionar ao campo \"descri\u00e7\u00e3o\"?"}, "resource:what_is": {"body": "S\u00e3o equipamentos e servi\u00e7os dispon\u00edveis no territ\u00f3rio, como pra\u00e7as, bibliotecas comunit\u00e1rias, programas voltados \u00e0 alfabetiza\u00e7\u00e3o, preven\u00e7\u00e3o de doen\u00e7as etc. O cadastro permite que a comunidade mensure a quantidade e qualidade desses recursos.", "title": "O que \u00e9 um \"recurso\" e por que cadastr\u00e1-lo?"}, "need:target_audience": {"body": "S\u00e3o os grupos de pessoas atingidos pelas necessidades ou que s\u00e3o potenciais para melhorar ou resolv\u00ea-las. Por exemplo, se a necessidade for uma creche, os p\u00fablicos-alvo s\u00e3o crian\u00e7as de 0 a 3 anos e suas m\u00e3es e pais.", "title": "O que s\u00e3o os p\u00fablicos-alvo?"}, "project:promote": {"body": "Para dar visibilidade ao projeto, mobilizar usu\u00e1rios colaboradores e a comunidade na resolu\u00e7\u00e3o das problem\u00e1ticas.", "title": "Por que promover o projeto?"}, "need:what_is": {"body": "Necessidade \u00e9 qualquer problema social, de maior ou menor complexidade, enfrentada em uma comunidade: desde buracos na rua at\u00e9 necessidade de a\u00e7\u00f5es de enfrentamento \u00e0 viol\u00eancia contra crian\u00e7as e adolescentes etc.", "title": "O que \u00e9 uma \"necessidade\"?"}, "user:policy": {"body": "Todos os dados inseridos por voc\u00ea em seu cadastro est\u00e3o p\u00fablicos na plataforma, exceto a senha e seu e-mail.", "title": "H\u00e1 uma pol\u00edtica de seguran\u00e7a dos dados?"}, "home:objects": {"body": "Objetos s\u00e3o comunidades, organiza\u00e7\u00f5es, necessidades, recursos e investimentos.", "title": "O que s\u00e3o os objetos no MootiroMaps?"}, "need:why": {"body": "Para moradores e atores sociais consigam compreender a dimens\u00e3o das problem\u00e1ticas existentes no territ\u00f3rio.", "title": "Por que cadastrar uma necessidade no MootiroMaps?"}, "map:addres_coordinate_search": {"body": "Voc\u00ea pode navegar at\u00e9 um local no mapa usando seu endere\u00e7o ou sua coordenada geogr\u00e1fica. Se for endere\u00e7o, insira no campo em branco informa\u00e7\u00f5es como rua, n\u00famero, distrito ou munic\u00edpio, CEP. Se preferir coordenadas, coloque a latitude e a longitude.  Depois clique em \"Ir\".", "title": "Como usar o campo de endere\u00e7o/coordendas?"}, "community:description": {"body": "Informa\u00e7\u00f5es como localiza\u00e7\u00e3o, infra-estrutura, hist\u00f3rico, popula\u00e7\u00e3o, perfil s\u00f3cio-econ\u00f4mico, economia, caracter\u00edsticas principais, fontes das informa\u00e7\u00f5es (site da prefeitura etc.)", "title": "O que devo escrever no campo da \"descri\u00e7\u00e3o\"?"}, "home:objects_edition": {"body": "O \u00edcone [[[tal]]] indica a edi\u00e7\u00e3o na p\u00e1gina de cada objeto cadastrado. Basta clicar, realizar a edi\u00e7\u00e3o e clicar no bot\u00e3o \"enviar\".", "title": "Como edito as informa\u00e7\u00f5es nos cadastros dos objetos no MootiroMaps?"}, "map:layers": {"body": "O bot\u00e3o \"Camadas\" \u00e9 utilizado para escolher e visualizar tipos espec\u00edficos de objetos no mapa, por exemplo, somente as organiza\u00e7\u00f5es, somente as comunidades, etc. ", "title": "O que s\u00e3o as \"Camadas\"?"}, "map:add": {"body": "Clicando no bot\u00e3o \"Adicionar\" o usu\u00e1rio pode mapear (adicionar) um objeto ao mapa.", "title": "O que significa \"Adicionar\"?"}, "organization:target_audience": {"body": "S\u00e3o grupos de pessoas atendidas pelas organiza\u00e7\u00f5es. Exemplo: crian\u00e7as (0-3), idosos, estudantes etc.", "title": "O que s\u00e3o os p\u00fablicos-alvo?"}, "organization:description": {"body": "Informa\u00e7\u00f5es como localiza\u00e7\u00e3o, tem\u00e1tica de atua\u00e7\u00e3o, servi\u00e7os oferecidos, hist\u00f3rico, participa\u00e7\u00f5es em redes e alian\u00e7as, parceiros, CNPJ, financiamento, gestores, fontes das informa\u00e7\u00f5es etc.", "title": "Que tipo de informa\u00e7\u00f5es devo adicionar ao campo \"descri\u00e7\u00e3o\"?"}, "investment:description": {"body": "Nome e descri\u00e7\u00e3o do projeto, da necessidade que o investimento apoia, financiador, objetivos e resultados do investimento ou do projeto apoiado etc.", "title": "Que tipo de informa\u00e7\u00f5es devo adicionar ao campo \"descri\u00e7\u00e3o\"?"}, "resource:description": {"body": "Informa\u00e7\u00f5es como localiza\u00e7\u00e3o, tem\u00e1tica da atua\u00e7\u00e3o, servi\u00e7os oferecidos, organiza\u00e7\u00f5es conveniadas ou \u00f3rg\u00e3os superiores, financiamento, fontes das informa\u00e7\u00f5es etc.", "title": "Que tipo de informa\u00e7\u00f5es devo adicionar ao campo \"descri\u00e7\u00e3o\"?"}}

    tours_config:
        "home":
            "slides": [
                {
                "title": gettext "MootiroMaps"
                "body": gettext "Clique no logo do MootiroMaps e você será redirecionado para a página central."
                "selector": "#logo"
                },
                {
                "title": gettext "Login"
                "body": gettext "Para criar um perfil no MootiroMaps ou logar na plataforma, clique aqui."
                "selector": "#login_button"
                "options": "tipLocation:left;nubPosition:top-right;"
                "offsetX": -230
                },
                {
                "title": gettext "Página do usuário"
                "body": gettext "Clicando no nome de qualquer usuário você encontra informações sobre o usuário, contatos e últimas edições feitas."
                "selector": "#user_menu"
                "options": "tipLocation:left;nubPosition:top-right;"
                "offsetX": -90
                },
                {
                "title": gettext "Visualize o mapa"
                "body": gettext "Aqui você encontra no mapa os objetos já mapeados - no Brasil e no mundo!"
                "selector": "#menu .map"
                },
                {
                "title": gettext "Objetos cadastrados"
                "body": gettext "Escolha o tipo de objeto cadastrado e veja as listas correspondentes."
                "selector": "#menu .objects"
                },
                {
                "title": gettext "Projetos cadastrados"
                "body": gettext "Visualize a lista de projetos de mapeamento acontecendo no MootiroMaps."
                "selector": "#menu .projects"
                },
                {
                "title": gettext "Blog do IT3S"
                "body": gettext "Em nosso Blog postamos análises e opinões sobre transparência, mobilização social, georreferenciamento, tecnologias e colaboração. Clique, leia e comente."
                "selector": ".news .blog"
                "options": "tipLocation:left;"
                },
                {
                "title": gettext "Edições recentes"
                "body": gettext "Acompanhe as atualizações feitas pelos usuários do MootiroMaps. Os ícones mostram os tipos de objetos editados. Edite você também."
                "selector": ".news .last_updates"
                "options": "tipLocation:right;"
                },
            ]
        "map":
            "slides": [
                {
                "title": gettext "Localização do ponto"
                "body": gettext "Escolha entre endereço (insira rua, número, município ou insira o CEP) ou coordenada (latitude e longitude) para ser direcionado a um ponto no mapa."
                "selector": "#map-searchbox"
                },
                {
                "title": gettext "Filtrar por raio"
                "body": gettext "Selecione um ponto no mapa e estabeleça a distância (raio) em que deseja que apareçam os objetos mapeados no território."
                "selector": "#map-panel-filter-tab"
                },
                {
                "title": gettext "Adicionar um objeto"
                "body": gettext 'Escolha o tipo de objeto que melhor se aplica ao que será mapeado e adicione ao mapa uma linha, um ponto ou uma área. Conclua o mapeamento pressionando o botão "avançar".'
                "selector": "#map-panel-add-tab"
                },
                {
                "title": gettext "Filtrar por camada"
                "body": gettext "Ligue ou desligue as camada para filtrar os objetos a serem apresentados no mapa."
                "selector": "#map-panel-layers-tab"
                },
            ]

        "community_list":
            "slides": [
                {
                "title": gettext "Lista de comunidades"
                "body": gettext "Aqui estão listadas  com uma curta descrição todas as comunidades cadastradas no MootiroMaps. Clique no nome da comunidade para acessar o cadastro completo."
                "selector": "div.view-list-item > h4 > span > a"
                },
                {
                "title": gettext "Ponto no mapa"
                "body": gettext "Clique para visualizar previamente o objeto no mapa."
                "selector": "div.view-list-item > h4 > a.list-map-preview"
                "options": "tipLocation:right;"
                "offsetY": -20
                },
                {
                "title": gettext "Visualização e filtragem"
                "body": gettext "Você pode escolher como deseja visualizar a listagem: por ordem alfabética ou data de cadastro. Também pode filtrar por palavras-chave."
                "selector": "div.view-list-visualization-header i"
                "options": "tipLocation:right;"
                "offsetX": 20
                "offsetY": -28
                },
            ]

        "organization_list":
            "slides": [
                {
                "title": gettext "Lista de organizações"
                "body": gettext "Aqui estão listadas com uma curta descrição todas as organizações cadastradas no MootiroMaps. Clique no nome da organização para acessar o cadastro completo."
                "selector": "div.view-list-item a.org-list-name"
                },
                {
                "title": gettext "Visualização e filtragem"
                "body": gettext "Você pode escolher como deseja visualizar a listagem: por ordem alfabética ou data de cadastro. Também pode filtrar por palavras-chave."
                "selector": "div.view-list-visualization-header i"
                "options": "tipLocation:right;"
                "offsetX": 20
                "offsetY": -28
                },
                {
                "title": gettext "Adicionar uma organização"
                "body": gettext "Clique aqui e cadastre no MootiroMaps uma nova organização."
                "selector": "div.button-new"
                },
            ]

        "need_list":
            "slides": [
                {
                "title": gettext "Lista de necessidades"
                "body": gettext "Aqui estão listadas com uma curta descrição todas as necessidades cadastradas no MootiroMaps. Clique no nome da necessidade para acessar o cadastro completo."
                "selector": "div.view-list-item > h4 > span > a"
                },
                {
                "title": gettext "Ponto no mapa"
                "body": gettext "Clique para visualizar previamente o objeto no mapa."
                "selector": "div.view-list-item > h4 > a.list-map-preview"
                "options": "tipLocation:right;"
                "offsetY": -20
                },
                {
                "title": gettext "Visualização e filtragem"
                "body": gettext "Você pode escolher como deseja visualizar a listagem: por ordem alfabética ou data de cadastro. Também pode filtrar por palavras-chave."
                "selector": "div.view-list-visualization-header i"
                "options": "tipLocation:right;"
                "offsetX": 20
                "offsetY": -28
                },
                {
                "title": gettext "Adicionar uma necessidade"
                "body": gettext "Clique aqui e cadastre no MootiroMaps uma nova necessidade."
                "selector": "div.button-new"
                },
            ]

        "resource_list":
            "slides": [
                {
                "title": gettext "Lista de recursos"
                "body": gettext "Aqui estão listados com uma curta descrição todos os recursos cadastrados no MootiroMaps. Clique no nome do recurso para acessar o cadastro completo."
                "selector": "div.view-list-item > h4 > span > a"
                },
                {
                "title": gettext "Ponto no mapa"
                "body": gettext "Clique aqui para visualizar previamente o objeto desejado no mapa."
                "selector": "div.view-list-item > h4 > a.list-map-preview"
                "options": "tipLocation:right;"
                "offsetY": -20
                },
                {
                "title": gettext "Visualização e filtragem"
                "body": gettext "Você pode escolher como deseja visualizar a listagem: por ordem alfabética ou data de cadastro. Também pode filtrar por palavras-chave."
                "selector": "div.view-list-visualization-header i"
                "options": "tipLocation:right;"
                "offsetX": 20
                "offsetY": -28
                },
                {
                "title": gettext "Adicionar um recurso"
                "body": gettext "Clique aqui e cadastre no MootiroMaps um novo recurso."
                "selector": "div.button-new"
                },
            ]

        "investment_list":
            "slides": [
                {
                "title": gettext "Lista de investimentos"
                "body": gettext "Aqui estão listados  com uma curta descrição todos os investimentos cadastrados no MootiroMaps. Clique no nome do investimentos para acessar o cadastro completo."
                "selector": "div.view-list-item > h4 > span > a"
                },
                {
                "title": gettext "Ponto no mapa"
                "body": gettext "Clique aqui para visualizar previamente o objeto no mapa."
                "selector": "div.view-list-item > h4 > a.list-map-preview"
                "options": "tipLocation:right;"
                "offsetY": -20
                },
                {
                "title": gettext "Visualização e filtragem"
                "body": gettext "Você pode escolher como deseja visualizar a listagem: por ordem alfabética ou data de cadastro. Também pode filtrar por palavras-chave."
                "selector": "div.view-list-visualization-header"
                "options": "tipLocation:right;"
                "offsetX": 20
                },
            ]

        "project_list":
            "slides": [
                {
                "title": gettext "Lista de projetos"
                "body": gettext "Aqui estão listados com uma curta descrição todos os projetos cadastrados no MootiroMaps. Clique no nome do projetos para acessar o cadastro completo."
                "selector": "div.view-list-item span > a"
                },
                {
                "title": gettext "Visualização e filtragem"
                "body": gettext "Você pode filtrar a busca por palavras-chave."
                "selector": "div.view-list-visualization-header i"
                "options": "tipLocation:right;"
                "offsetX": 20
                "offsetY": -28
                },
                {
                "title": gettext "Adicionar um projeto"
                "body": gettext "Clique aqui e comece um novo projeto de mapeamento no MootiroMaps."
                "selector": "div.button-new"
                },
            ]

        "community_show":
            "slides": [
                {
                "title": gettext "Título da comunidade"
                "body": gettext "Este é o nome com o qual o território foi cadastrado."
                "selector": ".main-column h2.title"
                },
                {
                "title": gettext "Edição do conteúdo"
                "body": gettext "Para editar conteúdos clique no lápis."
                "selector": "div.view-edit-btn"
                "options": "tipLocation:bottom;nubPosition:top-right;"
                "offsetX": -135
                },
                {
                "title": gettext "Perfil da comunidade"
                "body": gettext "Esse local contém a descrição da comunidade, como a localização, histórico, perfil socioeconômico da população etc."
                "selector": ".main-column .mark-down"
                "options": "tipLocation:left;"
                },
                {
                "title": gettext "No mapa"
                "body": gettext "Clique aqui se você quiser visualizar a comunidade em um mapa maior."
                "selector": "#map-preview"
                "options": "tipLocation:left;"
                },
                {
                "title": gettext "Comunidades próximas"
                "body": gettext "O campo mostra outras comunidades cadastradas no MootiroMaps que estão próximas a esta."
                "selector": ".right-bar .nearby-communities"
                "options": "tipLocation:left;"
                },
                {
                "title": gettext "Seguir"
                "body": gettext 'Clicando no botão "seguir" você assina as atualizações do conteúdo e recebe atualizações sempre que ele for alterado.'
                "selector": ".view-follow-btns"
                "options": ""
                },
                {
                "title": gettext "Comentar"
                "body": gettext "O que você acha desse local? Qual a sua opinião? Deixe um comentário na página."
                "selector": "#divFormComment"
                "options": "tipLocation:bottom;"
                },
                {
                "title": gettext "Redes sociais"
                "body": gettext "Gostou do conteúdo dessa página? Divulgue-a nas redes sociais."
                "selector": ".fb-like"
                "options": "tipLocation:bottom;"
                },
            ]

        "organization_show":
            "slides": [
                {
                "title": gettext "Título da organização"
                "body": gettext "Este é o nome com o qual a organização foi cadastrada."
                "selector": ".organization-header"
                },
                {
                "title": gettext "Edição do conteúdo"
                "body": gettext "Para editar conteúdos clique no lápis."
                "selector": "div.view-edit-btn"
                "options": "tipLocation:bottom;nubPosition:top-right;"
                "offsetX": -135
                },
                {
                "title": gettext "Descrição da organização"
                "body": gettext "Esse local contém a descrição da organização, como temática de atuação, objetivos, projetos e serviços, parceiros, financiadores etc."
                "selector": ".main-column .mark-down"
                "options": "tipLocation:left;"
                },
                {
                "title": gettext "No mapa"
                "body": gettext "Clique aqui se você quiser visualizar a organização em um mapa maior."
                "selector": "#map-preview"
                "options": "tipLocation:left;"
                },
                {
                "title": gettext "Projetos"
                "body": gettext "O campo apresenta a quais projetos de mapeamento esta organização está relacionada."
                "selector": ".projects-tag-header"
                "options": "tipLocation:left;"
                },
                {
                "title": gettext "Seguir"
                "body": gettext 'Clicando no botão "seguir" você assina as atualizações do conteúdo e recebe atualizações sempre que ele for alterado.'
                "selector": ".view-follow-btns"
                "options": ""
                },
                {
                "title": gettext "Comentar"
                "body": gettext "O que você acha desse local? Qual a sua opinião? Deixe um comentário na página."
                "selector": "#divFormComment"
                "options": "tipLocation:bottom;"
                },
                {
                "title": gettext "Redes sociais"
                "body": gettext "Gostou da organização? Divulgue-a nas redes sociais."
                "selector": ".fb-like"
                "options": "tipLocation:bottom;"
                },
            ]

        "need_show":
            "slides": [
                {
                "title": gettext "Título da necessidade"
                "body": gettext "Este é o nome com o qual a necessidade foi cadastrada."
                "selector": ".need-title"
                },
                {
                "title": gettext "Edição do conteúdo"
                "body": gettext "Para editar conteúdos clique no lápis."
                "selector": "div.view-edit-btn"
                "options": "tipLocation:bottom;nubPosition:top-right;"
                "offsetX": -135
                },
                {
                "title": gettext "Descrição da necessidade"
                "body": gettext "Esse local contém a descrição da necessidade e permite que os usuários consigam compreender a natureza da problemática."
                "selector": ".main-column .mark-down"
                "options": "tipLocation:right;"
                },
                {
                "title": gettext "No mapa"
                "body": gettext "Clique aqui se você quiser visualizar a necessidade em um mapa maior."
                "selector": "#map-preview"
                "options": "tipLocation:left;"
                },
                {
                "title": gettext "Proposta de resolução"
                "body": gettext "Neste campo é possível inserir novas propostas de resolução da necessidade."
                "selector": ".need-proposals"
                "options": "tipLocation:left;"
                },
                {
                "title": gettext "Necessidades semelhantes"
                "body": gettext "O MootiroMaps relaciona necessidades semelhantes ou próximas para facilitar que os usuários troquem experiências e discutam como resolvê-las."
                "selector": "#related-needs"
                "options": "tipLocation:left;"
                },
                {
                "title": gettext "Seguir"
                "body": gettext 'Clicando no botão "seguir" você assina as atualizações do conteúdo e recebe atualizações sempre que ele for alterado.'
                "selector": ".view-follow-btns"
                "options": ""
                },
                {
                "title": gettext "Comentar"
                "body": gettext "O que você acha desse local? Qual a sua opinião? Deixe um comentário na página."
                "selector": "#divFormComment"
                "options": "tipLocation:bottom;"
                },
                {
                "title": gettext "Redes sociais"
                "body": gettext "Achou importante a necessidade? Divulgue-a nas redes sociais."
                "selector": ".fb-like"
                "options": "tipLocation:bottom;"
                },
            ]

        "resource_show":
            "slides": [
                {
                "title": gettext "Título do recurso"
                "body": gettext "Este é o nome com o qual o recurso foi cadastrado."
                "selector": "h2.title"
                },
                {
                "title": gettext "Edição do conteúdo"
                "body": gettext "Para editar conteúdos clique no lápis."
                "selector": "div.view-edit-btn"
                "options": "tipLocation:bottom;nubPosition:top-right;"
                "offsetX": -135
                },
                {
                "title": gettext "Descrição do recurso"
                "body": gettext "Esse local contém a descrição do recurso, como localização, horários de atendimento, temática, projetos e serviços etc."
                "selector": ".main-column .mark-down"
                "options": "tipLocation:right;"
                },
                {
                "title": gettext "No mapa"
                "body": gettext "Clique aqui se você quiser visualizar o recurso em um mapa maior."
                "selector": "#map-preview"
                "options": "tipLocation:left;"
                },
                {
                "title": gettext "Recursos semelhantes"
                "body": gettext "O campo permite que os usuários identifiquem recursos semelhantes ou próximos."
                "selector": ".related-resource"
                "options": "tipLocation:left;"
                "offsetX": -10
                "offsetY": -25
                },
                {
                "title": gettext "Seguir"
                "body": gettext 'Clicando no botão "seguir" você assina as atualizações do conteúdo e recebe atualizações sempre que ele for alterado.'
                "selector": ".view-follow-btns"
                "options": ""
                },
                {
                "title": gettext "Comentar"
                "body": gettext "O que você acha desse local? Qual a sua opinião? Deixe um comentário na página."
                "selector": "#divFormComment"
                "options": "tipLocation:bottom;"
                },
                {
                "title": gettext "Redes sociais"
                "body": gettext "Gostou da página? Divulgue-a nas redes sociais."
                "selector": ".fb-like"
                "options": "tipLocation:bottom;"
                },
            ]

        "investment_show":
            "slides": [
                {
                "title": gettext "Título do investimento"
                "body": gettext "Este é o nome com o qual o investimento foi cadastrado."
                "selector": "h2.title"
                },
                {
                "title": gettext "Edição do conteúdo"
                "body": gettext "Para editar conteúdos clique no lápis."
                "selector": "div.view-edit-btn"
                "options": "tipLocation:bottom;nubPosition:top-right;"
                "offsetX": -135
                },
                {
                "title": gettext "Descrição do investimento"
                "body": gettext "O preenchimento deste campo mostra a descrição do investimento, como o objetivo, localização, temática, público-alvo etc."
                "selector": ".main-column .mark-down"
                "options": "tipLocation:right;"
                },
                {
                "title": gettext "Seguir"
                "body": gettext 'Clicando no botão "seguir" você assina as atualizações do conteúdo e recebe atualizações sempre que ele for alterado.'
                "selector": ".view-follow-btns"
                "options": ""
                },
                {
                "title": gettext "Comentar"
                "body": gettext "O que você acha desse investimento? Qual a sua opinião? Deixe um comentário na página."
                "selector": "#divFormComment"
                "options": "tipLocation:bottom;"
                },
                {
                "title": gettext "Redes sociais"
                "body": gettext "Achou importante essa informação? Divulgue-a nas redes sociais."
                "selector": ".fb-like"
                "options": "tipLocation:bottom;"
                },
            ]

        "project_show":
            "slides": [
                {
                "title": gettext "Título do projeto"
                "body": gettext "Este é o nome com o qual o projeto foi cadastrado."
                "selector": "h2.title"
                },
                {
                "title": gettext "Edição do conteúdo"
                "body": gettext "Para editar conteúdos clique no lápis."
                "selector": "div.view-edit-btn"
                "options": "tipLocation:bottom;nubPosition:top-right;"
                "offsetX": -135
                },
                {
                "title": gettext "Descrição do projeto"
                "body": gettext "Esse local contém a descrição do projeto, como o objetivo, localização, temática, público-alvo, apoiadores etc."
                "selector": ".main-column .mark-down"
                "options": "tipLocation:right;"
                },
                {
                "title": gettext "Objetos relacionados"
                "body": gettext "A listagem mostra objetos (organizações, recursos, necessidades etc) que foram cadastrados e relacionados a esse projeto."
                "selector": ".view-info-buttons"
                "options": "tipLocation:top;"
                "offsetX": 50
                },
                {
                "title": gettext "No mapa"
                "body": gettext "Clique aqui se você quiser visualizar todos os objetos relacionados ao projeto em um mapa maior."
                "selector": "#map-preview"
                "options": "tipLocation:left;"
                },
                {
                "title": gettext "Participantes"
                "body": gettext "O campo mostra o usuário administrador e os colaboradores."
                "selector": ".view-info-btn:last"
                },
                {
                "title": gettext "Seguir"
                "body": gettext 'Clicando no botão "seguir" você assina as atualizações do conteúdo e recebe atualizações sempre que ele for alterado.'
                "selector": ".view-follow-btns"
                "options": ""
                },
                {
                "title": gettext "Comentar"
                "body": gettext "O que você acha desse local? Qual a sua opinião? Deixe um comentário na página."
                "selector": "#divFormComment"
                "options": "tipLocation:bottom;"
                },
                {
                "title": gettext "Redes sociais"
                "body": gettext "Gostou do projeto? Divulgue-o nas redes sociais."
                "selector": ".fb-like"
                "options": "tipLocation:bottom;"
                },
            ]

window.HelpCenter = HelpCenter
