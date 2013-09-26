
define(['jquery', 'underscore', 'backbone'], function($, _, Backbone) {
  window.PanelInfo = Backbone.Model.extend({
    toJSON: function(attr) {
      return Backbone.Model.prototype.toJSON.call(this, attr);
    }
  });
  window.PanelInfoView = Backbone.View.extend({
    className: 'panel-info',
    initialize: function() {
      _.bindAll(this, 'render');
      return this.template = _.template($('#panel-info-template').html());
    },
    render: function() {
      var renderedContent;
      renderedContent = this.template(this.model.toJSON());
      $(this.el).html(renderedContent);
      return this;
    }
  });
  window.Feature = Backbone.Model.extend({
    toJSON: function(attr) {
      var defaultJSON, name, _ref, _ref2, _ref3;
      defaultJSON = Backbone.Model.prototype.toJSON.call(this, attr);
      name = (_ref = (_ref2 = this.get('properties')) != null ? _ref2['organization_name'] : void 0) != null ? _ref : '';
      if (name) name += ' - ';
      name += (_ref3 = this.get('properties')) != null ? _ref3['name'] : void 0;
      return _.extend(defaultJSON, {
        iconClass: this.iconClass,
        name: name
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
    title: function(count) {
      var msg;
      msg = this.type === 'Organization' ? ngettext("%s organization", "%s organizations", count) : this.type === 'Community' ? ngettext("%s community", "%s communities", count) : this.type === 'Resource' ? ngettext("%s resource", "%s resources", count) : this.type === 'Need' ? ngettext("%s need", "%s needs", count) : this.type === 'User' ? ngettext("%s collaborator", "%s collaborators", count) : "";
      return interpolate(msg, [count]);
    },
    iconClass: function() {
      var modelName;
      modelName = this.type;
      return "icon-" + (modelName.toLowerCase()) + "-big";
    },
    render: function() {
      var $features, collection;
      collection = this.collection;
      if (collection.length === 0) return this;
      this.$el.html(this.template({
        title: this.title(collection.length),
        iconClass: this.iconClass()
      }));
      $features = this.$('.feature-list');
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
  if (typeof KomooNS === "undefined" || KomooNS === null) KomooNS = {};
  KomooNS.drawFeaturesList = function(FeaturesViewClass) {
    var communitiesView, needsView, organizationsView, resourcesView, usersView,
      _this = this;
    if (FeaturesViewClass == null) FeaturesViewClass = FeaturesView;
    KomooNS.features = _(geojson.features).groupBy(function(f) {
      return f.properties.type;
    });
    communitiesView = new FeaturesViewClass({
      type: 'Community',
      collection: new Features().reset(KomooNS.features['Community'])
    });
    $('.features-wrapper').append(communitiesView.render().$el);
    needsView = new FeaturesViewClass({
      type: 'Need',
      collection: new Features().reset(KomooNS.features['Need'])
    });
    $('.features-wrapper').append(needsView.render().$el);
    resourcesView = new FeaturesViewClass({
      type: 'Resource',
      collection: new Features().reset(KomooNS.features['Resource'])
    });
    $('.features-wrapper').append(resourcesView.render().$el);
    organizationsView = new FeaturesViewClass({
      type: 'Organization',
      collection: new Features().reset(_.filter(KomooNS.features['Organization'], function(o) {
        return o.properties.name !== KomooNS.obj.name;
      }))
    });
    $('.features-wrapper').append(organizationsView.render().$el);
    usersView = new FeaturesViewClass({
      type: 'User',
      collection: new Features().reset(KomooNS.features['User'])
    });
    $('.features-wrapper').append(usersView.render().$el);
    return geoObjectsListing($('.features-wrapper'));
  };
  return KomooNS.drawFeaturesList;
});
