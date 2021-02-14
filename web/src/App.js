import './App.css';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON } from 'react-leaflet';
import districtMap from "./data/nyc-school-districts.json"


const x =[40.70594602843819, -73.97906084845815]

function App() {
  return (
    <div className="App">
    <MapContainer center={x} zoom={13} scrollWheelZoom={true}>
      <TileLayer
        attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <GeoJSON data={districtMap} />
    </MapContainer>
    </div>
  );
}

export default App;
