require [
    'jquery',
    'backbone',
    'community/model',
    'project/box'
], ($, Backbone, CommunityModel, ProjectBox) ->

    community = new CommunityModel.Community(KomooNS.object or {})
    projectsBox = new ProjectBox
        model: community
        collection: community.projects
    window.c = community

    # We're not providing projects with community json, so fetch it
    if community.projects.length == 0
        community.projects.fetch()

    $ () ->
        $('#projectsBox').append(projectsBox.render().$el)
