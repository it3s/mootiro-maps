define(['map/layers'], function(Layers) {
  colors = [
    'e11d21',
    'eb6420',
    'fbca04',
    '009800',
    '006b75',
    '207de5',
    '0052cc',
    '5319e7'
  ];

  var lastUsedColor = -1;

  // Layers configuration
  var LayersWidget = function(el) {
  if(el === undefined) el = '<div>';
    this.$el = $(el);
    this.$el.addClass('layers_widget');
    this.layers = new Layers.Layers();
    window.layers = this.layers;
    this.createControls();
  };

  LayersWidget.prototype.createControls = function() {
    var that = this;
    this.cur = 0;
    this.$ul = $('<ul>');
    this.$ul.sortable({
      placeholder: "ui-state-highlight",
      forcePlaceholderSize: true,
      delay: 300,
      axis: "y",
      stop: function(e, ui) { that.refresh(); }
    });
    this.$el.append(this.$ul);
    var $addBtn = $('<a>').text(gettext('New layer')).addClass('add_btn');
    $addBtn.click(function() { that.createNewLayer(); });
    this.$el.append($addBtn);
    return this;
  };

  LayersWidget.prototype.refresh = function(layers) {
    layers = layers || this.layers;
    layers.forEach(function(layer) {
      layer.$el.find('input[name=name]').val(layer.getName());

      // This widget only accept rule of type {operator:'has', property:'tags', value:[...]}
      var rule = layer.getRule();
      if (rule !== undefined && rule.operator === 'has' && rule.property === 'tags' && rule.value !== undefined) {
        layer.$el.find('input[name=tags]').importTags(rule.value.join(','));
      }

      layer.$el.find('.fillcolor').colpickSetColor(layer.getFillColor());
      layer.$el.find('.fillcolor').css('background', layer.getFillColor());

      layer.$el.find('.strokecolor').colpickSetColor(layer.getStrokeColor());
      layer.$el.find('.strokecolor').css('background', layer.getStrokeColor());

      layer.setPosition(layer.$el.index());
      layer.$el.find('.title').text(interpolate(gettext("Layer %s"), [layer.getPosition() + 1]));
      layer.$el.find('.layer_name').text(layer.getName());
    });
    return this;
  };

  LayersWidget.prototype.setRule = function(layer, tags) {
    var rule = undefined;
    if (tags.length) {
      rule = {
        operator: 'has',
        property: 'tags',
        value: tags.split(',')
      };
    }
    layer.setRule(rule);
    var count = layer.countFeatures();
    layer.$el.find('.layer_count').text(interpolate(
        ngettext('%s object', '%s objects', count),
        [count]));
    return this;
  };

  LayersWidget.prototype.addNewLayer = function(layer, map) {
    var that = this;
    this.$ul.find('.content').slideUp().parent().find('.details').show();
    layer.$el = $('<li>').addClass('layer');
    layer.$el.html('<div class="header"><h3 class="title"></h3><div class="details"><span class="strokecolor"><span class="fillcolor"></span></span><strong class="layer_name"></strong></div><span class="layer_count"></span></div>');
    layer.$el.find('.details').hide();
    layer.$el.append($('#layer_content_model').clone().show().attr('id', ''));
    // append to widget
    this.$ul.append(layer.$el);
    // init name widget
    layer.$el.find('input[name=name]').keyup(function() {
      layer.setName(this.value);
      layer.$el.find('.layer_name').text(this.value);
    });
    // init tags widget
    // FIXME: DRY
    // TODO: Convert the tags list to rule json format
    layer.$el.find('input[name=tags]').attr('id', 'tags'+layer.getId()).tagsInput({
      'autocomplete_url':'/project/search_all_tags/',
      'height':'auto',
      'width':'100%',
      'onChange': function () {
        var rule = that.setRule(layer, $(this).val());
      }
    });

    // init the color pick widgets
    layer.$el.find('.fillcolor').colpick({
      layout: 'hex',
      submit: 0,
      colorScheme: 'light',
      onChange: function(hsb, hex, rgb, fromSetColor) {
        if(!fromSetColor) {
          layer.$el.find('.fillcolor').css('background','#' + hex);
          layer.setFillColor('#' + hex);
        }
      }
    }).keyup(function(){
      $(this).colpickSetColor(this.value);
    });
    layer.$el.find('.strokecolor').colpick({
      layout: 'hex',
      submit: 0,
      colorScheme: 'light',
      onChange: function(hsb, hex, rgb, fromSetColor) {
        if(!fromSetColor) {
          layer.$el.find('.strokecolor').css('background','#' + hex);
          layer.setStrokeColor('#' + hex);
        }
      }
    }).keyup(function(){
      $(this).colpickSetColor(this.value);
    });
    layer.$el.data('layer', layer);
    layer.$el.find('.header').click(function() {
        that.toggleLayer(layer);
    });
    // init delete button
    layer.$el.find('.delete').click(function() {
      confirmationMessage(gettext('Remove layer'), gettext('Do you really want to remove this layer?'), null, function (resp) {
        if (resp === 'yes') {
          that.removeLayer(layer);
        }
      });
    });
    layer.$el.find('.collapse_btn').click(function() {
        that.toggleLayer(layer);
    });
    // add to layers collection
    this.layers.addLayer(layer);
    layer.setMap(map);
    this.refresh([layer]);
    return this;
  };

  LayersWidget.prototype.toggleLayer = function(layer) {
    layer.$el.find('.content').toggle(500);
    layer.$el.find('.details').toggle();
    return this;
  };

  LayersWidget.prototype.setRandomColor = function(layer) {
    // First try to get a color from the predefined list, if all colors were
    // already used then create a random color.
    hex = colors[++lastUsedColor];
    if (hex === undefined) {
      hex = Math.floor(Math.random() * 16777215).toString(16);
    }
    layer.setFillColor('#' + hex);
    layer.setStrokeColor('#' + hex);
    if (layer.$el) {
      layer.$el.find('.fillcolor').css('background','#' + hex);
      layer.$el.find('.strokecolor').css('background','#' + hex);
    }
    return this;
  };

  LayersWidget.prototype.removeLayer = function(layer) {
    // marks the layer to be deleted
    layer.delete = true;
    if(layer.isNew) {
      // If were are trying to remove an unsaved layer, just delete
      // it from layers collection
      this.layers.remove(layer);
    }
    // removes the layer DOM from widget
    layer.$el.remove();
    this.refresh();
    return this;
  };

  LayersWidget.prototype.createNewLayer = function(map) {
    var layer = new Layers.Layer({ id: 'new'+this.cur++ });
    layer.isNew = true;
    this.setRandomColor(layer);
    this.addNewLayer(layer, map);
    layer.$el.find('input[name=name]').focus();
    return this;
  };

  LayersWidget.prototype.loadLayers = function(layers, map) {
    for(var i=0, l=layers.length; i < l; i++) {
      this.addNewLayer(layers[i], map);
    }
    // Try to avoid repeted colors
    lastUsedColor = layers.length - 1;
    return this;
  };

  LayersWidget.prototype.toJSON = function() {
    layers = []
    this.layers.forEach(function(layer) {
      var layerJSON = layer.toJSON();
      // removes the temporary id
      if(layer.isNew) {
        layerJSON.id = undefined;
      }
      // marks the layer to be deleted
      if(layer.delete) {
        layerJSON.delete = true;
      }
      layers.push(layerJSON);
    });
    return layers;
  };

  return LayersWidget;
});
