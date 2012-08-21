(function() {

  define(['lib/underscore-min', 'lib/backbone-min'], function() {
    var $;
    $ = jQuery;
    window.PartnersLogo = Backbone.Model.extend({
      toJSON: function(attr) {
        return Backbone.Model.prototype.toJSON.call(this, attr);
      }
    });
    window.PartnersLogoView = Backbone.View.extend({
      className: 'partner-logo',
      tagName: 'li',
      initialize: function() {
        _.bindAll(this, 'render');
        return this.template = _.template('<img src="<%= url %>" />');
      },
      render: function() {
        var renderedContent;
        console.log('rendering model: ', this.model.toJSON());
        renderedContent = this.template(this.model.toJSON());
        $(this.el).html(renderedContent);
        return this;
      }
    });
    window.PartnersLogos = Backbone.Collection.extend({
      model: PartnersLogo
    });
    window.PartnersLogosView = Backbone.View.extend({
      initialize: function() {
        _.bindAll(this, 'render');
        this.template = _.template('<ul class="partners-logo-list"></ul>');
        return this.collection.bind('reset', this.render);
      },
      render: function() {
        var $logos, collection;
        collection = this.collection;
        this.$el.html(this.template());
        $logos = this.$('.partners-logo-list');
        collection.each(function(logo) {
          var view;
          console.log('-----', logo);
          view = new PartnersLogoView({
            model: logo
          });
          return $logos.append(view.render().$el);
        });
        return this;
      }
    });
    return $(function() {
      var panelInfoView, partnersLogosView;
      KomooNS.drawFeaturesList();
      panelInfoView = new PanelInfoView({
        model: new PanelInfo(KomooNS.obj)
      });
      $('.panel-info-wrapper').append(panelInfoView.render().$el);
      partnersLogosView = new PartnersLogosView({
        collection: new PartnersLogos().reset(KomooNS.obj.partners_logo)
      });
      return $('.panel-info-wrapper').append(partnersLogosView.render().$el);
    });
  });

}).call(this);
