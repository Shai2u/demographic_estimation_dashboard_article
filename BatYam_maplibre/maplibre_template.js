var size = 200;
// implementation of CustomLayerInterface to draw a pulsing dot icon on the map
// see https://maplibre.org/maplibre-gl-js-docs/api/properties/#customlayerinterface for more info
var pulsingDot = {
    width: size,
    height: size,
    data: new Uint8Array(size * size * 4),

    // get rendering context for the map canvas when layer is added to the map
    onAdd: function () {
        var canvas = document.createElement('canvas');
        canvas.width = this.width;
        canvas.height = this.height;
        this.context = canvas.getContext('2d');
    },

    // called once before every frame where the icon will be used
    render: function () {
        var duration = 1000;
        var t = (performance.now() % duration) / duration;

        var radius = (size / 2) * 0.3;
        var outerRadius = (size / 2) * 0.7 * t + radius;
        var context = this.context;

        // draw outer circle
        context.clearRect(0, 0, this.width, this.height);
        context.beginPath();
        context.arc(
            this.width / 2,
            this.height / 2,
            outerRadius,
            0,
            Math.PI * 2
        );
        context.fillStyle = 'rgba(255, 200, 200,' + (1 - t) + ')';
        context.fill();

        // draw inner circle
        context.beginPath();
        context.arc(
            this.width / 2,
            this.height / 2,
            radius,
            0,
            Math.PI * 2
        );
        context.fillStyle = '#F9C70F';
        context.strokeStyle = 'white';
        context.lineWidth = 2 + 4 * (1 - t);
        context.fill();
        context.stroke();

        // update this image's data with data from the canvas
        this.data = context.getImageData(
            0,
            0,
            this.width,
            this.height
        ).data;

        // continuously repaint the map, resulting in the smooth animation of the dot
        map.triggerRepaint();

        // return `true` to let the map know that the image was updated
        return true;
    }
};


var map = new maplibregl.Map({
    container: 'map',

    style: 'https://api.maptiler.com/maps/streets/style.json?key=khvVGD9ThOCYQHMkBNt5', // stylesheet location
    center: [34.743, 32.025], // starting position [lng, lat]
    zoom: 17, // starting zoom
    pitch: 60, // pitch in degrees
    bearing: 10, // bearing in degrees

});

