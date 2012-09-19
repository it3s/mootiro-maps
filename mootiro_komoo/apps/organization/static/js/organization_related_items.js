(function() {

  define(['jquery', 'underscore', 'backbone', 'related_items_panel'], function($, _, Backbone, drawFeaturesList) {
    window.OrganizationFeaturesView = FeaturesView.extend({
      title: function(count) {
        var msg;
        msg = this.type === 'SelfOrganizationBranch' ? ngettext("%s point on map", "%s points on map", count) : this.type === 'OrganizationBranch' ? ngettext("Supported %s organization", "Supported %s organizations", count) : this.type === 'Community' ? ngettext("On %s community", "On %s communities", count) : this.type === 'Resource' ? ngettext("Supported %s resource", "Supported %s resources", count) : this.type === 'Need' ? ngettext("Supported %s need", "Supported %s needs", count) : "";
        return interpolate(msg, [count]);
      }
    });
    return $(function() {
      var panelInfoView;
      drawFeaturesList(OrganizationFeaturesView);
      panelInfoView = new PanelInfoView({
        model: new PanelInfo(KomooNS.obj)
      });
      return $('.panel-info-wrapper').append(panelInfoView.render().$el);
    });
  });

}).call(this);
