"use strict";
const lanIP = `${window.location.hostname}:5000`;
const socketio = io(lanIP);

let userOnline = false;

// leaflet map
const provider = "https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png";
const copyright =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles style by <a href="https://www.hotosm.org/" target="_blank">Humanitarian OpenStreetMap Team</a> hosted by <a href="https://openstreetmap.fr/" target="_blank">OpenStreetMap France</a>';
let map, layerGroup;

let html_ridepage,
  html_homepage,
  html_ridespage,
  html_dashpage,
  html_statuspage,
  html_ride_button,
  html_totaldistance,
  html_ledradios,
  html_alarmradios,
  html_dashboard_curtime,
  html_dashboard_pasttime,
  html_dashboard_degrees,
  html_dashboard_speed,
  html_dashboard_gforce,
  html_dashboard_tempeng,
  html_dashboard_tempamb,
  html_rides_container,
  html_bike_img_container,
  html_digits,
  html_slidercontainer,
  html_ride_container;

let ride_tracking = false;

const listenToDashUI = function () {
  html_ride_button.addEventListener("click", function () {
    if (ride_tracking == true) {
      socketio.emit("ride", 0);
    }
    if (ride_tracking == false) {
      socketio.emit("ride", 1);
    }
  });
};

const listenToStatusUI = function () {
  html_ledradios.forEach(function (radioButton) {
    radioButton.addEventListener("change", function () {
      // console.log(Number(this.value))
      socketio.emit("led", { led: Number(this.value) });
    });
  });

  html_alarmradios.forEach(function (radioButton) {
    radioButton.addEventListener("change", function () {
      // console.log(Number(this.value))
      socketio.emit("alarm", { alarm: Number(this.value) });
    });
    // console.log(html_slidercontainer.querySelector('input[type="range"]').value);
    html_slidercontainer
      .querySelector('input[type="range"]')
      .addEventListener("change", function () {
        // console.log(Number(this.value))
        socketio.emit("sensitivity", { sensitivity: Number(this.value) });
      });
  });
};