map.on('load', () => {
    var url = window.location.pathname;
    var filename = url.substring(url.lastIndexOf('/') + 1);
    date_ = filename.split('.').slice(0, -1).join('.');
    console.log(date_);
    date_int = parseInt(date_);

    map.addSource('Statistical_Borders', {
        type: 'geojson',
        // Use a URL for the value for the `data` property.
        data: 'https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/statistical_tract_4326.geojson'
    });
    map.addSource('Background_Buildings', {
        type: 'geojson',
        // Use a URL for the value for the `data` property.
        data: 'https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/ts_test_aug_10_download.geojson'
    });

    map.addSource('Crane_Points', {
        type: 'geojson',
        // Use a URL for the value for the `data` property.
        data: 'https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/crane_points_4326.geojson'
    });

    map.addSource('Construction_sites', {
        type: 'geojson',
        // Use a URL for the value for the `data` property.
        data: 'https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/construction_sites.geojson'
    });

    map.loadImage(
        'https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/lawrence_Crane.png',
        function (error, image) {
            if (error) throw error;
            map.addImage('crane-marker', image);
        }
    )
    map.addImage('pulsing-dot', pulsingDot, { pixelRatio: 2 });

    map.addLayer({
        'id': 'Statistical_Borders',
        'type': 'line',
        'source': 'Statistical_Borders',
        'layout': {},
        'paint': {
            'line-color': 'rgba(0, 112, 255, 0.4)',
            'line-width': 3,
            'line-dasharray': [2, 1],
        }

    });
    // map.addLayer({
    //     'id': 'Building Before',
    //     'type': 'fill-extrusion',
    //     'source': 'Background_Buildings',
    //     'layout': {},
    //     'paint': {
    //         'fill-extrusion-color': '#ed7d30',

    //         'fill-extrusion-height': ['get', 'height'],
    //         'fill-extrusion-opacity': 0.6
    //     },
    //     'filter': ["all", ['==', 'status', 'Building before'],
    //         ['<', 'start_date_int', date_],
    //         ['>', 'end_date_int', date_]]
    // });


    map.addLayer({
        'id': 'CranesImages',
        'type': 'symbol',
        'source': 'Crane_Points',
        'layout': {
            'icon-image': 'crane-marker',
            'icon-size': ["*", 0.05, ['get', 'floors']],
            'icon-allow-overlap': true
        },
        'filter': ["all", ['==', 'status', 'Construction'],
            ['<', 'start_date_int', date_int],
            ['>', 'end_date_int', date_int]]
    });



    map.addLayer({
        'id': 'Cranes',
        'type': 'symbol',
        'source': 'Construction_sites',
        'layout': {
            'icon-image': 'pulsing-dot',
            'icon-allow-overlap': true
        },
        'filter': ["all", ['==', 'status', 'Construction'],
            ['<', 'start_date_int', date_int],
            ['>', 'end_date_int', date_int]]
    });





    //use this instead of date_
    map.addLayer({
        'id': 'Building After',
        'type': 'fill-extrusion',
        'source': 'Background_Buildings',
        'layout': {},
        'paint': {
            'fill-extrusion-color':
            {
                property: 'project_ty', // this will be your density property form you geojson
                stops: [
                    [1, 'rgba(55, 103, 153, 0.8)'],
                    [2, 'rgba(96, 144, 199,0.8)'],
                    [3, 'rgba(190, 210, 255,0.8)'],

                ]
            },

            'fill-extrusion-height': ['get', 'height'],
            'fill-extrusion-opacity': 0.6
        },
        'filter': ["all", ['==', 'status', 'Building after'],
            ['<', 'start_date_int', date_int],
            ['>', 'end_date_int', date_int]]
        // 'filter': ["all", ['==', 'status', 'Building after'],
        //     ['>=', 'start_date_int', date_int],
        //     ['<=', 'end_date_int', date_int]]
    });

    //use this instead of date_
    map.addLayer({
        'id': 'Building Before',
        'type': 'fill-extrusion',
        'source': 'Background_Buildings',
        'layout': {},
        'paint': {
            'fill-extrusion-color': '#808080',

            'fill-extrusion-height': ['get', 'height'],
            'fill-extrusion-opacity': 0.6
        },
        'filter': ["all", ['==', 'status', 'Building before'],
            ['<', 'start_date_int', date_int],
            ['>', 'end_date_int', date_int]]
    });

    // //use this instead of date_
    // map.addLayer({
    //     'id': 'Building Construction',
    //     'type': 'fill-extrusion',
    //     'source': 'Background_Buildings',
    //     'layout': {},
    //     'paint': {
    //         'fill-extrusion-color': '#F9C70F',

    //         'fill-extrusion-height': ['get', 'height'],
    //         'fill-extrusion-opacity': 0.6
    //     },
    //     'filter': ["all", ['==', 'status', 'Construction'],
    //         ['<=', 'start_date_int', date_int],
    //         ['>=', 'end_date_int', date_int]]
    // });
    // //test

    map.on('click', 'Building After', (e) => {
        new maplibregl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(`
            <b>Project type:</b> ${e.features[0].properties.project_ty} 🏗<br/>
            <b>Building Address Hebrew</b>: ${e.features[0].properties.hebrew_adr}<br/>
            <b>Project Number:</b> ${e.features[0].properties.project_nu}<br/>
            <b>Units:</b> ${e.features[0].properties.units} <br/>
            <b>Floors:</b> ${e.features[0].properties.floors} <br/>
            <b>Status:</b> ${e.features[0].properties.status} <br/>
            <b>Start Date:</b> ${e.features[0].properties.start_date_int} <br/>
            <b>End Date:</b> ${e.features[0].properties.end_date_int} <br/>
            <b>Website Date:</b> ${date_int}<br/>
            ${e.features[0].properties.start_date_int < date_int}<br/>
            ${e.features[0].properties.end_date_int > date_int} <br/>

            `)
            .addTo(map);
    });

    // Change the cursor to a pointer when
    // the mouse is over the states layer.
    map.on('mouseenter', 'Building After', () => {
        map.getCanvas().style.cursor = 'pointer';
    });

    // Change the cursor back to a pointer
    // when it leaves the states layer.
    map.on('mouseleave', 'Building After', () => {
        map.getCanvas().style.cursor = '';
    });
    // ['==', 'status', 'Building after'],

});
// add 3D render at a point
// https://stackoverflow.com/questions/46701072/how-to-put-threejs-building-on-mapbox-to-its-real-place
//https://github.com/jscastro76/threebox
//https://docs.mapbox.com/mapbox-gl-js/example/add-3d-model/