# Implementação do Mapa

## Organização do Código

O código do mapa é organizado em módulos utilizando AMD (Asynchronous Module Definition). Cada módulo pode conter uma ou mais classes ou componentes (trataremos dos componentes mais adiante).

É seguida a seguinte hierarquia para o código client-side relativo ao mapa:

* komoo\_map/static
    * coffee/
        * map.jquery.coffee
        * related\_items\_panel.coffee
        * map/
            * collections.coffee
                * GenericCollection - Generic class
                    * FeatureCollection
                        * FeatureCollectionPlus
            * common.coffee
            * component.coffee
                * Component - Generic class
            * controls.coffee
                * Box (Component) - Generic class
                    * SupporterBox
                    * LicenseBox
                    * CloseBox
                    * GeometrySelector
                    * DrawingControl
                * DrawingManager (Component)
                * PerimeterSelector (Component)
                * Balloon (Component) - Generic class
                    * AjaxBalloon - Generic class
                        * InfoWindow
                        * Tooltip
                * FeatureClusterer (Component)
                * Location (Component)
                    * SaveLocation
                        * AutosaveLocation
                * StreetView (Component)
            * core.coffee
                * Mediator
            * features.coffee
                * Feature
                * makeFeature - Factory
            * geometries.coffee
                * Geometry - Generic class
                    * Empty
                    * Point
                    * MultiPoint
                        * SinglePoint
                    * LineString
                        * MultiLineString
                        * Polygon
                * makeGeometry - Factory
            * maps.coffee
                * Map (Mediator)
                    * UserEditor
                    * Editor
                    * Preview
                    * StaticMap
                        * AjaxMap
                            * AjaxEditor
                * makeMap - Factory
            * maptypes.coffee
                * CleanMapType (Component)
            * providers.coffee
                * GenericProvider (Component) - Generic class
                    * FeatureProvider
    * js/
        * vendor/
            * [infobox\_packed.js](http://code.google.com/p/google-maps-utility-library-v3/wiki/Libraries#InfoBox)
            * [markercluster\_packed.js](http://code.google.com/p/google-maps-utility-library-v3/wiki/Libraries#MarkerClustererPlus)


## Componentes

Devido a necessidade de utilização da visualização no mapa em diversas áreas diferentes do sistema, cada uma com caracteristicas próprias, as diversas funcionalidades foram implementadas como componentes plugáveis com baixo acoplamento. É utilizado aqui o termo componente e não módulo para que haja uma distinção em relação aos módulos relativos ao AMD.

Um componente pode ser usado independentemente de quais outros estejam ou não sendo utilizados. Para alterar uma funcionalidade do mapa basta que se altere o componente responsável por ela.

A adição de componentes no mapa é feita com o método `addComponent(name, [type], [options])`. O parâmetro **name** deve estar no formato `module::ComponentClass`, onde _module_ é o módulo que será carregado internamente usando [RequireJS](http://requirejs.org/), o qual deve exportar um objeto contendo a classe do componente. Mais adiante será dado um exemplo.

O componente será instanciada recebendo a instância do mediador como parâmetro do construtor (o mapa terá o papel de mediador, como será explicado) e logo em seguida será chamado o método `init` do componente, passando como parâmetro o objeto de opções passado pelo método `addComponent` do mapa.

O método `init` poderá ser implementado como síncrono ou assíncrono. No primeiro caso não há necessidade de devolver valor algum, no segundo deve-se devolver uma promessa de um objeto deferred. O componente só será considerado inicializado quando a promessa for resolvida. Veja o exemplo a seguir.


    # Arquivo map/controls.coffee
    define ['jquery', 'map/component'], ($, Component) ->

      class Foo extends Component
        init: (opts) ->
          # Componente com inicialização síncrona
          content = opts?.content ? 'Nothing?!?'
          console?.log "Fui inicializado com o conteúdo '#{content}'"


      class Bar extends Component
        init: (opts) ->
          # Componente com inicialização assíncrona
          url = opts?.url ? '/default'
          dfd = @map.data.deferred()
          $.ajax(url).done(
            # Faz o que deve ser feito
          ).always () ->
            dfd.resolve()

          # Devolve uma promessa
          return dfd.promise()

      return
        Foo: Foo
        Bar: Bar


    # Arquivo app.coffee
    map = new Map({elementId: '#map-canvas'})
    map.addComponent('map/controls::Foo', 'dummy', {content: 'Spock Spock Spock!'})
    map.addComponent('map/controls::Bar', 'dummy', {url: '/bar'})


No caso de métodos assíncronos, deve-se utilizar `@map.data.deferred` e `@map.data.when` para garantir que os componentes utilizarão sempre a mesma implementação de objetos deferred que o mapa. Atualmente ambos são mapeados para a implementação do [jQuery](http://api.jquery.com/category/deferred-object/).


Há basicamente 3 categorias de componente: **Controls**, **MapTypes** e **Providers**. Abaixo há uma descrição de cada categoria, quais componentes pertencem a cada categoria e a responsabilidade de cada um. É apresentada também uma lista de mensagens publicadas e subscritas por cada componente, no formato _mensagem (lista de parâmetros)_.

### Controls

Na categoria de controles ficam basicamente as funcionalidades com as quais o usuário interage ou que desenhem caixas no mapa.

#### SupporterBox

Desenha os logos das organizações que suportam o projeto.

#### LicenseBox

Exibe informações sobre a licença do conteúdo do sistema.

#### CloseBox

Inclui uma caixa simples que exibe um botão para fechar mapas que foram abertos se sobrepondo ao conteúdo original da página.

Publica:

* close\_clicked

#### GeometrySelector

Possibilita a escolha de geometria (ponto, linha, polígono) na edição de elementos criados sem.

Publica:

* cancel\_drawing

Subscreve:

* select\_new\_geometry

#### DrawingControl

Inclui os controles de edição (botões para adicionar mais pontos, apagar polígonos, etc).

Publica:

* finish\_drawing
* cancel\_drawing

Subscreve:

* drawing\_started
* drawing\_finished
* mode\_changed

#### DrawingManager

Ativa a funcionalidade de edição.

Publica:

* drawing\_finished (feature, success)
* select\_new\_geometry (feature)
* drawing\_started (feature)

Subscreve:

* draw\_feature
* edit\_feature
* drawing\_finished
* finish\_drawing
* cancel\_drawing
* mode\_changed
* feature\_rightclick

#### PerimeterSelector

Permite a seleção de um perímetro no mapa (escolha de centro e raio de uma área circular).

Publica:

* perimeter\_selected (latLng, circleObj)

Subscreve:

* select\_perimeter
* click
* feature\_click

#### InfoWindow

Exibe informações sobre elementos quando clicados.

Subscreve:

* drawing\_started
* drawing\_finished
* feature\_click
* feature\_highlight\_changed

#### Tooltip

Exibe informações sobre elementos quando passa o mouse.

Publica:

* feature\_click (mouseEvent, feature)

Subscreve:

* drawing\_started
* drawing\_finished
* feature\_mousemove
* feature\_mouseout
* feature\_click
* cluster\_mouseover
* cluster\_mouseout
* cluster\_click

#### FeatureClusterer

Agrupa elementos próximos em clusters.

Publica:

* cluster\_click (features, clusterCenter)
* cluster\_mouseover (features, clusterCenter)
* cluster\_mouseout (features, clusterCenter)

Subscreve:

* feature_created

#### Location

Permite utilizar tanto coordenadas espaciais quanto endereços por extenso para definir a posição do mapa. Fornece também a localização do usuário utilizando geolocalização fornecida pelo navegador ou localização por ip via serviço do Google.

Subscreve:

* goto
* goto\_user\_location

#### SaveLocation

Permite salvar e recuperar a posição e o zoom atuais do mapa.

Publica:

* set\_location
* set\_zoom

Subscreve:

* save_location
* goto\_saved\_location

#### AutosaveLocation

Salva automaticamente a posição e o zoom do mapa sempre que alterados.

Subscreve:

* idle

#### StreetView

Adiciona o Google StreetView ao mapa.


### Maptype

Componentes deste tipo forncem opções visuais para o mapa, adicionando mais opções além dos padrões _Mapa_ e _Hibrido_.

#### CleanMapType

Fornece uma visualização mais discreta com cores mais apagadas e sem alguns elementos.


### Providers

Componentes que fornecem os elementos registrados no sistema para exibição no mapa durante a navegação.

#### FeatureProvider

Provê elementos via requisições AJAX, interpretando o GEOjson recebido do servidor, instanciando e adicionando _Features_ ao mapa.


## Mediador

Por simplicidade a própria classe do mapa faz o papel de mediador. Esta escolha foi feita pois nenhum componente tem utilidade sem um mapa. Isto quer dizer todos os componentes que forem adicionados terão sempre acesso à instância do mapa, com a qual interagem através das variáveis de instância `map` ou `mediator`.


    class Foo extends Component
      init: (opts) ->
        zoom = @map.getZoom()
        console?.log "The current zoom level is #{zoom}"


Como já explicado antes, um componente não possui acesso direto a outro componente. Para comunicação entre componentes deve-se utilizar o padrão publish/subscribe, através dos métodos `subscribe` e `publish` do mapa.


    class Foo extends Component
      init: (opts) ->
        @map.subscribe 'Bar_changed', () ->
          console?.log 'Foo knows that Bar changed'


    class Bar extends Component
      onChange: () ->
        @map.publish 'Bar_changed'


Esse padrão permite que ambos os componentes se comuniquem ao mesmo tempo que permite que se utilize apenas um deles sem precisar adicionar qualquer outro como dependência.


## Map

_TODO_


## Features

A classe Feature representa os vários objetos georreferenciados que serão desenhados no mapa. O comportamento e a aparência de cada _objeto_ é em parte determinados pela agregação de um objeto do tipo _Geometry_ e de um do tipo _FeatureType_.
Os objetos _Geometry_ serão descritos a seguir. Os objetos do tipo _FeatureType_ criados automaticamente a partir de declarações nos modelos python de cada _objeto_, seguindo a seguinte estrutura:

    class Model(GeoRefModel):
        class Map:
            editable = True

            title = ''
            tooltip = ''

            background_color = '#000'
            background_opacity = 0.6
            border_color = '#000'
            border_opacity = 0.6
            border_size = 1.5
            border_size_hover = 2.5

            geometries = []
            categories = []

            form_view_name = ''
            form_view_args = []
            form_view_kwargs = {}

            min_zoom_geometry = 16
            max_zoom_geometry = 100
            min_zoom_point = 14
            max_zoom_point = 15
            min_zoom_icon = 18
            max_zoom_icon = 100

            zindex = 10

As propriedades de cada modelo são convertidas para um objeto javascript e carregadas automaticamente pela classe Map via AJAX.

No modulo _Features_ há também uma função factory, `makeFeature`, que facilita a criação de instâncias da classe _Feature_ a partir de um objeto _geojson_. Já é criada junto uma instância de _Geometry_ e associado o _FeatureType_ correto.

## Geometries

No módulo _Geometries_ são definidas várias classes que abstraem os _overlays_ do Google Maps. São elas
* **Empty** - Objeto dummy para implementar Null Object pattern
* **Point** - Ponto único no mapa
* **MultiPoint** - Conjunto de vários pontos com características e comportamentos iguais
* **SinglePoint** - Conjunto de vários pontos mas que permite a inclusão de apenas um ponto no conjunto (implementado por motívos de compatibilidade com dados antigos)
* **LineString** - Linha única
* **MultiLineString** - Conjunto de várias linhas com características e comportamentos iguais
* **Polygon** - Polígono que permite vários caminhos

Neste módulo também há uma função factory, `makeGeometry`, que devolve a instância adequada para um _geojson_ recebido. Em geral este método só será utilizado pela função `makeFeature` e pela função responsável por alterar o tipo de geometria de uma instânica de _Feature_ já existente.

A aparência e o comportamento de cada instância de _Geometry_ são controlados pela instância de _Feature_ a qual está associada.


## JQuery Plugin

_TODO_

