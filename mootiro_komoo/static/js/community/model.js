(function() {

  define(['backbone', 'project/model', 'utils'], function(Backbone, ProjectModel) {
    var Communities, Community;
    Community = Backbone.Model.extend({
      urlRoot: '/community/',
      initialize: function() {
        this.projects = nestCollection(this, 'projects', new ProjectModel.Projects(this.get('projects')));
        return this.projects.url = "" + (this.url()) + "/projects/";
      }
    });
    Communities = Backbone.Collection.extend({
      model: Community,
      parse: function(response) {
        return response.results;
      }
    });
    return {
      Community: Community,
      Communities: Communities
    };
  });

}).call(this);
