(function() {

  define([], function() {
    return requirejs.onError = function(err) {
      if (err.requireType === 'timeout') {
        return require(['utils'], function() {
          errorMessage('Timeout', "Ocorreu uma falha ao carregar alguns serviços externos. Partes do Mootiro Maps poderão não funcionar corretamente.");
          return typeof console !== "undefined" && console !== null ? console.error(err) : void 0;
        });
      } else {
        throw err;
      }
    };
  });

}).call(this);
