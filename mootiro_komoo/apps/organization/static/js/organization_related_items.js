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
    return $(function() {
      var panelInfoView;
      panelInfoView = new PanelInfoView({
        model: new PanelInfo(KomooNS.obj)
      });
      return $('.panel-info-wrapper').append(panelInfoView.render().$el);
    });
  });

}).call(this);
