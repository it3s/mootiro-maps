({
    appDir: '',
    baseUrl: '.build',
    dir: '.build/min',
    paths: {
        jquery: "empty:",
        underscore: "empty:",
        backbone: "empty:"
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
