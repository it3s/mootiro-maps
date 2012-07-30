
$ = jQuery

$ () ->
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

    $('#form-profile').komooFormHintBoxes
        'contact':
            hint: 'Este Contanto ficará visível para outros usuários do MootiroMaps!'
            top: '30%'


    # message box close when x button is clicked
    $('.alert .close').live 'click', () ->
        $(this).parent().slideUp()


