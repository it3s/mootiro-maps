(function() {
  var $;

  $ = jQuery;

  window.Contribution = Backbone.Model.extend({});

  window.Contributions = Backbone.Collection.extend({
    model: Contribution
  });

  window.ContributionView = Backbone.View.extend({
    tagName: 'div',
    className: 'contribution',
    initialize: function() {
      _.bindAll(this, 'render');
      this.template = _.template($('#contribution-template').html());
      return console.log('Starting View for model', this.model.toJSON());
    },
    render: function() {
      var renderedContent;
      renderedContent = this.template(this.model.toJSON());
      $(this.el).html(renderedContent);
      return this;
    }
  });

  window.ContributionsView = Backbone.View.extend({
    initialize: function() {
      _.bindAll(this, 'render');
      this.template = _.template($("#contributions-template").html());
      return this.collection.bind('reset', this.render);
    },
    render: function() {
      var $contributions, collection;
      $(this.el).html(this.template({}));
      $contributions = this.$('.profile-cp-contributions');
      collection = this.collection;
      collection.each(function(contrib) {
        var view;
        view = new ContributionView({
          model: contrib,
          collection: collection
        });
        return $contributions.append(view.render().el);
      });
      return this;
    }
  });

  $(function() {
    var contributionsView, loaded_contributions;
    loaded_contributions = new Contributions();
    loaded_contributions.reset(window.KomooNS.contributions);
    contributionsView = new ContributionsView({
      collection: loaded_contributions
    });
    return $('.profile-central-pane').append(contributionsView.render().el);
  });

}).call(this);
