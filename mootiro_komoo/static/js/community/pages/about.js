(function() {

  require(['jquery', 'backbone', 'community/model', 'project/box'], function($, Backbone, CommunityModel, ProjectBox) {
    var community, projectsBox;
    community = new CommunityModel.Community(KomooNS.object || {});
    projectsBox = new ProjectBox({
      model: community,
      collection: community.projects
    });
    window.c = community;
    if (community.projects.length === 0) community.projects.fetch();
    return $(function() {
      return $('#projectsBox').append(projectsBox.render().$el);
    });
  });

}).call(this);
