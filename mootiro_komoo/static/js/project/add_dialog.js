(function() {

  define(['jquery', 'underscore', 'backbone', 'project/model', 'widgets/autocomplete', 'text!templates/project/_add_dialog.html', 'bootstrap'], function($, _, Backbone, Model, AutocompleteView, tplt) {
    'use strict';
    var AddDialogView, ProjectAutocompleteView;
    ProjectAutocompleteView = AutocompleteView.extend({
      inputName: 'project',
      autocompleteSource: '/project/search_by_name',
      className: 'project_autocomplete'
    });
    return AddDialogView = Backbone.View.extend({
      events: {
        'click .save': 'onSaveBtnClick',
        'click .cancel': 'onCancelBtnClick'
      },
      initialize: function() {
        var _this = this;
        _.bindAll(this, 'render');
        this.template = _.template(tplt);
        this.autocomplete = new ProjectAutocompleteView().render();
        return this.autocomplete.$input.on('autocompleteselect', function(event, ui) {
          return _this.onProjectSelected(ui.item);
        });
      },
      open: function() {
        $('body').append(this.$el);
        this.$('.dialog').modal('show');
        return this;
      },
      close: function() {
        this.$('.dialog').modal('hide');
        return this;
      },
      clear: function() {
        this.autocomplete.clear();
        this.$('.msg').html('');
        this.$('.save').addClass('disabled');
        return this;
      },
      onCancelBtnClick: function() {
        this.close();
        return false;
      },
      onSaveBtnClick: function() {
        var project, projectId,
          _this = this;
        if (this.$('.save').hasClass('disabled')) false;
        projectId = this.autocomplete.val();
        if (projectId) {
          project = new Model.Project({
            id: projectId
          });
          project.fetch();
          project.addObject(this.model).done(function(project) {
            return _this.trigger('saved', project);
          }).fail(function(project, msg) {
            return _this.trigger('failed', project, msg);
          });
        }
        return false;
      },
      onProjectSelected: function(item) {
        this.$('.msg').html("<p>Este objeto será adicionado ao projeto <strong> " + item.label + " </strong></p>");
        return this.$('.save').removeClass('disabled');
      },
      render: function() {
        var renderedContent,
          _this = this;
        renderedContent = this.template();
        this.$el.html(renderedContent);
        this.$('.project-selector').append(this.autocomplete.$el);
        this.$('.dialog').on('hide', function() {
          return _this.clear();
        });
        return this;
      }
    });
  });

}).call(this);
