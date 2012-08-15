(function() {

  define(['lib/underscore-min', 'lib/backbone-min'], function() {
    var $;
    $ = jQuery;
    window.Feature = Backbone.Model.extend({
      iconClass: function() {
        var modelName;
        if (this.properties.type === 'OrganizationBranch') {
          modelName = 'Organization';
        } else {
          modelName = this.properties.type;
        }
        return "icon-" + (modelName.toLowerCase()) + "-big";
      },
      toJSON: function(attr) {
        var defaultJSON;
        defaultJSON = Backbone.Model.prototype.toJSON.call(this, attr);
        return _.extend(defaultJSON, {
          iconClass: this.iconClass
        });
      },
      displayOnMap: function() {
        return $('#map-canvas').komooMap('highlight', {
          type: this.get('properties').type,
          id: this.get('properties').id
        });
      }
    });
    window.FeatureView = Backbone.View.extend({
      tagName: 'li',
      className: 'feature',
      events: {
        'mouseover': 'displayOnMap'
      },
      initialize: function() {
        _.bindAll(this, 'render', 'displayOnMap');
        return this.template = _.template($('#feature-template').html());
      },
      render: function() {
        var renderedContent;
        console.log('rendering model: ', this.model.toJSON());
        renderedContent = this.template(this.model.toJSON());
        $(this.el).html(renderedContent);
        return this;
      },
      displayOnMap: function() {
        this.model.displayOnMap();
        return this;
      }
    });
    window.Features = Backbone.Collection.extend({
      model: Feature
    });
    window.FeaturesView = Backbone.View.extend({
      initialize: function() {
        _.bindAll(this, 'render');
        this.template = _.template($('#features-template').html());
        return this.collection.bind('reset', this.render);
      },
      render: function() {
        var $features, collection;
        this.$el.html(this.template({}));
        $features = this.$('.feature-list');
        collection = this.collection;
        collection.each(function(feature) {
          var view;
          view = new FeatureView({
            model: feature
          });
          return $features.append(view.render().$el);
        });
        return this;
      }
    });
    return $(function() {
      var featuresView, loadedFeatures;
      if (typeof KomooNS === "undefined" || KomooNS === null) KomooNS = {};
      KomooNS.features = geojson.features;
      loadedFeatures = new Features();
      loadedFeatures.reset(window.KomooNS.features);
      featuresView = new FeaturesView({
        collection: loadedFeatures
      });
      return $('.features-wrapper').append(featuresView.render().$el);
    });
  });

}).call(this);
