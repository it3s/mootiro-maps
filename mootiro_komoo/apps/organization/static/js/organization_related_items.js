(function() {

  define(['lib/underscore-min', 'lib/backbone-min'], function() {
    var $;
    $ = jQuery;
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
        console.log('rendering model: ', this.model.toJSON());
        renderedContent = this.template(this.model.toJSON());
        $(this.el).html(renderedContent);
        return this;
      }
    });
    window.OrganizationFeaturesView = FeaturesView.extend({
      title: function(count) {
        var msg;
        msg = this.type === 'OrganizationBranch' ? ngettext("%s point on map", "%s points on map", count) : this.type === 'SupportedOrganizationBranch' ? ngettext("Supported %s organization", "Supported %s organizations", count) : this.type === 'Community' ? ngettext("On %s community", "On %s communities", count) : this.type === 'Resource' ? ngettext("Supported %s resource", "Supported %s resources", count) : this.type === 'Need' ? ngettext("Supported %s need", "Supported %s needs", count) : "";
        return interpolate(msg, [count]);
      }
    });
    return $(function() {
      var panelInfoView;
      KomooNS.drawFeaturesList(OrganizationFeaturesView);
      panelInfoView = new PanelInfoView({
        model: new PanelInfo(KomooNS.obj)
      });
      return $('.panel-info-wrapper').append(panelInfoView.render().$el);
    });
  });

}).call(this);
