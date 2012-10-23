(function() {

  define(['jquery', 'underscore', 'backbone', 'project/add_dialog', 'text!templates/project/_box.html', 'utils'], function($, _, Backbone, AddDialog, tplt) {
    'use strict';
    var BoxView, ProjectItemView;
    ProjectItemView = Backbone.View.extend({
      tagName: 'li',
      initialize: function() {
        _.bindAll(this, 'render');
        this.model.bind('change', this.render, this);
        return this.model.bind('destroy', this.remove, this);
      },
      render: function() {
        this.$el.html("<a href=\"" + (this.model.get('view_url')) + "\">" + (this.model.get('name')) + "</a>");
        return this;
      }
    });
    BoxView = Backbone.View.extend({
      className: 'project_box',
      events: {
        'click .add': 'onAddBtnClick'
      },
      initialize: function() {
        var _ref, _ref2,
          _this = this;
        _.bindAll(this, 'render');
        this.template = _.template(tplt);
        if ((_ref = this.collection) != null) _ref.bind('add', this.addOne, this);
        if ((_ref2 = this.collection) != null) {
          _ref2.bind('reset', this.render, this);
        }
        this.addDialog = new AddDialog({
          model: this.model
        }).render();
        this.addDialog.on('saved', function(project) {
          flash("Adicionado ao projeto " + (project.get('name')));
          _this.collection.add(project);
          return _this.addDialog.close();
        });
        return this.addDialog.on('failed', function(project, msg) {
          return flash("Falhou ao adicionar ao projeto " + (project.get('name')) + ": " + msg);
        });
      },
      addOne: function(project) {
        var view;
        view = new ProjectItemView({
          model: project
        });
        return this.$('.list').append(view.render().el);
      },
      addAll: function() {
        var _ref,
          _this = this;
        return (_ref = this.collection) != null ? _ref.each(function(project) {
          return _this.addOne(project);
        }) : void 0;
      },
      openAddDialog: function() {
        return this.addDialog.open();
      },
      onAddBtnClick: function() {
        this.openAddDialog();
        return false;
      },
      render: function() {
        var renderedContent;
        renderedContent = this.template({
          projects: this.collection
        });
        this.$el.html(renderedContent);
        this.addAll();
        return this;
      }
    });
    return BoxView;
  });

}).call(this);
