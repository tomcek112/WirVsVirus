(function() {
    const cameras = new Map();
    const previousCameras = new Map();
    const cameraValues = new Map();
    const previousCameraValues = new Map();
    //let startDate = new Date(Date.now() - 604800000);
    let startDate = new Date("2020-03-22");
    let endDate = new Date("2020-03-23");
    let redLayer;
    let greenLayer;
    let map;

    window.addEventListener("DOMContentLoaded", () => {
        fetchObservations(startDate, endDate);
        setDateDOM(startDate, "start");
        setDateDOM(endDate, "end")

        document.querySelector("#start").addEventListener("input", (e) => {
            startDate = new Date(e.target.value);
            fetchObservations(startDate, endDate);
        });

        document.querySelector("#end").addEventListener("input", (e) => {
            endDate = new Date(e.target.value);
            fetchObservations(startDate, endDate);
        });
    });

    function fetchObservations(from, to) {
        cameraValues.clear();
        cameras.clear();

        const previousUrl = "/observations" + (startDate ? `?from=${("" + (from.getTime() - 604800000)).substr(0, 10)}&to=${("" + from.getTime()).substr(0, 10)}` : "");
        const url = "/observations" + (startDate ? `?from=${("" + from.getTime()).substr(0, 10)}&to=${("" + to.getTime()).substr(0, 10)}` : "");
        
        Promise.all([fetch(previousUrl), fetch(url)]).then(([presp, resp]) => {
            Promise.all([presp.json(), resp.json()]).then(([po, o]) => {
                const previousObservations = po.observations;
                const observations = o.observations;
                observations.forEach(o => {
                    cameras.has(o.camera_id) ? cameras.set(o.camera_id, [...cameras.get(o.camera_id), o]) : cameras.set(o.camera_id, [o])
                })

                previousObservations.forEach(o => {
                    previousCameras.has(o.camera_id) ? previousCameras.set(o.camera_id, [...previousCameras.get(o.camera_id), o]) : previousCameras.set(o.camera_id, [o])
                })
        
                console.log(cameras);
        
                Array.from(cameras.keys()).forEach(k => {
                    cs = cameras.get(k).map(c => c.count);
                    cameraValues.set(k, cs.reduce((p, c) => p + c, 0)/cs.length);
                })

                Array.from(previousCameras.keys()).forEach(k => {
                    cs = previousCameras.get(k).map(c => c.count);
                    previousCameraValues.set(k, cs.reduce((p, c) => p + c, 0)/cs.length);
                })
        
                const redCircles = [];
                const greenCircles = [];
        
                Array.from(cameraValues.keys()).forEach((k, i) => {
                    const isRed = cameraValues.get(k) > previousCameraValues.get(k);
                    const circ = new ol.geom.Point(ol.proj.fromLonLat([+cameras.get(k)[0].long, +cameras.get(k)[0].lat]));
                    (isRed ? redCircles : greenCircles).push(new ol.Feature({
                            geometry: circ,
                            size: 8000*cameraValues.get(k)
                        }
                    ));
                })

                console.log(ol.geom)
                
                const redSource = new ol.source.Vector({
                    projection: 'EPSG:4326',
                    features: redCircles
                });

                const greenSource = new ol.source.Vector({
                    projection: 'EPSG:4326',
                    features: greenCircles
                });
        
                const redStyle = new ol.style.Style({
                    fill: new ol.style.Fill({
                        color: 'rgba(255, 100, 50, 0.3)'
                    }),
                    stroke: new ol.style.Stroke({
                        width: 2,
                        color: 'rgba(255, 100, 50, 0.3)'
                    }),
                    image: new ol.style.Circle({
                        fill: new ol.style.Fill({
                            color: 'rgba(255, 100, 50, 0.3)'
                        }),
                        stroke: new ol.style.Stroke({
                            width: 1,
                            color: 'rgba(255, 100, 50, 0.3)'
                        }),
                        radius: 10
                    }),
                });

                const greenStyle = new ol.style.Style({
                    fill: new ol.style.Fill({
                        color: 'rgba(55, 200, 150, 0.5)'
                    }),
                    stroke: new ol.style.Stroke({
                        width: 2,
                        color: 'rgba(55, 200, 150, 0.5)'
                    }),
                    image: new ol.style.Circle({
                        fill: new ol.style.Fill({
                            color: 'rgba(55, 200, 150, 0.5)'
                        }),
                        stroke: new ol.style.Stroke({
                            width: 1,
                            color: 'rgba(55, 200, 150, 0.8)'
                        }),
                        radius: 10
                    }),
                });

                if(map) {
                    map.removeLayer(redLayer);
                    map.removeLayer(greenLayer);
                }
        
                redLayer = new ol.layer.Vector({
                    source: redSource,
                    style: redStyle
                });

                greenLayer = new ol.layer.Vector({
                    source: greenSource,
                    style: greenStyle
                });

                if(map) {
                    map.addLayer(redLayer);
                    map.addLayer(greenLayer);
                } else {
                    map = new ol.Map({
                        target: 'map',
                        renderer: 'canvas',
                        layers: [
                          new ol.layer.Tile({
                            source: new ol.source.OSM()
                          }),
                          redLayer,
                          greenLayer
                        ],
                        view: new ol.View({
                          center: ol.proj.fromLonLat([10.8142194, 50.7171052]),
                          zoom: 6
                        })
                    });
                }

                console.log(map);
        
                console.log(cameraValues);
            })
        })
    }

    function setDateDOM(date, id) {
        document.querySelector(`#${id}`).value = date.toISOString().substr(0, 10);
    }
})()

