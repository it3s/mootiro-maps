({
    appDir: '',
    baseUrl: '.build',
    dir: '.build/min',
    paths: {
        'jquery': "empty:",
        'underscore': "empty:",
        'backbone': "empty:",
        'async': '../apps/main/static/lib/requirejs/async',
        'goog': '../apps/main/static/lib/requirejs/goog',
        'propertyParser': '../apps/main/static/lib/requirejs/propertyParser'
    },
    modules: [
        {
            name: 'app',
            include: [
                'app',
                'map/maps'
            ]
        }
    ]
})
