const cameras = new Map();
const cameraValues = new Map();

fetch("/observations").then(resp => {
    resp.json().then(({observations}) => {
        console.log(observations);
        observations.forEach(o => {
            cameras.has(o.camera_id) ? cameras.set(o.camera_id, [...cameras.get(o.camera_id), o]) : cameras.set(o.camera_id, [o])
        })

        console.log(cameras);

        Array.from(cameras.keys()).forEach(k => {
            cs = cameras.get(k).map(c => c.count);
            cameraValues.set(k, cs.reduce((p, c) => p + c, 0));
        })

        const circles = [];

        Array.from(cameraValues.keys()).forEach(k => {
            const circ = new ol.geom.Circle(ol.proj.fromLonLat([+cameras.get(k)[0].long, +cameras.get(k)[0].lat]), 2000*cameraValues.get(k));
            circles.push(new ol.Feature(
                circ
            ));
        })

        console.log(circles)

        const vectorSource = new ol.source.Vector({
            projection: 'EPSG:4326',
            features: circles
        });

        const style = new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'rgba(255, 100, 50, 0.3)'
            }),
            stroke: new ol.style.Stroke({
                width: 2,
                color: 'rgba(255, 100, 50, 0.8)'
            }),
            image: new ol.style.Circle({
                fill: new ol.style.Fill({
                    color: 'rgba(55, 200, 150, 0.5)'
                }),
                stroke: new ol.style.Stroke({
                    width: 1,
                    color: 'rgba(55, 200, 150, 0.8)'
                }),
                radius: 7
            }),
        });

        const vectorLayer = new ol.layer.Vector({
            source: vectorSource,
            style: style
        });

        const map = new ol.Map({
            target: 'map',
            renderer: 'canvas',
            layers: [
              new ol.layer.Tile({
                source: new ol.source.OSM()
              }),
              vectorLayer
            ],
            view: new ol.View({
              center: ol.proj.fromLonLat([10.8142194, 50.7171052]),
              zoom: 6
            })
        });

        console.log(cameraValues);
    })
})