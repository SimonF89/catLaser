var tmp = playgrounds.replace(/&#39;/gm, '"').replace(/False/gm, 'false').replace(/True/gm, 'true');
playgrounds = JSON.parse(tmp);
var svg = document.getElementById("playground");
var svgContainer = document.getElementById("canvasContainer");
var pointsContainer = document.getElementById("pointsContainer");
var svgScale;
var id = 0;
for (i = 0; i < playgrounds.length; i++) {
    if (playgrounds[i].active == true) {
        id = i;
    }
}
var activePlayground = playgrounds[id]
svgScale = resizeSVG(svg, activePlayground["minX"], activePlayground["maxX"], activePlayground["minY"], activePlayground["maxY"]);
DrawPlayground(activePlayground);

window.onresize = function (event) {
    redrawSVG();
};

//////////////////////////////////////////////////////////////////////////////
/////////////////////////////  SVG-Drawing  //////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

function redrawSVG() {
    svgScale = resizeSVG(svg, activePlayground["minX"], activePlayground["maxX"], activePlayground["minY"], activePlayground["maxY"]);
    svg.innerHTML = "";
    DrawPlayground(activePlayground);
}

function resizeSVG(svg, minX, maxX, minY, maxY) {
    var x = svgContainer.offsetWidth - 30;
    var y = x * 0.7;
    svg.style.width = x;
    svg.style.height = y;
    pointsContainer.style.maxHeight = (y + 50) + "px";
    // calc scale and offset for SVG
    offsetX = -minX;
    offsetY = -minY;
    scaleX = (maxX - minX) / x;
    scaleY = (maxY - minY) / y;
    return [offsetX, offsetY, scaleX, scaleY]
}

function DrawPlayground(playground) {
    for (i = 0; i < playground['edges'].length; i++) {
        var edges = playground['edges'];
        var edge = edges[i];
        if (!edge.color) {
            edge.color = getRandomColor();
        }
        svg.innerHTML += getSvgLine(edge.A.x, edge.A.y, edge.B.x, edge.B.y, edge.color);
    }
    for (i = 0; i < playground['run_points'].length; i++) {
        var run_points = playground['run_points'];
        var run_point = run_points[i];
        svg.innerHTML += getSvgCircle(run_point.x, run_point.y);
    }
    if (currentPos) {
        svg.innerHTML += getSvgCircle(currentPos.x, currentPos.y);
    }
}

function getSvgLine(x1, y1, x2, y2, color) {
    var Xoff = svgScale[0];
    var Yoff = svgScale[1];
    var Xscale = svgScale[2];
    var Yscale = svgScale[3];
    x1 = (x1 + Xoff) / Xscale;
    x2 = (x2 + Xoff) / Xscale;
    y1 = (y1 + Yoff) / Yscale;
    y2 = (y2 + Yoff) / Yscale;
    return '<line x1=' + x1 + ' y1=' + y1 + ' x2=' + x2 + ' y2=' + y2 + ' style="stroke:' + color + ';stroke-width:2" />';
}

function getSvgCircle(x1, y1) {
    color = getRandomColor();
    var Xoff = svgScale[0];
    var Yoff = svgScale[1];
    var Xscale = svgScale[2];
    var Yscale = svgScale[3];
    x1 = (x1 + Xoff) / Xscale;
    y1 = (y1 + Yoff) / Yscale;
    return '<circle cx=' + x1 + ' cy=' + y1 + ' r="10" stroke="black" stroke-width="3" fill="red" />';
}

function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

//////////////////////////////////////////////////////////////////////////////
////////////////////////////  Update-Status  /////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

var data_url = document.getElementById("link_from_django_to_js").getAttribute("change_status_url");

function draw(element) {
    started = false;
    var name = element.getAttribute("data");
    for (i = 0; i < playgrounds.length; i++) {
        if (playgrounds[i].name == name) {
            id = i;
            playgrounds[i]["active"] = false
        }
    }
    activePlayground = playgrounds[id];
    redrawSVG(svg, activePlayground);
}

function setActive(element) {
    started = false;
    var name = element.getAttribute("data");
    for (i = 0; i < playgrounds.length; i++) {
        if (playgrounds[i].name == name) {
            id = i;
            playgrounds[i]["active"] = false
        }
    }
    ajaxPOST(playgrounds[id].name);
    activePlayground = playgrounds[id];
    activePlayground["active"] = true;
    resetSimulation();
}

function ajaxPOST(name) {
    $.ajax({
        type: 'POST',
        url: data_url,
        data: { 'playground_name':name },
        dataType: 'json',
        success: function (result) { return result; },
        error: function (result) {
            alert("error occurred on DAM4KMU-ajax-request, with following data: " + JSON.stringify({ 'playground_name': name }));
            return null;
        }
    });
}

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////  Simulation  //////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

// TODO calculate maxSpeed from activePlayground.Laser.z and max-Alpha of Servo
// TODO calculate maxSpeed from activePlayground.Laser.z and max-Alpha of Servo
// TODO calculate maxSpeed from activePlayground.Laser.z and max-Alpha of Servo
var maxSpeed = 400;                        // mm per second
var started = false;
var updateRate = 20;                        // millis
var minMaxSpeed = [200, 5000]               // mm per second
var featureID = 0;
var minMaxFeatureDuration = [5000, 20000];  // millis
var featureDuration = 0;                    // millis
var eventProbability = 20;                  // %
var eventID = null;
var minMaxEventDuration = [500, 5000];      // millis
var eventDuration = 0;                      // millis
var currentPos = { 'x': 0, 'y': 0, 'speed': 10 };
var Targets = [];
var tmpTargets = [];
var currentSpeed = 10;                       // mm per second
var arrived = false;

function resetSimulation() {
    currentPos = { 'x': 0, 'y': 0, 'speed': 10 }

    if (activePlayground.maxX > activePlayground.maxY) {
        if (activePlayground.maxY > maxSpeed) {
            minMaxSpeed = [maxSpeed / 5, maxSpeed]
        }
        else {
            minMaxSpeed = [activePlayground.maxY / 10, activePlayground.maxY / 2]
        }
    }
    resetEventValues();
    resetFeatureValues();
    redrawSVG(svg, activePlayground);
}

window.setInterval(function () {
    if (started) {
        if (activePlayground["active"] != true) {
            started = false;
            alert("current Playground not active!")
        }
        else {
            if (Targets.length <= 1) {
                Targets.push(calcNextPoint());
                arrived = false;
            }
            if (Targets.length > 1) {
                if (arrived) {
                    Targets.shift();
                    arrived = false;
                }
                currentPos = goTowardsNextTarget();
                redrawSVG();
                arrived = arrivedTarget();
            }
        }
    }
    if (featureDuration >= 0) {
        featureDuration = featureDuration - updateRate;
    }
    if (eventDuration >= 0) {
        eventDuration = eventDuration - updateRate;
    }
}, updateRate);

function goTowardsNextTarget() {
    var target = Targets[0];
    var DirX = target.x - currentPos.x;
    var DirY = target.y - currentPos.y;
    DirX = DirX / Math.sqrt(Math.pow(DirX, 2) + Math.pow(DirY, 2));
    DirY = DirY / Math.sqrt(Math.pow(DirX, 2) + Math.pow(DirY, 2));
    if (isNaN(DirX)) {
        DirX = 0;
    }
    if (isNaN(DirY)) {
        DirY = 0;
    }
    //svgScale = [offsetX, offsetY, scaleX, scaleY]
    var x = currentPos.x + DirX * currentSpeed / 1000 * updateRate / svgScale[2];
    var y = currentPos.y + DirY * currentSpeed / 1000 * updateRate / svgScale[3];
    var newPoint = { 'x': x, 'y': y, 'speed': currentPos.speed };
    console.log("currentPos: " + JSON.stringify(currentPos) + ", \ncurrentTarget: " + JSON.stringify(target) + ", \nDirX: " + DirX + ", \nDirY: " + DirY + ", \nnew x: " + x + ", \nnew y: " + y + ", \nnewPoint: " + JSON.stringify(newPoint));
    return newPoint;
}

function arrivedTarget() {
    var target = Targets[0];
    var tol = currentSpeed / 1000 * updateRate * 1; // adjust the 1 if it works overruns the Target
    var xmin = currentPos.x - tol;
    var xmax = currentPos.x + tol;
    var ymin = currentPos.y - tol;
    var ymax = currentPos.y + tol;
    if (xmin <= target.x && target.x <= xmax && ymin <= target.y && target.y <= ymax) {
        console.log("-lasnfölaflkasjfdlkajsfdölkajfdslkjafdslkajdsfölkajfdölkdsalfkjalkjfdaöljfölakjfdölakjfdlkafdskajölfdkjasjaölsjföalkdsjfölkajfds");
        return true;
    }
    else {
        return false;
    }
}

function StartSimulation(boolstart) {
    if (activePlayground["active"] == true) {
        if (boolstart) {
            started = true;
        }
        else {
            started = false;
        }
    }
    else {
        started = false;
        alert("current Playground not active!")
    }
}

function getRndInteger(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function calcNextPoint() {
    if (eventDuration > 0) {
        return calcNextEventPoint(eventID);
    }
    else if (featureDuration > 0) {
        return calcNextFeaturePoint(featureID);
    }
    else { // eventDuration <= 0 && featureDuration <= 0
        featureID = 0;//getRndInteger(0, 2);
        currentSpeed = getRndInteger(minMaxSpeed[0], minMaxSpeed[1]);
        featureDuration = getRndInteger(minMaxFeatureDuration[0], minMaxFeatureDuration[1]);
        return calcNextFeaturePoint(featureID);

        // DONT DELETE!!!!!
        // DONT DELETE!!!!! - uncomment if all events and features work!!
        // DONT DELETE!!!!!
        //if (getRndInteger(0, 100) < eventProbability) {
        //    eventID = getRndInteger(0, 7);
        //    currentSpeed = getRndInteger(minMaxSpeed[0], minMaxSpeed[1]);
        //    eventDuration = getRndInteger(minMaxFeatureDuration[0], minMaxFeatureDuration[1]);
        //    return calcNextEventPoint(eventID);
        //}
        //else {
        //    featureID = getRndInteger(0, 2);
        //    currentSpeed = getRndInteger(minMaxSpeed[0], minMaxSpeed[1]);
        //    featureDuration = getRndInteger(minMaxFeatureDuration[0], minMaxFeatureDuration[1]);
        //    return calcNextFeaturePoint(featureID);
        //}
        // DONT DELETE!!!!!
        // DONT DELETE!!!!!
        // DONT DELETE!!!!!
    }
}

///////////////////////////////  Features  ///////////////////////////////////

// will be executed after a new Playground is loaded
function resetFeatureValues() {

}

function calcNextFeaturePoint(_featureID) {
    switch (_featureID) {
        case 0:
            return FeatureABC();
            break;
        case 1:
            return FeatureZickZack();
            break;
        case 2:
            return FeatureEdgeRun();
            break;
        default:
            return FeatureABC();
    }
}

var ABCcounter = -1;
var ABCstep = 1;
function FeatureABC() {
    var run_points = activePlayground["run_points"];
    if (run_points.length == 0) {
        featureDuration = 0;
        alert("no Run-Points defined! Simulation stoped!")
        // TODO
        // TODO
        // TODO - set FeatureID != 0 cause this happens only if no Run-Points are selected
        // TODO - send message so the user knows that this features and some other not working without run_points
        // TODO
        // TODO
        started = false;
        return currentPos;
    }
    else {
        ABCcounter = ABCcounter + ABCstep;
        if (ABCcounter >= run_points.length) {
            ABCstep = -ABCstep;
            ABCcounter = ABCcounter + ABCstep;
        }
        else if (ABCcounter < 0) {
            ABCstep = -ABCstep;
            ABCcounter = ABCcounter + ABCstep;
        }
        return { 'x': run_points[ABCcounter].x, 'y': run_points[ABCcounter].y, 'speed': currentSpeed };
    }
}

function FeatureZickZack() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentPos.speed }
}

function FeatureEdgeRun() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentPos.speed }
}

////////////////////////////////  Events  ////////////////////////////////////

// will be executed after a new Playground is loaded
function resetEventValues() {

}

function calcNextEventPoint(_eventID) {
    switch (_eventID) {
        case 0:
            return EventCircle()
            break;
        case 1:
            return EventSinCos()
            break;
        case 2:
            return EventBlink()
            break;
        case 3:
            return EventStandStill()
            break;
        case 4:
            return EventWollkneul()
            break;
        case 5:
            return EventForwardBackward()
            break;
        default: // EventGoOn()
            eventDuration = 0;
            return currentPos;
    }
}

function EventCircle() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentPos.speed }
}

function EventSinCos() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentPos.speed }
}

function EventBlink() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentPos.speed }
}

function EventStandStill() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentPos.speed }
}

function EventWollkneul() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentPos.speed }
}

function EventForwardBackward() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentPos.speed }
}