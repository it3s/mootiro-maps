requirejs.config
    baseUrl: '/static/js'
    paths:
        map: 'map'
        vendor: 'vendor'
        lib: '../lib'
        'ad-gallery': '../ad_gallery/jquery.ad-gallery.min'
    shim:
        'lib/backbone-min':
            deps: ['lib/underscore-min', 'lib/jquery-1.7.1.min']
            exports: 'Backbone'

