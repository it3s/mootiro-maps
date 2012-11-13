(function() {

  define(['jquery', 'backbone'], function($, Backbone) {
    var Project, Projects;
    Project = Backbone.Model.extend({
      urlRoot: '/projects/',
      addObject: function(obj) {
        var dfd,
          _this = this;
        dfd = $.Deferred();
        $.post('/project/add_related/', {
          object_id: obj.get('id'),
          content_type: obj.get('content_type'),
          project_id: this.get('id')
        }, 'json').success(function(data) {
          if (data.success) {
            return dfd.resolve(_this);
          } else {
            return dfd.reject(_this, 'Falha ao relacionar este objeto ao projeto selecionado');
          }
        }).error(function() {
          return dfd.reject(_this, 'Falha no servidor');
        });
        return dfd.promise();
      }
    });
    Projects = Backbone.Collection.extend({
      model: Project,
      parse: function(response) {
        return response.results;
      }
    });
    return {
      Project: Project,
      Projects: Projects
    };
  });

}).call(this);