const listenToSocket = function () {
  socketio.on("connect", function () {
    console.log("verbonden met socket webserver");
  });

  socketio.on("GPS", function (data) {
    // console.log(userOnline);
    const lat = data["long"];
    const long = data["lat"];
    const zoom = 12;

    console.log(lat, long);

    if (lat != 0 && long != 0) {
      map = L.map("mapid").setView([lat, long], zoom);

      if (userOnline == true) {
        L.tileLayer(provider).addTo(map);
        layerGroup = L.layerGroup().addTo(map);
        getWeather(lat, long);
        layerGroup.clearLayers();
        const marker = L.marker([lat, long]);
        marker.addTo(layerGroup);
      } else {
        layerGroup = L.tileLayer("maps/{z}/{x}/{y}.png", {
          maxZoom: 13,
          minZoom: 3,
          tileSize: 512,
          zoomOffset: -1,
        }).addTo(map);
        const marker = new L.Marker([lat, long]);
        marker.addTo(map);
      }
    } else {
      // socketio.emit("GPS");
      setTimeout(() => {
        socketio.emit("GPS");
      }, 1000);
    }
  });

  socketio.on("dash", function (data) {
    if (html_dashpage) {
      console.log(data);
      html_dashboard_curtime.innerHTML = data["time"];
      html_dashboard_pasttime.innerHTML = data["time_ride"];
      html_dashboard_degrees.innerHTML = Math.round(data["tilt"]);
      html_dashboard_gforce.innerHTML = data["accel"].toFixed(1);
      html_dashboard_tempeng.innerHTML = Math.round(data["engine_temp"]);
      html_dashboard_tempamb.innerHTML = Math.round(data["ambient_temp"]);
    }
  });

  socketio.on("status", function (data) {
    if (html_statuspage) {
      let html_ledradio;
      for (var i = 0; i < html_ledradios.length; i++) {
        html_ledradio = html_ledradios[i];

        if (Number(html_ledradio.value) === data["led"]) {
          html_ledradio.checked = true;
        }
      }
      let html_alarmradio;
      for (var i = 0; i < html_alarmradios.length; i++) {
        html_alarmradio = html_alarmradios[i];

        if (Number(html_alarmradio.value) === data["alarm"]) {
          html_alarmradio.checked = true;
        }
      }

      // add or remove images according to status
      if (data["led"] == 1 || data["auto-on/off"] == 1) {
        html_bike_img_container
          .querySelector("img[src='./style/images/light.png']")
          .classList.add("show");
      } else {
        html_bike_img_container
          .querySelector("img[src='./style/images/light.png']")
          .classList.remove("show");
      }

      if (data["alarm"] == 1) {
        html_bike_img_container
          .querySelector("img[src='./style/images/alarm.png']")
          .classList.add("show");
      } else {
        html_bike_img_container
          .querySelector("img[src='./style/images/alarm.png']")
          .classList.remove("show");
      }

      // show sensitivity slider when auto is checked
      if (html_ledradios[1].checked == true) {
        html_slidercontainer.classList.add("show");
      } else {
        html_slidercontainer.classList.remove("show");
      }
      // set value of sensitivity
      html_slidercontainer.querySelector('input[type="range"]').value =
        data["sensitivity"];

      // add or remove images tried to create the element inside js but unnecessarily complex
      //   if(data['led'] == 1){
      //     let ledImage = html_bike_img_container.querySelector("img[src='./style/images/light.png']")
      //     if(ledImage){
      //       html_bike_img_container.removeChild(ledImage)
      //     }
      //     ledImage = document.createElement('img')
      //     ledImage.setAttribute('src', './style/images/light.png');
      //     html_bike_img_container.appendChild(ledImage);
      //     // delay adding of clas for transition
      //     setTimeout(() => {
      //       ledImage.classList.add('show');
      //     }, 100);
      //   }
      //   else{
      //     const ledImage = html_bike_img_container.querySelector("img[src='./style/images/light.png']");
      //     if(ledImage){
      //       html_bike_img_container.removeChild(ledImage)
      //     }
      //   }

      //   if(data['alarm'] == 1){
      //     let alarmImage = html_bike_img_container.querySelector("img[src='./style/images/alarm.png']")
      //     if(alarmImage){
      //       html_bike_img_container.removeChild(alarmImage)
      //     }
      //     alarmImage = document.createElement('img')
      //     alarmImage.setAttribute('src', './style/images/alarm.png');
      //     html_bike_img_container.appendChild(alarmImage);
      //     setTimeout(() => {
      //       alarmImage.classList.add('show');
      //     }, 100);
      //   }
      //   else{
      //     const alarmImage = html_bike_img_container.querySelector("img[src='./style/images/alarm.png']");
      //     if(alarmImage){
      //       html_bike_img_container.removeChild(alarmImage)
      //     }
      //   }
    }
  });

  socketio.on("ride", function (data) {
    // console.log('temp')
    if (data == 1) {
      html_ride_button.innerHTML = "Stop ride";
      ride_tracking = true;
    }
    if (data == 0) {
      ride_tracking = false;
      setTimeout(() => {
        html_ride_button.innerHTML = "Start ride";
        html_dashboard_curtime.innerHTML = "--:--";
        html_dashboard_pasttime.innerHTML = "--:--:--";
        html_dashboard_degrees.innerHTML = "-";
        html_dashboard_gforce.innerHTML = "-";
        html_dashboard_tempeng.innerHTML = "--";
        html_dashboard_tempamb.innerHTML = "--";
      }, 1000);
    }
  });
};

const getRides = function () {
  handleData(`http://${lanIP}/api/v1/rides`, showRides);
};

const getRide = function (id) {
  handleData(`http://${lanIP}/api/v1/rides/${id}`, showRide);
};

const getRideLocations = function (id) {
  handleData(`http://${lanIP}/api/v1/rides/locations/${id}`, showRideLocations);
};

const getTotalDistance = function () {
  handleData(`http://${lanIP}/api/v1/rides/totaldistance`, showTotalDistance);
};

