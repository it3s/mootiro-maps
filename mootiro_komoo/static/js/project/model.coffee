define [
    'jquery',
    'backbone'
], ($, Backbone) ->
    Project = Backbone.Model.extend
        urlRoot: '/projects/'

        addObject: (obj) ->
            dfd = $.Deferred()
            $.post('/project/add_related/',
                object_id: obj.get 'id'
                content_type: obj.get 'content_type'
                project_id: @get 'id'
            , 'json')
            .success (data) =>
                if data.success
                    dfd.resolve this
                else
                    dfd.reject this, 'Falha ao relacionar este objeto ao projeto selecionado'
            .error () =>
                dfd.reject this, 'Falha no servidor'

            return dfd.promise()

    Projects = Backbone.Collection.extend
        model: Project

        parse: (response) -> response.results

    Project: Project
    Projects: Projects
