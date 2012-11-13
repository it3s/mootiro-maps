define [
    'backbone',
    'project/model',
    'utils'
], (Backbone, ProjectModel) ->
    Community = Backbone.Model.extend
        urlRoot: '/community/'

        initialize: () ->
            @projects = nestCollection this, 'projects', new ProjectModel.Projects(@get 'projects')
            @projects.url = "#{@url()}/projects/"


    Communities = Backbone.Collection.extend
        model: Community

        parse: (response) -> response.results

    Community: Community
    Communities: Communities
