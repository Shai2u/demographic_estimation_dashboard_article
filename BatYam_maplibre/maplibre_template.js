var map = new maplibregl.Map({
    container: 'map',

    style: 'https://api.maptiler.com/maps/streets/style.json?key=khvVGD9ThOCYQHMkBNt5', // stylesheet location
    center: [34.743, 32.025], // starting position [lng, lat]
    zoom: 17, // starting zoom
    pitch: 60, // pitch in degrees
    bearing: 10, // bearing in degrees

});

map.on('load', () => {
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

    map.addSource('Cranes_Points_Prototype', {
        type: 'geojson',
        // Use a URL for the value for the `data` property.
        data: 'https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/buildings_for_dashboard_centroid_4326.geojson'
    });
    map.loadImage(
        'https://raw.githubusercontent.com/Shai2u/demographic_estimation_dashboard_article/main/dashboard/data/lawrence_Crane.png',
        function (error, image) {
            if (error) throw error;
            map.addImage('crane-marker', image);
        }
    )
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
    map.addLayer({
        'id': 'Building Before',
        'type': 'fill-extrusion',
        'source': 'Background_Buildings',
        'layout': {},
        'paint': {
            'fill-extrusion-color': '#ed7d30',

            'fill-extrusion-height': ['get', 'height'],
            'fill-extrusion-opacity': 0.6
        },
        'filter': ['==', 'status', 'Building before']

    });
    // map.addLayer({
    //     'id': 'Cranes',
    //     'type': 'circle',
    //     'source': 'Cranes_Points_Prototype',
    //     'paint': {
    //         'circle-radius': 6,
    //         'circle-color': '#B42222'
    //     },
    // });

    map.addLayer({
        'id': 'Cranes-images',
        'type': 'symbol',
        'source': 'Cranes_Points_Prototype',
        'layout': {
            'icon-image': 'crane-marker',
        },
        'filter': ["all", ['==', 'status', 'Construction'],
            ['<', 'start_date_int', date_],
            ['>', 'end_date_int', date_]]
    });

    var url = window.location.pathname;
    var filename = url.substring(url.lastIndexOf('/') + 1);
    date_ = filename.split('.').slice(0, -1).join('.');
    console.log(date_);
    date_ = parseInt(date_);
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
            ['<', 'start_date_int', date_],
            ['>', 'end_date_int', date_]]
        // ["all",
        //     ['<', 'start_date_int', date_],
        //     ['>', 'end_date_int', date_]
        // ]

    });
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