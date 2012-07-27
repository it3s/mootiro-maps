(function() {
  var $;

  $ = jQuery;

  window.Contribution = Backbone.Model.extend({
    imageName: function() {
      var modelName;
      if (this.model_name === 'organizationbranch') {
        modelName = 'organization';
      } else {
        modelName = this.model_name;
      }
      return "/static/img/updates-page/" + modelName + "-" + (this.typeExt()) + ".png";
    },
    typeExt: function() {
      return {
        A: gettext('added'),
        E: gettext('edited'),
        C: gettext('discussed'),
        D: gettext('deleted')
      }[this.type];
    },
    modelPrettyName: function() {
      var namesMapper;
      namesMapper = {
        organization: gettext('Organization'),
        organizationbranch: gettext('Organization'),
        need: gettext('Need'),
        community: gettext('Community'),
        resource: gettext('Resource')
      };
      return namesMapper[this.model_name];
    },
    actionDesc: function() {
      var at_trans;
      at_trans = gettext('at');
      return "" + (this.modelPrettyName()) + " " + (this.typeExt()) + " " + at_trans + " " + this.date + ".";
    },
    toJSON: function(attr) {
      var defaultJSON;
      defaultJSON = Backbone.Model.prototype.toJSON.call(this, attr);
      return _.extend(defaultJSON, {
        imageName: this.imageName,
        actionDesc: this.actionDesc,
        typeExt: this.typeExt,
        modelPrettyName: this.modelPrettyName
      });
    }
  });

  window.Contributions = Backbone.Collection.extend({
    model: Contribution
  });

  window.ContributionView = Backbone.View.extend({
    tagName: 'div',
    className: 'contribution',
    initialize: function() {
      _.bindAll(this, 'render');
      return this.template = _.template($('#contribution-template').html());
    },
    render: function() {
      var renderedContent;
      console.log('rendering model', this.model.toJSON());
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
