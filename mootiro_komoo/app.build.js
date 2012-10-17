({
    findNestedDependencies: true,

    appDir: '',
    baseUrl: '.build',
    dir: '.build/min',

    paths: {
        'jquery': 'empty:',
        'underscore': 'empty:',
        'backbone': 'empty:',
        'async': '../static/lib/requirejs/async',
        'goog': '../static/lib/requirejs/goog',
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
