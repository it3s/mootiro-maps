define [], () ->
    requirejs.onError =  (err) ->
        if err.requireType == 'timeout'
            require ['utils'], () ->
                # TODO: i18n me
                errorMessage 'Timeout', "Ocorreu uma falha ao carregar alguns serviços externos. Partes do Mootiro Maps poderão não funcionar corretamente."
                console?.error err
        else
            thror err

