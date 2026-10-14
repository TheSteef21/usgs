const PANAMA_USGS_API = 'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minlatitude=6.5&maxlatitude=10.0&minlongitude=-83.5&maxlongitude=-76.5';
const GLOBAL_USGS_API = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson';

// Inicializar Mapa Leaflet
const map = L.map('map', { zoomControl: false }).setView([8.9, -80.2], 6);

L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Base/MapServer/tile/{z}/{y}/{x}', {
  maxZoom: 16,
  attribution: 'Esri, USGS, SADV41'
}).addTo(map);

function severity(m) {
  if (m >= 7) return { cls: 'crit', label: 'CRÍTICO' };
  if (m >= 6) return { cls: 'high', label: 'ALTO' };
  if (m >= 5) return { cls: 'med', label: 'MEDIO' };
  return { cls: '', label: 'VIGILANCIA' };
}

function isPanama(lat, lon) {
  return lat >= 6.5 && lat <= 10.0 && lon >= -83.5 && lon <= -76.5;
}

async function autoUpdateUSGS() {
  const list = document.getElementById('list');
  const listPA = document.getElementById('list-pa');

  try {
    const [rPa, rGlobal] = await Promise.all([
      fetch(PANAMA_USGS_API),
      fetch(GLOBAL_USGS_API)
    ]);

    const dataPa = await rPa.json();
    const dataGlobal = await rGlobal.json();

    if (list) list.innerHTML = '';
    if (listPA) listPA.innerHTML = '';

    // Limpiar marcadores existentes del mapa
    map.eachLayer(layer => {
      if (layer instanceof L.CircleMarker) map.removeLayer(layer);
    });

    // Renderizar eventos Panamá + Centroamérica
    dataPa.features.forEach(f => {
      const [lon, lat, depth] = f.geometry.coordinates;
      const { mag, place, time } = f.properties;
      const sev = severity(mag);
      const date = new Date(time).toLocaleString('es-PA');
      const color = sev.cls === 'crit' ? '#ff3b30' : (sev.cls === 'high' ? '#ff9500' : '#00e5ff');

      L.circleMarker([lat, lon], {
        radius: Math.max(4, mag * 2.5),
        color: color,
        fillColor: color,
        fillOpacity: 0.7,
        weight: 1
      }).addTo(map).bindPopup(`<b>M${mag}</b> ${place}<br>${date}<br>Prof: ${depth}km`);

      if (listPA) {
        listPA.innerHTML += `
          <div class="quake">
            <div>
              <div style="font-weight:bold; color:#eee;">${place}</div>
              <div style="font-size:10px; color:#666;">${date} • Prof: ${depth}km</div>
            </div>
            <span class="mag ${sev.cls}">M ${mag ? mag.toFixed(1) : '0'}</span>
          </div>
        `;
      }
    });

    // Renderizar sismos globales fuera del cuadrante
    dataGlobal.features.slice(0, 15).forEach(f => {
      const [lon, lat] = f.geometry.coordinates;
      const { mag, place, time } = f.properties;
      const sev = severity(mag);
      const date = new Date(time).toLocaleString('es-PA');

      if (!isPanama(lat, lon)) {
        L.circleMarker([lat, lon], {
          radius: Math.max(3, mag * 2),
          color: '#555',
          fillColor: '#888',
          fillOpacity: 0.4,
          weight: 1
        }).addTo(map).bindPopup(`<b>M${mag}</b> ${place}<br>${date}`);
      }

      if (list) {
        list.innerHTML += `
          <div class="quake">
            <div>
              <div style="font-weight:bold; color:#ccc;">${place}</div>
              <div style="font-size:10px; color:#555;">${date}</div>
            </div>
            <span class="mag ${sev.cls}">M ${mag ? mag.toFixed(1) : '0'}</span>
          </div>
        `;
      }
    });

  } catch(e) {
    console.error("Error al actualizar feed USGS:", e);
    if (listPA) listPA.innerHTML = '<div style="color:#ff3b30; font-size:11px;">Error al cargar datos en vivo</div>';
  }
}

// Ejecución inicial y ciclo automatizado cada 60 segundos
document.addEventListener('DOMContentLoaded', () => {
  autoUpdateUSGS();
  setInterval(autoUpdateUSGS, 60000);
});
