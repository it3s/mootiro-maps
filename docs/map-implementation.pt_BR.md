# Implementação do Mapa

## Organização do Código

O código do mapa é organizado em módulos utilizando AMD. Cada módulo pode conter uma ou mais classes ou componentes (trataremos dos componentes a seguir).

É seguida a seguinte hierarquia (pasta > arquivo > classe > subclasses):

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
                * Ballon (Component) - Generic class
                    * AjaxBallon - Generic class
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

Devido a necessidade de utilização da visualização no mapa em diversas áreas diferentes do sistema, cada uma com caracteristicas próprias, as diversas funcionalidades foram implementadas como componentes plugáveis com baixo acoplamento. Para garantir o baixo acoplamento foram utilizados os padrões publish/subscribe e mediator, que serão tratados mais adiante.

Um componente pode ser usado independentemente de quais outros estejam ou não sendo utilizados. Pode-se também reimplementar qualquer um dos componentes substituindo o antigo para alterar alguma característica funcionalidade pela qual ele é responsável.

Os componentes são carregados no mapa com o método `addComponent(name, [type], [options])` no qual o parâmetro `name` é no formato `path/to/module::ComponentClass`. É importante que o módulo exporte a classe do componente.

Exemplo:

    map = new Map({elementId: '#map-canvas'})
    map.addComponent('map/controls::Tooltip', 'ballon')
    map.addComponent('map/controls::LicenseBox')


Os componentes estão divididos em 3 tipos:

  * Controls
  * MapTypes
  * Providers

Abaixo está a descrição da responsabilidade de cada componente junto com a lista das mensagens que cada um publica, no formato *mensagem (parâmetros)*

### Controls

Na categoria de controles ficam basicamente as funcionalidades com as quais o usuário interage para realizar tarefa.

#### SupporterBox

Caixa que exibe os logos das organizações que dão suporte ao projeto.

#### LicenseBox

Caixa que exibe informações sobre a licença do conteúdo do sistema.

#### CloseBox

Caixa simples que exibe um botão para fechar mapas que abrem se sobrepondo ao conteúdo original da página.

#### GeometrySelector

Caixa para seleção de geometria (ponto, linha, polígono) na ediçõ de elementos criados sem.

Publica:

* cancel\_drawing

#### DrawingControl

Caixa com controles de edição, por exemplo botões para adicionar mais pontos, apagar polígonos, etc.

Publica:

* finish\_drawing
* cancel\_drawing

#### DrawingManager

Ativa a funcionalidade de edição fornecida pelo Google e interage com as personalizações do nosso sistema.

Publica:

* drawing\_finished (feature, success)
* select\_new\_geometry (feature)
* drawing\_started (feature)


#### PerimeterSelector

Permite a seleção de um perímetro no mapa (escolha de centro e raio de uma área circular).

Publica:

* perimeter\_selected (latLng, circleObj)

#### InfoWindow

Exibe informações sobre elementos quando clicados.

#### Tooltip

Exibe informações sobre elementos quando passa o mouse.

Publica:

* feature\_click (mouseEvent, feature)

#### FeatureClusterer

Agrupa elementos em clusters.

Publica:

* cluster\_click (features, clusterCenter)
* cluster\_mouseover (features, clusterCenter)
* cluster\_mouseout (features, clusterCenter)

#### Location

Permite utilizar tanto coordenadas espaciais quanto endereços por extenso para selecionar locais no mapa e fornece a localização do usuário utilizando geolocalização fornecida pelo navegador ou localização por ip via serviço do Google.

#### SaveLocation

Permite salvar e recuperar a posição e o zoom atuais do mapa.

#### AutosaveLocation

Salva automaticamente a posição e o zoom do mapa sempre que alterados.

#### StreetView

Adiciona o Google StreetView ao mapa.


### Maptype

Fornce opções de visualização do mapa em si, acrescentando outras opções além do *Mapa* e do *Hibrido*.

#### CleanMapType

Fornece uma visualização mais discreta com cores mais apagadas e sem alguns elementos.


### Providers

Componentes que fornecem os elementos registrados no sistema para exibição no mapa durante a navegação.

#### FeatureProvider

Provê elementos via requisições AJAX.


## Mediator

Por simplicidade a própria classe do mapa faz o papel de mediator, visto que nenhum componente tem função sem um mapa. Isto quer dizer todos os componentes que forem carregados terão sempre acesso à instância do mapa usando a variável de instancia `map` ou `mediator`.


    class Foo extends Component
      init: (opts) ->
        zoom = @map.getZoom()
        console?.log "The current zoom level is #{zoom}"


Como já explicado antes, um componente não possui acesso direto a outro componente. Para se comunicarem deve-se utilizar o padrão publish/subscribe através dos métodos `subscribe` e `publish` do mediator, isto é, do mapa.


    class Foo extends Component
      init: (opts) ->
        @map.subscribe 'Bar_changed', () ->
          console?.log 'Foo knows that Bar changed'


    class Bar extends Component
      onChange: () ->
        @map.publish 'Bar_changed'


Esse padrão permite que ambos os componentes se comuniquem ao mesmo tempo que permite que se utilize apenas um deles sem precisar carregar o outro como dependência.

## Map

## Features


## Geometries

### Empty
### Point
### MultiPoint
### SinglePoint
### LineString
### MultiLineString
### Polygon

## JQuery Plugin
