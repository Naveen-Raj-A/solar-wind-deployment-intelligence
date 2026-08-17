import React, { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMap,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

const MapUpdater = ({
  latitude,
  longitude,
}) => {
  const map = useMap();

  useEffect(() => {
    if (
      Number.isFinite(latitude) &&
      Number.isFinite(longitude)
    ) {
      map.setView(
        [latitude, longitude],
        11,
        {
          animate: false,
        }
      );

      setTimeout(() => {
        map.invalidateSize();
      }, 150);
    }
  }, [
    latitude,
    longitude,
    map,
  ]);

  return null;
};

const MapView = ({
  latitude,
  longitude,
  locationName,
}) => {
  const lat = Number(latitude);
  const lng = Number(longitude);

  const validCoordinates =
    Number.isFinite(lat) &&
    Number.isFinite(lng) &&
    lat >= -90 &&
    lat <= 90 &&
    lng >= -180 &&
    lng <= 180;

  if (!validCoordinates) {
    return (
      <div className="map-error">

        <strong>
          Map unavailable
        </strong>

        <span>
          Valid latitude and
          longitude are required
          to display the site
          location.
        </span>

      </div>
    );
  }

  return (
    <div className="site-map-wrapper">

      <MapContainer
        center={[lat, lng]}
        zoom={11}
        scrollWheelZoom={true}
        className="site-map"
      >

        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapUpdater
          latitude={lat}
          longitude={lng}
        />

        <CircleMarker
          center={[lat, lng]}
          radius={10}
          pathOptions={{
            color: "#0b2237",
            fillColor: "#1769aa",
            fillOpacity: 0.95,
            weight: 3,
          }}
        >

          <Popup>

            <div className="map-popup">

              <strong>
                {locationName ||
                  "Analysed Site"}
              </strong>

              <span>
                Latitude: {lat}
              </span>

              <span>
                Longitude: {lng}
              </span>

            </div>

          </Popup>

        </CircleMarker>

      </MapContainer>

      <div className="map-overlay">

        <span>
          ANALYSED SITE
        </span>

        <strong>
          {locationName ||
            "Selected Location"}
        </strong>

      </div>

    </div>
  );
};

export default MapView;