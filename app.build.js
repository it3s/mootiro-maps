({
    findNestedDependencies: true,

    appDir: '',
    baseUrl: '.build',
    dir: '.build/min',

    paths: {
        'jquery': 'empty:',
        'underscore': 'empty:',
        'backbone': 'empty:',
        'templates': '../mootiro_maps/static/templates',
        'async': '../mootiro_maps/static/lib/requirejs/async',
        'goog': '../mootiro_maps/static/lib/requirejs/goog',
        'text': '../mootiro_maps/static/lib/requirejs/text',
        'propertyParser': '../mootiro_maps/static/lib/requirejs/propertyParser',
        'infobox': 'empty:',
        'markerclusterer': 'empty:'
    },

    name: 'app',
    include: [
        'app'
     ],

    excludeShallow: [
    ]
})
