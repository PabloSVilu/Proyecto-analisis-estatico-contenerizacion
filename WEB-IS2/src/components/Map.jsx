import React from 'react';
import { MapContainer, TileLayer, useMap, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import styles from './Map.module.css'; // 1. Importa tu archivo CSS module

// Arreglo de Iconos de Marcador
import L from 'leaflet';
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});


function RecenterMap({ coords }) {
  const map = useMap();
   if (coords && coords.length === 2 && !isNaN(coords[0]) && !isNaN(coords[1])) {
    map.setView(coords, map.getZoom());
  }
  return null;
}

function Map({ coords }) {
  const validCoords = (coords && coords.length === 2 && !isNaN(coords[0]) && !isNaN(coords[1]))
    ? coords
    : [-33.45694, -70.64827];

  return (
    // 2. Aplica la clase al MapContainer
    <MapContainer 
      center={validCoords} 
      zoom={13} 
      className={styles.mapContainerRounded} // Aplicar la clase CSS
    >
      <TileLayer
        attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {coords && coords.length === 2 && !isNaN(coords[0]) && !isNaN(coords[1]) && (
        <>
          <Marker position={coords}>
            <Popup>Aquí está tu ciudad.</Popup>
          </Marker>
          <RecenterMap coords={coords} />
        </>
      )}
    </MapContainer>
  );
}

export default Map;