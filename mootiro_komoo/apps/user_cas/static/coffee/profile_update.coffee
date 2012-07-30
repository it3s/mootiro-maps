
$ = jQuery

#
# ======== Backbone => MVC for signatures settings =========
#
window.Signature = Backbone.Model.extend
    imageName: () ->
        if @model_name is 'organizationbranch'
            modelName = 'organization'
        else
            modelName = @model_name
        # TODO we need proper images (using added only for testing)
        "/static/img/updates-page/#{modelName}-added.png"

    toJSON: (attr) ->
        defaultJSON = Backbone.Model.prototype.toJSON.call this, attr
        _.extend defaultJSON, {
            imageName: @imageName
        }


window.SignatureView = Backbone.View.extend
    className: 'signature'
    initialize: () ->
        _.bindAll this, 'render'
        @template = _.template $('#signature-template').html()

    render: () ->
        console.log 'rendering model: ', @model.toJSON()
        renderedContent = @template @model.toJSON()
        $(@el).html renderedContent
        this


window.SignaturesList = Backbone.Collection.extend
    model: Signature


window.SignaturesListView = Backbone.View.extend
    initialize: () ->
        _.bindAll this, 'render'
        @template = _.template $('#signatures-list-collection').html()
        @collection.bind 'reset', @render

    render: () ->
        $(@el).html @template({})
        $signatures = this.$ '.signatures-list'

        collection = @collection
        collection.each (sign) ->
            view = new SignatureView
                model: sign
                collection: collection
            $signatures.append view.render().el
        this


# jQuery -> on document ready
$ () ->

    #
    #=========  Public Settings Tab ==========
    #
    $('#form-profile').ajaxform
        clean: false
        onSuccess: (data) ->
            console.log data
            $messageBox = $ '.form-message-box'
            if $messageBox.length
                $messageBox.remove()
            msgTemplate = _.template $('#form-message-box').html()
            renderedContent = msgTemplate
                msg: gettext 'Seus dados públicos foram salvos com sucesso!'

            $('#form-profile .form-actions').before renderedContent
            $('#form-profile .alert').fadeIn()
            false


    $('#form-profile').komooFormHintBoxes
        'contact':
            hint: 'Este Contanto ficará visível para outros usuários do MootiroMaps!'
            top: '30%'


    # message box close when x button is clicked
    $('.alert .close').live 'click', () ->
        $(this).parent().slideUp()

    #
    #========== Personal Settings Tab ================
    #
    $('#form-personal').ajaxform
        clean: false
        onSuccess: (data) ->
            console.log data
            $messageBox = $ '.form-message-box'
            if $messageBox.length
                $messageBox.remove()
            msgTemplate = _.template $('#form-message-box').html()
            renderedContent = msgTemplate
                msg: gettext 'Seus dados pessoais foram salvos com sucesso!'

            $('#form-personal .form-actions').before renderedContent
            $('#form-personal .alert').fadeIn()
            false

    #
    #=========== Signatures Settings Tab ==============
    #
    loadedSignatures = new SignaturesList()
    loadedSignatures.reset window.KomooNS.signatures

    signaturesListView = new SignaturesListView
        collection: loadedSignatures

    $('.signatures-list-wrapper').append signaturesListView.render().el
