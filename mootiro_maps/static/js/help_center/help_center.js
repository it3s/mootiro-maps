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

  HelpCenter.prototype.tour_tpl = "        <!------------ PAGE TOUR ----------->        <ol id='joyride'>          <% for (var j = 0; j < tour.slides.length; j++) { %>          <li data-selector='<%= tour.slides[j].selector %>'            data-button='<% if (j != tour.slides.length-1) { print(gettext('Next')); } else { print(gettext('Finish')); } %>'            data-options='<%= tour.slides[j].options %>'            data-offsetX='<%= tour.slides[j].offsetX %>'            data-offsetY='<%= tour.slides[j].offsetY %>'          >            <h2><%= tour.slides[j].title %></h2>            <p><%= tour.slides[j].body %></p>          </li>          <% } %>        </ol>        <!--------------------------------->        ";

  HelpCenter.prototype.modal_tpl = "        <div id='help_center' class='modal hide fade'>          <div class='modal-header'>            <button type='button' class='close' data-dismiss='modal'>×</button>            <h2><%= gettext('Help Center') %></h2>          </div>          <section class='modal-body'>            <ul id='questions'>              <% for (var i = 0; i < questions.length; i++) { %>              <li class='<%= questions[i].type %>'>                <!------------ QUESTION ----------->                <article>                  <h3><%= questions[i].title %></h3>                  <p><%= questions[i].body %></p>                </article>                <!--------------------------------->              </li>              <% } %>            </ul>            <% if (hasTour) { %><button id='tour_button'><%= gettext('Take the guided tour') %></button><% } %>            <a id='help_center_about' href='/about/'><%= gettext('About') %></a>            <a id='help_center_usecases' href='/use_cases/'><%= gettext('Use Cases') %></a>          </section>        </div>        ";

  HelpCenter.prototype.modal_setup = function() {
    var html;
    html = _.template(this.modal_tpl, {
      questions: this.questions,
      hasTour: this.tour != null
    });
    this.$modal = $(html);
    this.$modal.modal({
      show: false
    });
    return $('body').append(this.$modal);
  };

  HelpCenter.prototype.tour_setup = function() {
    var html, modal_wrap;
    if (!(this.tour != null)) return;
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
    "home:others_edition": {
      "body": "Na p\u00e1gina de cada objeto cadastrado o bot\u00e3o \"Hist\u00f3rico\" apresenta informa\u00e7\u00f5es sobre a cria\u00e7\u00e3o e edi\u00e7\u00f5es recentes.",
      "title": "Como eu posso saber se outro usu\u00e1rio editou um cadastro?"
    },
    "community:what_is": {
      "body": "Comunidade pode ser uma rua, bairro, favela, cidade, aldeia ind\u00edgena etc., ou seja, um determinado territ\u00f3rio. Mapear uma comunidade \u00e9 o primeiro passo para o desenvolvimento local e permite que sejam realizados diagn\u00f3sticos territoriais.",
      "title": "O que \u00e9 uma \"comunidade\" e por que mape\u00e1-la?"
    },
    "user:name_edition": {
      "body": "Sim. Na p\u00e1gina do usu\u00e1rio clique no campo \"Nome\" e edite. Para tanto \u00e9 preciso estar logado.",
      "title": "Posso editar meu nome?"
    },
    "user:password": {
      "body": "N\u00e3o h\u00e1 limite de caracteres para a senha, mas quanto mais letras e n\u00fameros misturados mais segura ser\u00e1 sua senha.",
      "title": "Como deve ser a minha senha?"
    },
    "home:mootiro_maps": {
      "body": "\u00c9 uma plataforma de mapeamento colaborativo de comunidades, suas organiza\u00e7\u00f5es, recursos e necessidades voltada para o desenvolvimento comunit\u00e1rio.",
      "title": "O que \u00e9 o MootiroMaps?"
    },
    "user:data": {
      "body": "O MootiroMaps tem como um de seus objetivos conectar mapeadores possibilitando que troquem experi\u00eancias, conhe\u00e7am outros projetos e colaborem entre si. Informa\u00e7\u00f5es de contato e de localiza\u00e7\u00e3o s\u00e3o importantes para que outros usu\u00e1rios possam entrar em contato com voc\u00ea.",
      "title": "Por que informar meus dados?"
    },
    "community:geometry_edition": {
      "body": "Sim! Para voc\u00ea editar os pontos no mapa de uma comunidade, abra o cadastro da comunidade. L\u00e1, clique no bot\u00e3o \"editar\" (l\u00e1pis). Dentro do cadastro voc\u00ea encontrar\u00e1 uma op\u00e7\u00e3o para abrir o editor de mapas. Arraste os pontos e salve sua edi\u00e7\u00e3o.",
      "title": "Posso editar os pontos no mapa de uma comunidade?"
    },
    "need:proposal": {
      "body": "Para que os usu\u00e1rios, principalmente os moradores daquela regi\u00e3o, possam juntos debater as necessidades e como resolv\u00ea-las.",
      "title": "Para que servem as propostas?"
    },
    "need:discuss": {
      "body": "Basta clicar no bot\u00e3o [[[tal]]] e inserir sua opini\u00e3o e reflex\u00e3o sobre a necessidade.",
      "title": "Como discutir uma necessidade?"
    },
    "investment:what_is": {
      "body": "Trata-se de um investimento social que envolve ou n\u00e3o dinheiro, feito por empresas, funda\u00e7\u00f5es, pessoas f\u00edsicas. O cadastro \u00e9 fundamental para gerar transpar\u00eancia e apresentar a rela\u00e7\u00e3o entre investidores e organiza\u00e7\u00f5es que receberam o investimento.",
      "title": "O que \u00e9 um \"investimento\" e por que cadastr\u00e1-lo?"
    },
    "map:radius_search": {
      "body": "Usando essa ferramenta \u00e9 poss\u00edvel escolher um ponto central no mapa e estabelecer o raio de dist\u00e2ncia em que voc\u00ea deseja visualizar os objetos mapeados. Trata-se de um modo pr\u00e1tico para o diagn\u00f3stico territorial.",
      "title": "O que significa a \"Busca por raio\"?"
    },
    "project:what_is": {
      "body": "Projetos s\u00e3o a\u00e7\u00f5es de mapeamento que est\u00e3o acontecendo no MootiroMaps. Dentro do projeto podem ser reaproveitados todos os objetos e informa\u00e7\u00f5es j\u00e1 criados no mapa.",
      "title": "O que \u00e9 um \"projeto\" e por que cadastr\u00e1-lo?"
    },
    "home:search": {
      "body": "A principal ferramenta de busca est\u00e1 localizada no cabe\u00e7alho do MootiroMaps, onde podem ser inseridos endere\u00e7os ou nomes de organiza\u00e7\u00f5es, comunidades etc. \u00c9 poss\u00edvel tamb\u00e9m acessar no menu superior a p\u00e1gina de cada tipo de objeto e inserir palavras-chaves no campo \"Op\u00e7\u00f5es de Visualiza\u00e7\u00e3o e Filtragem\" para uma busca mais espec\u00edfica nas listas.",
      "title": "Como posso buscar um objeto no MootiroMaps?"
    },
    "resource:acronym": {
      "body": "Ao criar ou editar um cadastro \u00e9 importante usar sigla e nome do recurso para facilitar a busca. Existem recursos que s\u00e3o mais conhecidas pela sua sigla. Exemplo: Centro da Juventude - CJ.",
      "title": "Por que \u00e9 importante inserir a sigla junto ao nome do recurso?"
    },
    "organization:transparency": {
      "body": "Para atender ativamente a Lei de Acesso \u00e0 Informa\u00e7\u00e3o (Lei 12.527) e permitir que os cidad\u00e3os acessem com facilidade informa\u00e7\u00f5es como CNPJ, financiamento, parceiros etc.",
      "title": "Por que a transpar\u00eancia das informa\u00e7\u00f5es sobre uma organiza\u00e7\u00e3o \u00e9 importante?"
    },
    "home:denounce_content": {
      "body": "Sim. Ao final da p\u00e1gina de cada objeto cadastrado o bot\u00e3o \"Denunciar\" permite que o usu\u00e1rio registre sua den\u00fancia.",
      "title": "Eu posso denunciar um cadastro?"
    },
    "project:batch_upload": {
      "body": "A importa\u00e7\u00e3o de dados \u00e9 importante, para disponibilizar no mapa informa\u00e7\u00f5es que voc\u00ea j\u00e1 coletou ou tem dispon\u00edvel em planilhas. Para adicionar dados em lote, voc\u00ea deve clicar no bot\u00e3o \"importar dados\" e criar uma nova planilha de importa\u00e7\u00e3o.",
      "title": "Por que e como adicionar dados em lote?"
    },
    "home:who_can_use": {
      "body": "Qualquer pessoa ou organiza\u00e7\u00e3o pode navegar e utilizar a plataforma.",
      "title": "Quem pode usar o MootiroMaps?"
    },
    "user:name": {
      "body": "Voc\u00ea pode escolher qualquer nome, mas preferimos que use seu primeiro nome e sobrenome.",
      "title": "Como deve ser o meu nome?"
    },
    "need:name": {
      "body": "O t\u00edtulo deve descrever, de forma precisa e atrav\u00e9s de palavras-chaves, do que se trata a necessidade. Exemplos: \"buraco na rua\", \"falta de computador\", \"constru\u00e7\u00e3o de escola\" etc.",
      "title": "O t\u00edtulo da necessidade deve conter quais informa\u00e7\u00f5es?"
    },
    "resource:difference_organization": {
      "body": "Organiza\u00e7\u00e3o \u00e9 uma entidade que normalmente apresenta estrutura f\u00edsica, CNPJ, colaboradores. Recurso pode ser entendido como o projeto desenvolvido por uma organiza\u00e7\u00e3o, equipamentos, materiais ou espa\u00e7os existentes na comunidade ou como um grupo de pessoas (coletivo) promovendo o desenvolvimento comunit\u00e1rio.",
      "title": "Qual \u00e9 a diferen\u00e7a entre um recurso e uma organiza\u00e7\u00e3o?"
    },
    "organization:what_is": {
      "body": "S\u00e3o ONGs, associa\u00e7\u00f5es de bairro, entidades em geral que atuam no Terceiro Setor, empresas, prefeituras. O cadastro ajuda a gerar visibilidade e a criar rela\u00e7\u00e3o com outras ONGs, al\u00e9m de associar recursos, necessidades, investimentos etc.",
      "title": "O que \u00e9 uma \"organiza\u00e7\u00e3o\" e por que cadastr\u00e1-la?"
    },
    "need:description": {
      "body": "A descri\u00e7\u00e3o deve explicar do melhor modo poss\u00edvel a situa\u00e7\u00e3o da necessidade: sua localiza\u00e7\u00e3o, materiais ou recursos \u00fateis para resolv\u00ea-la, se uma pessoa ou organiza\u00e7\u00e3o j\u00e1 est\u00e1 cuidando disso etc.",
      "title": "O que devo inserir no campo \"descri\u00e7\u00e3o\"?"
    },
    "need:categories": {
      "body": "Classificar as \u00e1reas facilita a busca mais espec\u00edfica na p\u00e1gina das necessidades. Al\u00e9m disso, \u00e9 \u00fatil para os investidores escolherem a \u00e1rea onde desejam aplicar seus recursos. ",
      "title": "O que s\u00e3o as \"\u00e1reas\" e para que servem?"
    },
    "home:collaborative_mapping": {
      "body": "Com o mapeamento moradores e organiza\u00e7\u00f5es sociais - atuando colaborativamente - georreferenciam situa\u00e7\u00f5es de vulnerabilidade em suas comunidades, geram de forma aut\u00f4noma indicadores e buscam mudan\u00e7as para as realidades locais propondo solu\u00e7\u00f5es.",
      "title": "O que significa \"mapeamento colaborativo\"?"
    },
    "investment:name": {
      "body": "Deve ser inserido o nome do projeto apoioda pelo investimento.",
      "title": "O que devo inserir no campo \"T\u00edtulo\"?"
    },
    "user:location": {
      "body": "Para possibilitar que outros mapeadores que atuam ou moram perto de voc\u00ea conhe\u00e7am sua localiza\u00e7\u00e3o e possam entrar em contato.",
      "title": "Por que informar minha localiza\u00e7\u00e3o? "
    },
    "community:search_data": {
      "body": "Em sites como o do IBGE (http://www.ibge.gov.br/) ou da prefeitura/subprefeitura de sua cidade.",
      "title": "Como posso encontrar dados sobre a comunidade?"
    },
    "user:public_contact": {
      "body": "S\u00e3o informa\u00e7\u00f5es como email, Skype, contas de redes sociais, por onde outros usu\u00e1rios poder\u00e3o entrar em contato com voc\u00ea.",
      "title": "O que significa o contato p\u00fablico?"
    },
    "community:description (copy)": {
      "body": "Informa\u00e7\u00f5es como localiza\u00e7\u00e3o, infra-estrutura, hist\u00f3rico, popula\u00e7\u00e3o, perfil s\u00f3cio-econ\u00f4mico, economia, caracter\u00edsticas principais, fontes das informa\u00e7\u00f5es (site da prefeitura etc.)",
      "title": "O que devo informar no campo \"descri\u00e7\u00e3o\"?"
    },
    "investment:transparency": {
      "body": "Para atender \u00e0 Lei de Acesso \u00e0 Informa\u00e7\u00e3o, informar os moradores locais sobre quais as empresas e investidores que est\u00e3o ajudando a comunidade ou a organiza\u00e7\u00e3o com recursos.",
      "title": "Por que a transpar\u00eancia das informa\u00e7\u00f5es sobre um investimento \u00e9 importante?"
    },
    "home:cost": {
      "body": "N\u00e3o.  O MootiroMaps \u00e9 um software livre e gratuito. Voc\u00ea pode tanto criar uma conta ou tamb\u00e9m baixar o c\u00f3digo de nosso reposit\u00f3rio e instalar em seu servidor.",
      "title": "Preciso pagar para usar o MootiroMaps?"
    },
    "organization:acronym": {
      "body": "Ao criar ou editar um cadastro \u00e9 importante usar a sigla e o nome da organiza\u00e7\u00e3o para facilitar a busca. Existem organiza\u00e7\u00f5es que s\u00e3o mais conhecidas por sua sigla. Exemplo: Instituto de Fomento \u00e0 Tecnologia do Terceiro Setor - IT3S.",
      "title": "Por que \u00e9 importante inserir a sigla junto ao nome da organiza\u00e7\u00e3o?"
    },
    "user:delete": {
      "body": "Atualmente \u00e9 preciso solicitar ao administrador que sua conta seja apagada.",
      "title": "Posso apagar minha conta?"
    },
    "community:related_info": {
      "body": "\u00c9 legal voc\u00ea inserir imagens que representam bem sua comunidade, tais como fotos de ruas principais, centros comunit\u00e1rios ou parques centrais etc. Se houver coloque refer\u00eancias que voc\u00ea usou.",
      "title": "Que tipo de arquivos ou links s\u00e3o importantes para inserir no cadastro?"
    },
    "project:description": {
      "body": "Objetivos e finalidades do mapeamento, territ\u00f3rios de atua\u00e7\u00e3o, coordenadores, hist\u00f3rico, estrat\u00e9gias de pesquisa, resultados de pesquisa, fontes das informa\u00e7\u00f5es etc.",
      "title": "Que tipo de informa\u00e7\u00f5es devo adicionar ao campo \"descri\u00e7\u00e3o\"?"
    },
    "resource:what_is": {
      "body": "S\u00e3o equipamentos e servi\u00e7os dispon\u00edveis no territ\u00f3rio, como pra\u00e7as, bibliotecas comunit\u00e1rias, programas voltados \u00e0 alfabetiza\u00e7\u00e3o, preven\u00e7\u00e3o de doen\u00e7as etc. O cadastro permite que a comunidade mensure a quantidade e qualidade desses recursos.",
      "title": "O que \u00e9 um \"recurso\" e por que cadastr\u00e1-lo?"
    },
    "need:target_audience": {
      "body": "S\u00e3o os grupos de pessoas atingidos pelas necessidades ou que s\u00e3o potenciais para melhorar ou resolv\u00ea-las. Por exemplo, se a necessidade for uma creche, os p\u00fablicos-alvo s\u00e3o crian\u00e7as de 0 a 3 anos e suas m\u00e3es e pais.",
      "title": "O que s\u00e3o os p\u00fablicos-alvo?"
    },
    "project:promote": {
      "body": "Para dar visibilidade ao projeto, mobilizar usu\u00e1rios colaboradores e a comunidade na resolu\u00e7\u00e3o das problem\u00e1ticas.",
      "title": "Por que promover o projeto?"
    },
    "need:what_is": {
      "body": "Necessidade \u00e9 qualquer problema social, de maior ou menor complexidade, enfrentada em uma comunidade: desde buracos na rua at\u00e9 necessidade de a\u00e7\u00f5es de enfrentamento \u00e0 viol\u00eancia contra crian\u00e7as e adolescentes etc.",
      "title": "O que \u00e9 uma \"necessidade\"?"
    },
    "user:policy": {
      "body": "Todos os dados inseridos por voc\u00ea em seu cadastro est\u00e3o p\u00fablicos na plataforma, exceto a senha e seu e-mail.",
      "title": "H\u00e1 uma pol\u00edtica de seguran\u00e7a dos dados?"
    },
    "home:objects": {
      "body": "Objetos s\u00e3o comunidades, organiza\u00e7\u00f5es, necessidades, recursos e investimentos.",
      "title": "O que s\u00e3o os objetos no MootiroMaps?"
    },
    "need:why": {
      "body": "Para moradores e atores sociais consigam compreender a dimens\u00e3o das problem\u00e1ticas existentes no territ\u00f3rio.",
      "title": "Por que cadastrar uma necessidade no MootiroMaps?"
    },
    "map:addres_coordinate_search": {
      "body": "Voc\u00ea pode navegar at\u00e9 um local no mapa usando seu endere\u00e7o ou sua coordenada geogr\u00e1fica. Se for endere\u00e7o, insira no campo em branco informa\u00e7\u00f5es como rua, n\u00famero, distrito ou munic\u00edpio, CEP. Se preferir coordenadas, coloque a latitude e a longitude.  Depois clique em \"Ir\".",
      "title": "Como usar o campo de endere\u00e7o/coordendas?"
    },
    "community:description": {
      "body": "Informa\u00e7\u00f5es como localiza\u00e7\u00e3o, infra-estrutura, hist\u00f3rico, popula\u00e7\u00e3o, perfil s\u00f3cio-econ\u00f4mico, economia, caracter\u00edsticas principais, fontes das informa\u00e7\u00f5es (site da prefeitura etc.)",
      "title": "O que devo escrever no campo da \"descri\u00e7\u00e3o\"?"
    },
    "home:objects_edition": {
      "body": "O \u00edcone [[[tal]]] indica a edi\u00e7\u00e3o na p\u00e1gina de cada objeto cadastrado. Basta clicar, realizar a edi\u00e7\u00e3o e clicar no bot\u00e3o \"enviar\".",
      "title": "Como edito as informa\u00e7\u00f5es nos cadastros dos objetos no MootiroMaps?"
    },
    "map:layers": {
      "body": "O bot\u00e3o \"Camadas\" \u00e9 utilizado para escolher e visualizar tipos espec\u00edficos de objetos no mapa, por exemplo, somente as organiza\u00e7\u00f5es, somente as comunidades, etc. ",
      "title": "O que s\u00e3o as \"Camadas\"?"
    },
    "map:add": {
      "body": "Clicando no bot\u00e3o \"Adicionar\" o usu\u00e1rio pode mapear (adicionar) um objeto ao mapa.",
      "title": "O que significa \"Adicionar\"?"
    },
    "organization:target_audience": {
      "body": "S\u00e3o grupos de pessoas atendidas pelas organiza\u00e7\u00f5es. Exemplo: crian\u00e7as (0-3), idosos, estudantes etc.",
      "title": "O que s\u00e3o os p\u00fablicos-alvo?"
    },
    "organization:description": {
      "body": "Informa\u00e7\u00f5es como localiza\u00e7\u00e3o, tem\u00e1tica de atua\u00e7\u00e3o, servi\u00e7os oferecidos, hist\u00f3rico, participa\u00e7\u00f5es em redes e alian\u00e7as, parceiros, CNPJ, financiamento, gestores, fontes das informa\u00e7\u00f5es etc.",
      "title": "Que tipo de informa\u00e7\u00f5es devo adicionar ao campo \"descri\u00e7\u00e3o\"?"
    },
    "investment:description": {
      "body": "Nome e descri\u00e7\u00e3o do projeto, da necessidade que o investimento apoia, financiador, objetivos e resultados do investimento ou do projeto apoiado etc.",
      "title": "Que tipo de informa\u00e7\u00f5es devo adicionar ao campo \"descri\u00e7\u00e3o\"?"
    },
    "resource:description": {
      "body": "Informa\u00e7\u00f5es como localiza\u00e7\u00e3o, tem\u00e1tica da atua\u00e7\u00e3o, servi\u00e7os oferecidos, organiza\u00e7\u00f5es conveniadas ou \u00f3rg\u00e3os superiores, financiamento, fontes das informa\u00e7\u00f5es etc.",
      "title": "Que tipo de informa\u00e7\u00f5es devo adicionar ao campo \"descri\u00e7\u00e3o\"?"
    }
  };

  HelpCenter.prototype.tours_config = {
    "home": {
      "slides": [
        {
          "title": gettext("MootiroMaps"),
          "body": gettext("Click on MootiroMaps logo and you will be redirected to the front page."),
          "selector": "#logo"
        }, {
          "title": gettext("Login"),
          "body": gettext("In order to create a profile on MootiroMaps or log to the application, click here."),
          "selector": "#login_button",
          "options": "tipLocation:left;nubPosition:top-right;",
          "offsetX": -230
        }, {
          "title": gettext("User page"),
          "body": gettext("Clicking on a user's name you will be redirected to the respective user page, where you can find contact data and contributions to MootiroMap made by this user."),
          "selector": "#user_menu",
          "options": "tipLocation:left;nubPosition:top-right;",
          "offsetX": -90
        }, {
          "title": gettext("Search the map"),
          "body": gettext("Here you can find data about contents that have been already mapped - in Brazil and in the world!"),
          "selector": "#menu .map"
        }, {
          "title": gettext("Mapped items"),
          "body": gettext("Select one of the content types in order to get a list of corresponding items that have been mapped."),
          "selector": "#menu .objects"
        }, {
          "title": gettext("Mapping projects"),
          "body": gettext("Content can be associated to mapping projects. Click here to get to know our projects and start your own one."),
          "selector": "#menu .projects"
        }, {
          "title": gettext("Read more"),
          "body": gettext("On our blog we post analyses and opinions about transparency, participation on the map, geocoding, collaborative technologies and new feature releases. Click, read and comment."),
          "selector": ".news .blog",
          "options": "tipLocation:left;"
        }, {
          "title": gettext("Stay tuned"),
          "body": gettext("Learn more about recent editions and new data that was created. Icons show the type of content and edition. Take part as well and contribute to MootiroMaps."),
          "selector": ".news .last_updates",
          "options": "tipLocation:right;"
        }
      ]
    },
    "map": {
      "slides": [
        {
          "title": gettext("Find a location on the map"),
          "body": gettext("Insert an address (street address, city, zip-code) or GPS coordinates (latitude and longitude)! We will get you to this place on the map."),
          "selector": "#map-searchbox"
        }, {
          "title": gettext("See what is close"),
          "body": gettext("Please select a point on the map in order to filter mapped content in a specific distance from this location."),
          "selector": "#map-panel-filter-tab"
        }, {
          "title": gettext("Become a mapper"),
          "body": gettext('Select the content type that is most appropriate for your object and add a line, a point or a shape to the map. Finish the mapping by clicking \"Next step\".'),
          "selector": "#map-panel-add-tab"
        }, {
          "title": gettext("Filter by layer"),
          "body": gettext("Enable or disable the layers in order to filter the objects to be shown on the map."),
          "selector": "#map-panel-layers-tab"
        }
      ]
    },
    "community_list": {
      "slides": [
        {
          "title": gettext("All our communities"),
          "body": gettext("Here you find a list and a short description of all the communities that have been registered on MootiroMaps. Click on the name of each community in order to access its page."),
          "selector": "div.view-list-item > h4 > span > a"
        }, {
          "title": gettext("See it on the map"),
          "body": gettext("Click on this icon in order to get an idea on where this content is located on the map."),
          "selector": "div.view-list-item > h4 > a.list-map-preview",
          "options": "tipLocation:right;",
          "offsetY": -20
        }, {
          "title": gettext("Custom the results list"),
          "body": gettext("Configure the visualization of results and filter content: you can sort contents by alphabetical order or creation date. Setting the right keywords you will easily find content that fits your interest."),
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
          "title": gettext("So many actors"),
          "body": gettext("Here you find a list and short description of all the organizations, institutions and actors that have been registered on MootiroMaps. Click on the name of each content in order to access its page."),
          "selector": "div.view-list-item a.org-list-name"
        }, {
          "title": gettext("Custom the results list"),
          "body": gettext("Configure the visualization of results and filter content: you can sort contents by alphabetical order or creation date. Setting the right keywords you will easily find content that fits your interest."),
          "selector": "div.view-list-visualization-header i",
          "options": "tipLocation:right;",
          "offsetX": 20,
          "offsetY": -28
        }, {
          "title": gettext("Add an organization yourself"),
          "body": gettext("Some organization is missing? No problem! You can add it. Just click here and fill out the form."),
          "selector": "div.button-new"
        }
      ]
    },
    "need_list": {
      "slides": [
        {
          "title": gettext("Browse needs and challenges"),
          "body": gettext("On this page you find a list and short description of all the needs, challenges and community problems that have been registered on MootiroMaps. You can learn more by clicking on the name of each content."),
          "selector": "div.view-list-item > h4 > span > a"
        }, {
          "title": gettext("See it on the map"),
          "body": gettext("Click on this icon in order to get an idea on where this content is located on the map."),
          "selector": "div.view-list-item > h4 > a.list-map-preview",
          "options": "tipLocation:right;",
          "offsetY": -20
        }, {
          "title": gettext("Custom the results list"),
          "body": gettext("Configure the visualization of results and filter content: you can sort contents by alphabetical order or creation date. Setting the right keywords you will easily find content that fits your interest."),
          "selector": "div.view-list-visualization-header i",
          "options": "tipLocation:right;",
          "offsetX": 20,
          "offsetY": -28
        }, {
          "title": gettext("Report a need of your community"),
          "body": gettext("Click here to add a new need or community problem to MootiroMaps."),
          "selector": "div.button-new"
        }
      ]
    },
    "resource_list": {
      "slides": [
        {
          "title": gettext("Resources for local development"),
          "body": gettext("Here you find a list and short description of all the resources that have been registered on MootiroMaps so far! They are available in the communities and can be used for local development. Click on the title of each resource to find out more information."),
          "selector": "div.view-list-item > h4 > span > a"
        }, {
          "title": gettext("See it on the map"),
          "body": gettext("Click on this icon in order to get an idea on where this content is located on the map."),
          "selector": "div.view-list-item > h4 > a.list-map-preview",
          "options": "tipLocation:right;",
          "offsetY": -20
        }, {
          "title": gettext("Custom the results list"),
          "body": gettext("Configure the visualization of results and filter content: you can sort contents by alphabetical order or creation date. Setting the right keywords you will easily find content that fits your interest."),
          "selector": "div.view-list-visualization-header i",
          "options": "tipLocation:right;",
          "offsetX": 20,
          "offsetY": -28
        }, {
          "title": gettext("Add a resource to the map"),
          "body": gettext("You know about a resource (equipment, rooms, vehicles, outdoor facilities, etc.) available to your community that is missing on the map? Go ahead and add this information! "),
          "selector": "div.button-new"
        }
      ]
    },
    "investment_list": {
      "slides": [
        {
          "title": gettext("Where the money comes from ... and where it goes"),
          "body": gettext("You can map public and private investments on MootiroMaps. Give transparency about who is financing your organization. Below, you find a list of all investments. Click on each title to learn more."),
          "selector": "div.view-list-item > h4 > span > a"
        }, {
          "title": gettext("See it on the map"),
          "body": gettext("Click on this icon in order to get an idea on where this content is located on the map."),
          "selector": "div.view-list-item > h4 > a.list-map-preview",
          "options": "tipLocation:right;",
          "offsetY": -20
        }, {
          "title": gettext("Custom the results list"),
          "body": gettext("Configure the visualization of results and filter content: you can sort contents by alphabetical order or creation date. Setting the right keywords you will easily find content that fits your interest."),
          "selector": "div.view-list-visualization-header",
          "options": "tipLocation:right;",
          "offsetX": 20
        }
      ]
    },
    "project_list": {
      "slides": [
        {
          "title": gettext("It's all about projects"),
          "body": gettext("Objects on MootiroMaps can be added to one or more mapping projects. Mapping projects can be related to a specific community, organization or topic. Below you find a list of all projects that have been created so far. Click on its titles to access the project pages."),
          "selector": "div.view-list-item span > a"
        }, {
          "title": gettext("Custom the results list"),
          "body": gettext("You can filter and search by using keywords. Sometimes contents do not appear as they have not been tagged properly. Help improving mapped data and set keywords!"),
          "selector": "div.view-list-visualization-header i",
          "options": "tipLocation:right;",
          "offsetX": 20,
          "offsetY": -28
        }, {
          "title": gettext("Make your own project!"),
          "body": gettext("Click here in order to start your own mapping project! Have a look at the examples to get an idea about what you can do with MootiroMaps."),
          "selector": "div.button-new"
        }
      ]
    },
    "community_show": {
      "slides": [
        {
          "title": gettext("Name of the community"),
          "body": gettext("This is the name of the community. You can find the community by typing its name in the search field above."),
          "selector": ".main-column h2.title"
        }, {
          "title": gettext("Some information missing? - Become an editor!"),
          "body": gettext("It is very easy to collaborate with MootiroMaps. Just click on the edit icon and add some information."),
          "selector": "div.view-edit-btn",
          "options": "tipLocation:bottom;nubPosition:top-right;",
          "offsetX": -135
        }, {
          "title": gettext("Each community has its own story to tell"),
          "body": gettext("Every community has its description field. There you should inform its location, history, statistical data, cultures and traditions and so on. Be creative and contribute with your knowledge."),
          "selector": ".main-column .mark-down",
          "options": "tipLocation:left;"
        }, {
          "title": gettext("See it on the map"),
          "body": gettext("Click here in order to see this community on a larger map. You can also find out about related resources, needs and organizations."),
          "selector": "#map-preview",
          "options": "tipLocation:left;"
        }, {
          "title": gettext("Nearby communities"),
          "body": gettext("In this section you can find communities that are close. Have a look at them and resources and organizations located there."),
          "selector": ".right-bar .nearby-communities",
          "options": "tipLocation:left;"
        }, {
          "title": gettext("Get notifications"),
          "body": gettext('You want to receive notifications when a content is modified? No problem! Just subscribe the content and you will receive an email everytime that someone edits or comments.'),
          "selector": ".view-follow-btns",
          "options": ""
        }, {
          "title": gettext("Leave your opinion"),
          "body": gettext("What do you think about this content? What is your opinion? Write a comment and interact with other users."),
          "selector": "#divFormComment",
          "options": "tipLocation:bottom;"
        }, {
          "title": gettext("Spread the word"),
          "body": gettext("Did you like the information on this page? Share it with your friends on Facebook, Twitter and Google+."),
          "selector": ".fb-like",
          "options": "tipLocation:bottom;"
        }
      ]
    },
    "organization_show": {
      "slides": [
        {
          "title": gettext("Name of the organization"),
          "body": gettext("This is the name of the organization. Sometimes users added a detail, for instance name of the municipality or the state to avoid ambiguity. You can find this content by typing its name in the search field above."),
          "selector": ".organization-header"
        }, {
          "title": gettext("Some information missing? - Become an editor!"),
          "body": gettext("It is very easy to collaborate with MootiroMaps. Just click on the edit icon and add some information."),
          "selector": "div.view-edit-btn",
          "options": "tipLocation:bottom;nubPosition:top-right;",
          "offsetX": -135
        }, {
          "title": gettext("Tell us more about this organization"),
          "body": gettext("Do you know something about this organization or institution? Share your information here and write about its activities, objectives, history or partners."),
          "selector": ".main-column .mark-down",
          "options": "tipLocation:left;"
        }, {
          "title": gettext("See it on the map"),
          "body": gettext("Click here in order to see this organization on a larger map. You can also find out about related communities, needs and resources."),
          "selector": "#map-preview",
          "options": "tipLocation:left;"
        }, {
          "title": gettext("Use this information in you project"),
          "body": gettext("Here you can see in which projects this organization appears. You can also use it in you mapping project. Just click on the add button."),
          "selector": ".projects-tag-header",
          "options": "tipLocation:left;"
        }, {
          "title": gettext("Get notifications"),
          "body": gettext('You want to receive notifications when a content is modified? No problem! Just subscribe the content and you will receive an email everytime that someone edits or comments.'),
          "selector": ".view-follow-btns",
          "options": ""
        }, {
          "title": gettext("Leave your opinion"),
          "body": gettext("What do you think about this content? What is your opinion? Write a comment and interact with other users."),
          "selector": "#divFormComment",
          "options": "tipLocation:bottom;"
        }, {
          "title": gettext("Spread the word"),
          "body": gettext("Did you like this page? Share it with your friends on Facebook, Twitter and Google+."),
          "selector": ".fb-like",
          "options": "tipLocation:bottom;"
        }
      ]
    },
    "need_show": {
      "slides": [
        {
          "title": gettext("Name of the community need"),
          "body": gettext("This is the title of the community need. Make sure that it is easy to understand. Users can search for this need by typing its name in the search field above."),
          "selector": ".need-title"
        }, {
          "title": gettext("Some information missing? - Become an editor!"),
          "body": gettext("It is very easy to collaborate with MootiroMaps. Just click on the edit icon and add some information."),
          "selector": "div.view-edit-btn",
          "options": "tipLocation:bottom;nubPosition:top-right;",
          "offsetX": -135
        }, {
          "title": gettext("Tell us more about this need"),
          "body": gettext("In order to solve a problem, it is important to have information about its causes and origin. Also it could be interesting to know what has been tried so far to find a solution. You can use this section to give some details."),
          "selector": ".main-column .mark-down",
          "options": "tipLocation:right;"
        }, {
          "title": gettext("See it on the map"),
          "body": gettext("Click here in order to see this community on a larger map. You can also find out about related resources, communities and organizations."),
          "selector": "#map-preview",
          "options": "tipLocation:left;"
        }, {
          "title": gettext("Ideas for problem solving"),
          "body": gettext("Have an idea about how to solve this problem? Click here and add a new proposal!"),
          "selector": ".need-proposals",
          "options": "tipLocation:left;"
        }, {
          "title": gettext("Similar needs"),
          "body": gettext("Here you find related needs. Sometimes, in order to solve a problem it is important to know about how other communities got along with it and which strategies they used. Have a look and learn from similar needs."),
          "selector": "#related-needs",
          "options": "tipLocation:left;"
        }, {
          "title": gettext("Get notifications"),
          "body": gettext('You want to receive notifications when a content is modified? No problem! Just subscribe the content and you will receive an email everytime that someone edits or comments.'),
          "selector": ".view-follow-btns",
          "options": ""
        }, {
          "title": gettext("Leave your opinion"),
          "body": gettext("What do you think about this content? What is your opinion? Write a comment and interact with other users."),
          "selector": "#divFormComment",
          "options": "tipLocation:bottom;"
        }, {
          "title": gettext("Spread the word"),
          "body": gettext("Do you consider this problem important? Spread the word about it by sharing on Facebook, Twitter and Google+."),
          "selector": ".fb-like",
          "options": "tipLocation:bottom;"
        }
      ]
    },
    "resource_show": {
      "slides": [
        {
          "title": gettext("Name of the resource"),
          "body": gettext("This is the title of the resource. Make sure it is clear. Users might find this resource by typing its name in the search field above."),
          "selector": "h2.title"
        }, {
          "title": gettext("Some information missing? - Become an editor!"),
          "body": gettext("It is very easy to collaborate with MootiroMaps. Just click on the edit icon and add some information."),
          "selector": "div.view-edit-btn",
          "options": "tipLocation:bottom;nubPosition:top-right;",
          "offsetX": -135
        }, {
          "title": gettext("Tell us more about this resource"),
          "body": gettext("Resources can be used in the local development of your community. Inform how people can have access to this resource, when is it open, whom do they have to talk to?"),
          "selector": ".main-column .mark-down",
          "options": "tipLocation:right;"
        }, {
          "title": gettext("See it on the map"),
          "body": gettext("Click here in order to see this resource on a larger map. You can also find out about related needs, communities and organizations."),
          "selector": "#map-preview",
          "options": "tipLocation:left;"
        }, {
          "title": gettext("Similar resources"),
          "body": gettext("Here you can find similar resources according to the tags that were used in its descriptions. "),
          "selector": ".related-resource",
          "options": "tipLocation:left;",
          "offsetX": -10,
          "offsetY": -25
        }, {
          "title": gettext("Get notifications"),
          "body": gettext('You want to receive notifications when a content is modified? No problem! Just subscribe the content and you will receive an email everytime that someone edits or comments.'),
          "selector": ".view-follow-btns",
          "options": ""
        }, {
          "title": gettext("Leave your opinion"),
          "body": gettext("What do you think about this content? What is your opinion? Write a comment and interact with other users."),
          "selector": "#divFormComment",
          "options": "tipLocation:bottom;"
        }, {
          "title": gettext("Spread the word"),
          "body": gettext("Did you like this information? Spread it on social networks!"),
          "selector": ".fb-like",
          "options": "tipLocation:bottom;"
        }
      ]
    },
    "investment_show": {
      "slides": [
        {
          "title": gettext("Name of the investment"),
          "body": gettext("This is the name of your investment. Make sure it is clear. It should contain data about the name of the investor or grantee."),
          "selector": "h2.title"
        }, {
          "title": gettext("Some information missing? - Become an editor!"),
          "body": gettext("It is very easy to collaborate with MootiroMaps. Just click on the edit icon and add some information."),
          "selector": "div.view-edit-btn",
          "options": "tipLocation:bottom;nubPosition:top-right;",
          "offsetX": -135
        }, {
          "title": gettext("Give transparency about the investment"),
          "body": gettext("Do you know anything about the money that has been spent? What is it for? When has it been received? What are expected results? "),
          "selector": ".main-column .mark-down",
          "options": "tipLocation:right;"
        }, {
          "title": gettext("Get notifications"),
          "body": gettext('You want to receive notifications when a content is modified? No problem! Just subscribe the content and you will receive an email everytime that someone edits or comments.'),
          "selector": ".view-follow-btns",
          "options": ""
        }, {
          "title": gettext("Leave your opinion"),
          "body": gettext("What do you think about this content? What is your opinion? Write a comment and interact with other users."),
          "selector": "#divFormComment",
          "options": "tipLocation:bottom;"
        }, {
          "title": gettext("Spread the word"),
          "body": gettext("Did you find this information useful? Spread it on social networks!"),
          "selector": ".fb-like",
          "options": "tipLocation:bottom;"
        }
      ]
    },
    "project_show": {
      "slides": [
        {
          "title": gettext("Project title"),
          "body": gettext("This is the name of the project. You can find the project by typing its name in the search field above."),
          "selector": "h2.title"
        }, {
          "title": gettext("Some information missing? - Become an editor!"),
          "body": gettext("It is very easy to collaborate with MootiroMaps. Just click on the edit icon and add some information."),
          "selector": "div.view-edit-btn",
          "options": "tipLocation:bottom;nubPosition:top-right;",
          "offsetX": -135
        }, {
          "title": gettext("Project description"),
          "body": gettext("In this section you may find more about the goals of this project, how is it done and how you can contribute to mapping."),
          "selector": ".main-column .mark-down",
          "options": "tipLocation:right;"
        }, {
          "title": gettext("Associated objects"),
          "body": gettext("Here you can find a list of all the objects (organizations, resources, needs, etc.) that were added to this project."),
          "selector": ".view-info-buttons",
          "options": "tipLocation:top;",
          "offsetX": 50
        }, {
          "title": gettext("See it on the map"),
          "body": gettext("Click here to navigate the map of this project and add new content."),
          "selector": "#map-preview",
          "options": "tipLocation:left;"
        }, {
          "title": gettext("Who is making this map"),
          "body": gettext("In this section you can see who created the project and contributed to it so far. "),
          "selector": ".view-info-btn:last"
        }, {
          "title": gettext("Get notifications"),
          "body": gettext('You want to receive notifications when a content is modified? No problem! Just subscribe the content and you will receive an email everytime that someone edits or comments.'),
          "selector": ".view-follow-btns",
          "options": ""
        }, {
          "title": gettext("Leave your opinion"),
          "body": gettext("What do you think about this content? What is your opinion? Write a comment and interact with other users."),
          "selector": "#divFormComment",
          "options": "tipLocation:bottom;"
        }, {
          "title": gettext("Spread the word"),
          "body": gettext("Did you like this project? Share it on your social networks. Help to engage people with this data!"),
          "selector": ".fb-like",
          "options": "tipLocation:bottom;"
        }
      ]
    }
  };

  return HelpCenter;

})();

window.HelpCenter = HelpCenter;
