({
    findNestedDependencies: true,

    appDir: '',
    baseUrl: '.build',
    dir: '.build/min',

    paths: {
        'jquery': 'empty:',
        'underscore': 'empty:',
        'backbone': 'empty:',
        'templates': '../static/templates',
        'async': '../static/lib/requirejs/async',
        'goog': '../static/lib/requirejs/goog',
        'text': '../static/lib/requirejs/text',
        'propertyParser': '../static/lib/requirejs/propertyParser',
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
