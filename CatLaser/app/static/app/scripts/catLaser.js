var tmp = playgrounds.replace(/&#39;/gm, '"').replace(/False/gm, 'false').replace(/True/gm, 'true');
playgrounds = JSON.parse(tmp);
var svg = document.getElementById("playground");
var svgContainer = document.getElementById("canvasContainer");
var pointsContainer = document.getElementById("pointsContainer");
var svgScale;
var id = 0;
for (i = 0; i < playgrounds.length; i++) {
    if (playgrounds[i].active === true) {
        id = i;
    }
}
var activePlayground = playgrounds[id];
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
    return [offsetX, offsetY, scaleX, scaleY];
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
        svg.innerHTML += getSvgCircle(run_point.x, run_point.y, "black", "red");
    }
    if (currentPos) {
        svg.innerHTML += getSvgCircle(currentPos.x, currentPos.y, "black", "black");
    }
    if (Targets) {
        for (i = 0; i < Targets.length; i++) {
            svg.innerHTML += getSvgCircle(Targets[i].x, Targets[i].y, "silver", "yellow");
        }
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

function getSvgCircle(x1, y1, stroke, fill) {
    color = getRandomColor();
    var Xoff = svgScale[0];
    var Yoff = svgScale[1];
    var Xscale = svgScale[2];
    var Yscale = svgScale[3];
    x1 = (x1 + Xoff) / Xscale;
    y1 = (y1 + Yoff) / Yscale;
    return '<circle cx=' + x1 + ' cy=' + y1 + ' r="10" stroke=' + stroke + ' stroke-width="3" fill=' + fill + ' />';
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
        if (playgrounds[i].name === name) {
            id = i;
            playgrounds[i]["active"] = false;
        }
    }
    activePlayground = playgrounds[id];
    redrawSVG(svg, activePlayground);
}