const getWeather = async (lat, long) => {
  const html_location = document.querySelector(".c-weather--location");
  const html_icon = document.querySelector(".c-weather--icon");
  const html_temp = document.querySelector(".c-weather--temp");
  const html_description = document.querySelector(".c-weather--description");
  const API_KEY = "6526c59b52b72536ed1d2d8d0f24e193";
  const weatherLink = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${long}&appid=${API_KEY}&units=metric&lang=eng`;
  const response = await fetch(weatherLink);
  const data = await response.json();

  console.log(data);
  html_location.innerHTML = `${data.name}, ${data.sys.country}`;

  const weatherIcon =
    "http://openweathermap.org/img/w/" + data.weather[0].icon + ".png";
  html_icon.setAttribute("src", weatherIcon);

  html_temp.innerHTML = `${Math.round(data.main.temp)}°C`;

  html_description.innerHTML = data.weather[0].description;
};

const showRide = function (json) {
  console.log(json.ride);
  html_ride_container.querySelector(".js-name").innerHTML = json.ride.name;
  html_ride_container.querySelector(".js-formatted_start_time").innerHTML =
    json.ride.formatted_start_time;
  html_ride_container.querySelector(".js-distance").innerHTML = (
    json.ride.distance / 1000
  ).toFixed(1);
  html_ride_container.querySelector(".js-avg_speed").innerHTML = Math.round(
    json.ride.avg_speed
  );
  html_ride_container.querySelector(".js-max_speed").innerHTML = Math.round(
    json.ride.max_speed
  );

  html_ride_container.querySelector(".js-max_accel").innerHTML =
    json.ride.max_accel.toFixed(1);
  html_ride_container.querySelector(".js-min_accel").innerHTML =
    json.ride.min_accel.toFixed(1);

  html_ride_container.querySelector(".js-max_left_tilt").innerHTML = Math.round(
    json.ride.max_left_tilt
  );
  html_ride_container.querySelector(".js-max_right_tilt").innerHTML =
    Math.round(json.ride.max_right_tilt);
  html_ride_container.querySelector(".js-avg_eng_temp").innerHTML = Math.round(
    json.ride.avg_eng_temp
  );
  html_ride_container.querySelector(".js-max_eng_temp").innerHTML = Math.round(
    json.ride.max_eng_temp
  );
  html_ride_container.querySelector(".js-avg_amb_temp").innerHTML = Math.round(
    json.ride.avg_amb_temp
  );
  html_ride_container.querySelector(".js-max_amb_temp").innerHTML = Math.round(
    json.ride.max_amb_temp
  );
};

const showTotalDistance = function (json) {
  // console.log(json.totaldistance.distance);

  const totalDistance = json.totaldistance.distance / 1000;
  const intValue = Math.round(totalDistance);
  const formattedValue = String(intValue).padStart(6, "0");
  const digits = formattedValue.split("");

  for (let i in digits) {
    html_digits[i].innerHTML = digits[i];
  }
};

const showRideLocations = function (json) {
  console.log(json);
  const lat = 50.908417;
  const long = 3.374111;
  const zoom = 10;
  map = L.map("mapid").setView([lat, long], zoom);

  if (userOnline == true) {
    L.tileLayer(provider).addTo(map);
    layerGroup = L.layerGroup().addTo(map);
  } else {
    layerGroup = L.tileLayer("maps/{z}/{x}/{y}.png", {
      maxZoom: 13,
      minZoom: 3,
      tileSize: 512,
      zoomOffset: -1,
    }).addTo(map);
  }

  // let latlngs = [
  //   [45.51, -122.68],
  //   [37.77, -122.43],
  //   [34.04, -118.2],
  // ];
  // console.log(latlngs)
  // draw polyline on map
  var polyline = L.polyline(json, { color: "red" }).addTo(map);
  // zoom the map to the polyline
  map.fitBounds(polyline.getBounds());
};

const showRides = function (json) {
  let htmlString = "";
  console.log(json.rides);
  for (let ride of json.rides) {
    const ridename = ride.name;
    const rideid = ride.id;
    const datetime = ride.formatted_start_time;
    const max_tilt_left = ride.max_left_tilt;
    const max_tilt_right = ride.max_right_tilt;
    let max_tilt = 0;
    const avg_speed = ride.avg_speed;
    const max_speed = ride.max_speed;
    if (Math.abs(max_tilt_right) > Math.abs(max_tilt_left)) {
      max_tilt = max_tilt_right;
    } else {
      max_tilt = max_tilt_left;
    }
    htmlString += `<a class="c-card c-card--rides"  href="ride.html?id=${rideid}">
    <div class="c-card__content ">
        <p class="c-card__title">${ridename}</p>
        <p class="c-card__datetime">${datetime}</p>
    </div>
    <div class="c-card__content">
        <div class="c-card__preview">
        <img src="./style/images/tilt.svg" alt="Angle icon">
            <p>${max_tilt}</p>
        </div>
        <div class="c-card__preview">
        <img src="./style/images/odometer.svg" alt="Odometer speed icon">
            <p>${avg_speed}</p>
        </div>
        <div class="c-card__preview">
        <img src="./style/images/odometer.svg" alt="Odometer speed icon">
            <p>${max_speed}</p>
        </div>
    </div>
</a>`;
  }
  html_rides_container.innerHTML = htmlString;
};

// async function IsUserOnline() {
//   try {
//     const response = await fetch("https://api.github.com/users/xiaotian/repos");
//     if (response.ok) {
//       // User has an active internet connection
//       console.log("User is connected to the internet");
//       userOnline = true;
//     } else {
//       // User does not have an active internet connection
//       // console.log("User is not connected to the internet");
//       userOnline = false;
//     }
//   } catch (error) {
//     // An error occurred, indicating the user is not connected to the internet
//     // console.log("User is not connected to the internet");
//     userOnline = false;
//   }
// }

const init = function () {
  // homepage | index.html
  html_homepage = document.querySelector(".js-homepage");

  // dashpage | dashboard.html
  html_dashpage = document.querySelector(".js-dashpage");
  html_dashboard_curtime = document.querySelector(".js-dashboard--cur-time");
  html_dashboard_pasttime = document.querySelector(".js-dashboard--past-time");
  html_dashboard_degrees = document.querySelector(".js-dashboard--degrees");
  html_dashboard_speed = document.querySelector(".js-dashboard--speed");
  html_dashboard_gforce = document.querySelector(".js-dashboard--g-force");
  html_dashboard_tempeng = document.querySelector(".js-dashboard--temp-eng");
  html_dashboard_tempamb = document.querySelector(".js-dashboard--temp-amb");
  html_ride_button = document.querySelector(".js-ride_button");

  // ridespage | rides.html
  html_ridespage = document.querySelector(".js-ridespage");
  html_rides_container = document.querySelector(".js-rides-container");

  // ridepage | ride.html
  html_ridepage = document.querySelector(".js-ridepage");
  html_ride_container = document.querySelector(".js-ride-container");

  // statuspage |status.html
  html_statuspage = document.querySelector(".js-statuspage");
  html_totaldistance = document.querySelector(".js-totaldistance");
  html_ledradios = document.querySelectorAll(".js-ledradio");
  html_alarmradios = document.querySelectorAll(".js-alarmradio");
  html_bike_img_container = document.querySelector(".js-bike-img-container");
  html_slidercontainer = document.querySelector(".js-slidercontainer");
  html_digits = document.querySelectorAll(".js-digit");

  console.info("DOM geladen");
  // IsUserOnline()
  listenToSocket();

  if (html_homepage) {
    socketio.emit("GPS");
  }

  if (html_dashpage) {
    listenToDashUI();
    socketio.emit("ridestatus");
  }

  if (html_ridepage) {
    let urlParams = new URLSearchParams(window.location.search);
    let rideid = urlParams.get("id");
    getRide(rideid);
    getRideLocations(rideid);
  }

  if (html_ridespage) {
    getRides();
  }

  if (html_statuspage) {
    socketio.emit("status");
    getTotalDistance();
    listenToStatusUI();
  }
};
document.addEventListener("DOMContentLoaded", init);
