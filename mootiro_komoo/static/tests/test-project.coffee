require [
    'jquery',
    'sinon',
    'project/model',
    'project/box',
    'project/add_dialog'
], ($, sinon, Model, BoxView, AddDialogView) ->

    window.gettext ?= (s) -> s

    module 'Project',
        setup: =>
        teardown: =>

    test 'BoxView constructor', ->
        p = new BoxView
            collection: new Model.Projects().reset [
                {name: 'first project'},
                {name: 'second project'},
                {name: 'last project'}
            ]
        p.render()

        # Verify some elements creation
        ok p.$el

        notEqual p.$('.add').text(), '', 'Add button should have text'

        $ul = p.$ '.list'
        $li = $ul.find 'li'
        equal $li.eq(0).text(), 'first project', 'Should add project to list'
        equal $li.eq(1).text(), 'second project', 'Should add project to list'
        equal $li.eq(2).text(), 'last project', 'Should add project to list'


    test 'BoxView Open dialog on button click', ->
        p = new BoxView().render()

        spy = sinon.spy p, 'openAddDialog'
        p.$('.add').click()

        ok spy.calledOnce


    test 'AddDialogView constructor', ->
        d = new AddDialogView().render()

        ok d.autocomplete, 'Should have autocoplete widget'
        ok not d.$('.dialog').is ':visible', 'Should init closed'

    test 'AddDialogView open', ->
        d = new AddDialogView().render()

        d.open()
        ok d.$('.dialog').is ':visible', 'Should be visible when opened'