function setActive(element) {
    started = false;
    var name = element.getAttribute("data");
    for (i = 0; i < playgrounds.length; i++) {
        if (playgrounds[i].name === name) {
            id = i;
            playgrounds[i]["active"] = false;
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
var maxSpeed = 400;                         // mm per second
var started = false;
var updateRate = 20;                        // millis
var minMaxSpeed = [10000, 15000];              // mm per second
var featureID = 0;
var minMaxFeatureDuration = [3000, 6000];  // millis
var featureDuration = 0;                    // millis
var eventProbability = 20;                  // %
var eventID = null;
var minMaxEventDuration = [500, 5000];      // millis
var eventDuration = 0;                      // millis
var Targets = [];
var tmpTargets = [];
var currentSpeed = 10;                       // mm per second
var initPosition = { 'x': 20, 'y': 20, 'speed': currentSpeed };
var currentPos = initPosition;
var arrived = false;

function resetSimulation() {
    currentSpeed = 10;
    Targets = [];
    tmpTargets = [];
    currentPos = initPosition;
    arrived = false;

    if (activePlayground.maxX > activePlayground.maxY) {
        if (activePlayground.maxY > maxSpeed) {
            minMaxSpeed = [maxSpeed / 5, maxSpeed];
        }
        else {
            minMaxSpeed = [activePlayground.maxY / 10, activePlayground.maxY / 2];
        }
    }
    resetEventValues();
    resetFeatureValues();
    redrawSVG(svg, activePlayground);
}

window.setInterval(function () {
    if (started) {
        if (activePlayground["active"] !== true) {
            started = false;
            alert("current Playground not active!");
        }
        else {
            if (Targets.length <= 1) {
                var newPoint = calcNextPoint();
                if (Array.isArray(newPoint)) {
                    Targets.concat(newPoint);
                }
                else {
                    Targets.push(newPoint);
                }
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
        console.log("featureDuration: " + featureDuration);
    }
    if (eventDuration >= 0) {
        eventDuration = eventDuration - updateRate;
        console.log("eventDuration: " + eventDuration);
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
    var newPoint = { 'x': x, 'y': y, 'speed': currentSpeed };
    //console.log("currentPos: " + JSON.stringify(currentPos) + ", \ncurrentTarget: " + JSON.stringify(target) + ", \nDirX: " + DirX + ", \nDirY: " + DirY + ", \nnew x: " + x + ", \nnew y: " + y + ", \nnewPoint: " + JSON.stringify(newPoint));
    return newPoint;
}

function arrivedTarget() {
    var target = Targets[0];
    var tol = currentSpeed / 1000 * updateRate / 3; // adjust the 1 if it works overruns the Target
    var xmin = currentPos.x - tol;
    var xmax = currentPos.x + tol;
    var ymin = currentPos.y - tol;
    var ymax = currentPos.y + tol;
    if (xmin <= target.x && target.x <= xmax && ymin <= target.y && target.y <= ymax) {
        return true;
    }
    else {
        return false;
    }
}

function StartSimulation(boolstart) {
    if (activePlayground["active"] === true) {
        if (boolstart) {
            started = true;
        }
        else {
            started = false;
        }
    }
    else {
        started = false;
        alert("current Playground not active!");
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
        // TODO if run_points.length = 0 dann....
        // TODO mit 
        // TODO var run_points = activePlayground["run_points"];
        // TODO if (run_points.length === 0)
        // TODO - set FeatureID != 0 cause this happens only if no Run-Points are selected
        // TODO - send message so the user knows that this features and some other not working without run_points
        // TODO
        // TODO
        var newPoint;
        resetFeatureValues();
        featureID = getRndInteger(0, 1);
        currentSpeed = getRndInteger(minMaxSpeed[0], minMaxSpeed[1]);
        featureDuration = getRndInteger(minMaxFeatureDuration[0], minMaxFeatureDuration[1]);
        newPoint = calcNextFeaturePoint(featureID);
        // catch errors in new Point-Calculation
        if (newPoint.x > activePlayground.maxX || newPoint.y > activePlayground.maxY) {
            newPoint = initPosition;
            alert("feature: " + featureID + ", generated a not valid Target!");
        }
        

        // DONT DELETE!!!!!
        // DONT DELETE!!!!! - uncomment if all events and features work!!
        // DONT DELETE!!!!!
        // calculate new Event-Points
        //if (getRndInteger(0, 100) < eventProbability) {
        //    eventID = getRndInteger(0, 7);
        //    currentSpeed = getRndInteger(minMaxSpeed[0], minMaxSpeed[1]);
        //    eventDuration = getRndInteger(minMaxFeatureDuration[0], minMaxFeatureDuration[1]);
        //    newPoint = calcNextEventPoint(eventID);
        //}
        //else { // calculate new Feature-Point
        //    featureID = getRndInteger(0, 2);
        //    currentSpeed = getRndInteger(minMaxSpeed[0], minMaxSpeed[1]);
        //    featureDuration = getRndInteger(minMaxFeatureDuration[0], minMaxFeatureDuration[1]);
        //    newPoint = calcNextFeaturePoint(featureID);
        //}
        // DONT DELETE!!!!!
        // DONT DELETE!!!!!
        // DONT DELETE!!!!!
        return newPoint;
    }
}

///////////////////////////////  Features  ///////////////////////////////////

function calcNextFeaturePoint(_featureID) {
    switch (_featureID) {
        case 0: return FeatureABC();
        case 1: return FeatureZickZack();
        case 2: return FeatureEdgeRun();

        default: return FeatureABC();
    }
}

var ABCcounter = -1;
var ABCstep = 1;
function FeatureABC() {
    var run_points = activePlayground["run_points"];
    if (run_points.length === 0) {
        featureDuration = 0;
        alert("no Run-Points defined! Simulation stoped!");
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

var ZickZackcurrentDir = { 'x': 1, 'y': 1 };
function FeatureZickZack() {
    var edges = activePlayground['edges'];
    var M;
    if (Targets.length > 0) {
        M = Targets[Targets.length - 1];
    }
    else {
        M = currentPos;
    }
    var Dir = ZickZackcurrentDir;
    // calculate all hits of 2D Raycast with edges
    // AND calculate the distance to nearest edge (shortestDistance)
    var shortestDistance = 1000000;
    for (i = 0; i < edges.length; i++) {
        var _x = M.x + Dir.x * 1000000;
        var _y = M.y + Dir.y * 1000000;
        var pointer = { 'x': _x, 'y': _y };
        var P = get_line_intersection(M, pointer, edges[i].A, edges[i].B);

        if (P.x !== -6666 && P.y !== -6666) {
            var distance = Math.sqrt(Math.pow(M.x - P.x, 2) + Math.pow(M.y - P.y, 2));
            if (distance < shortestDistance) {
                shortestDistance = distance;
            }
        }
    }
    // catch error - if shortestDistance is still the init value, something went wrong!
    if (shortestDistance === 1000000) {
        alert("something went wrong in FeatureZickZack.");
        return currentPos;
        // if this happens, maybe the currentPos wasent in the Playground anymore!
    }
    // calculate new Position according to Dir and distance to next edge (shortestDistance)
    var offset = getRndInteger(shortestDistance / 20, shortestDistance);
    var DirAbs = Math.sqrt(Math.pow(Dir.x, 2) + Math.pow(Dir.y, 2));
    var factor = (shortestDistance - offset) / DirAbs;
    var newX = M.x + Dir.x * factor;
    var newY = M.y + Dir.y * factor;

    // rotate Dir Vector Randomly
    var randomX = getRndInteger(-100, 100) / 100;
    var randomY = getRndInteger(-100, 100) / 100;
    ZickZackcurrentDir = { 'x': randomX, 'y': randomY };

    return { 'x': newX, 'y': newY, 'speed': currentSpeed };
}

function FeatureEdgeRun() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentSpeed }
}

// will be executed after a new Playground is loaded
function resetFeatureValues() {
    ABCcounter = -1;
    ABCstep = 1;
}

////////////////////////////////  Events  ////////////////////////////////////

function calcNextEventPoint(_eventID) {
    switch (_eventID) {
        case 0: return EventCircle();
        case 1: return EventSinCos();
        case 2: return EventBlink();
        case 3: return EventStandStill();
        case 4: return EventWollkneul();
        case 5: return EventForwardBackward();
        default: // EventGoOn()
            eventDuration = 0;
            return currentPos;
    }
}


var CircleMaxRadius = 2000;
var CircleMaxSpeed = 1000;      // mm per second
function EventCircle() {
    var CircleResolution = 36;         // amount of steps per circle!
    var CircleTmpCurrentPos = currentPos;
    var speed = getRndInteger(minMaxSpeed[0], minMaxSpeed[1]);
    var CircleRadius = eventDuration * speed / (2 * Math.PI);
    var Circlesteps = 360 / CircleResolution;
    var newPoints = [];
    var newX, newY;
    for (i = 0; i < CircleResolution; i++) {
        newX = CircleRadius * Math.sin(toRadians(CircleCurrentAngle));
        newY = CircleRadius * Math.cos(toRadians(CircleCurrentAngle));
        CircleCurrentAngle = CircleCurrentAngle + Circlesteps;
        newPoints.append({ 'x': newX, 'y': newY, 'speed': currentSpeed });
    }
    newPoints.append(CircleTmpCurrentPos);
    return newPoints;
}

function EventSinCos() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentSpeed };
}

function EventBlink() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentSpeed };
}

function EventStandStill() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentSpeed };
}

function EventWollkneul() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentSpeed };
}

