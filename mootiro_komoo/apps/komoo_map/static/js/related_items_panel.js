(function() {

  define(['lib/underscore-min', 'lib/backbone-min'], function() {
    var $;
    $ = jQuery;
    window.Feature = Backbone.Model.extend({
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
      initialize: function() {},
      model: Feature
    });
    window.FeaturesView = Backbone.View.extend({
      initialize: function(attr) {
        _.bindAll(this, 'render');
        this.type = attr.type;
        this.template = _.template($('#features-template').html());
        return this.collection.bind('reset', this.render);
      },
      title: function() {
        if (this.type === 'OrganizationBranch') {
          return "" + this.collection.length + " points on map";
        } else if (this.type === 'Community') {
          return "On " + this.collection.length + " communities";
        } else if (this.type === 'SupportedOrganizationBranch') {
          return "Supported " + this.collection.length + " organizations";
        } else if (this.type === 'Resource') {
          return "Supported " + this.collection.length + " resources";
        } else if (this.type === 'Need') {
          return "Supported " + this.collection.length + " needs";
        } else {
          return "";
        }
      },
      iconClass: function() {
        var modelName, _ref;
        if ((_ref = this.type) === 'OrganizationBranch' || _ref === 'SupportedOrganizationBranch') {
          modelName = 'Organization';
        } else {
          modelName = this.type;
        }
        return "icon-" + (modelName.toLowerCase()) + "-big";
      },
      render: function() {
        var $features, collection;
        this.$el.html(this.template({
          title: this.title(),
          iconClass: this.iconClass()
        }));
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
      var branchsView, communitiesView, needsView, resourcesView, supportedBranchsView,
        _this = this;
      if (typeof KomooNS === "undefined" || KomooNS === null) KomooNS = {};
      KomooNS.features = _(geojson.features).groupBy(function(f) {
        return f.properties.type;
      });
      communitiesView = new FeaturesView({
        type: 'Community',
        collection: new Features().reset(KomooNS.features['Community'])
      });
      $('.features-wrapper').append(communitiesView.render().$el);
      needsView = new FeaturesView({
        type: 'Need',
        collection: new Features().reset(KomooNS.features['Need'])
      });
      $('.features-wrapper').append(needsView.render().$el);
      resourcesView = new FeaturesView({
        type: 'Resource',
        collection: new Features().reset(KomooNS.features['Resource'])
      });
      $('.features-wrapper').append(resourcesView.render().$el);
      branchsView = new FeaturesView({
        type: 'OrganizationBranch',
        collection: new Features().reset(_.filter(KomooNS.features['OrganizationBranch'], function(o) {
          return o.properties.organization_name === KomooNS.obj.name;
        }))
      });
      $('.features-wrapper').append(branchsView.render().$el);
      supportedBranchsView = new FeaturesView({
        type: 'SupportedOrganizationBranch',
        collection: new Features().reset(_.filter(KomooNS.features['OrganizationBranch'], function(o) {
          return o.properties.organization_name !== KomooNS.obj.name;
        }))
      });
      $('.features-wrapper').append(supportedBranchsView.render().$el);
      return geoObjectsListing($('.features-wrapper'));
    });
  });

}).call(this);
