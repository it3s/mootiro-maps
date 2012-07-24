(function() {
  var $;

  $ = jQuery;

  window.Contribution = Backbone.Model.extend({
    bla: function() {
      return console.log('blaa');
    }
  });

  window.Contributions = Backbone.Collection.extend({
    model: Contribution
  });

  window.ContributionView = Backbone.View.extend({
    tagName: 'li',
    className: 'contribution',
    initialize: function() {
      _.bindAll(this, 'render');
      return this.template = _.template($('#contribution-template').html());
    },
    render: function() {
      var renderedContent;
      renderedContent = this.template(this.model.toJSON());
      $(this.el).html(renderedContent);
      return this;
    }
  });

  window.ContributionsView = Backbone.View.extend({});

}).call(this);