function EventForwardBackward() {
    return newPoint; // { 'x': x, 'y': y, 'speed': currentSpeed };
}

// will be executed after a new Playground is loaded
function resetEventValues() {

}

/////////////////////// Features-Events-Functions  ///////////////////////////

function get_line_intersection(A1, A2, B1, B2) {
    var a = A2.y - A1.y;
    var b = -B2.y + B1.y;
    var c = A2.x - A1.x;
    var d = -B2.x + B1.x;
    var C1 = B1.y - A1.y;
    var C2 = B1.x - A1.x;

    var tmp = a * d - b * c;
    if (tmp) {
        var invMa = d / tmp;
        var invMb = -b / tmp;
        var invMc = -c / tmp;
        var invMd = a / tmp;

        var m = invMa * C1 + invMb * C2;
        var n = invMc * C1 + invMd * C2;
        if (0 <= m && m <= 1 && 0 <= n && n <= 1) {
            var x = A1.x + m * (A2.x - A1.x);
            var y = A1.y + m * (A2.y - A1.y);
            return { 'x': x, 'y': y};
        }
        else {
            return { 'x': -6666, 'y': -6666};
        }
    }
    else {
        return { 'x': -6666, 'y': -6666};
    }
}

function toRadians(angle) {
    return angle * (Math.PI / 180);
}