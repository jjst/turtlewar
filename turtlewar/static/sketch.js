var colors = [
    [0, 0, 0],
    [255, 255, 255],
    [255, 0, 0],
    [0, 255, 0],
    [0, 0, 255],
    [0, 255, 255],
    [255, 0, 255],
    [255, 255, 0]
];

var penDown = false;
var currentColor = colors[0];
var transforms = [];

function setup() {
    createCanvas(
        windowWidth,
        windowHeight
    );
    var initialPosition = {
        x: windowWidth / 2,
        y: windowHeight / 2
    };
    transforms.push(["translate", initialPosition.x, initialPosition.y]);
    background(0, 0, 0);
    angleMode(DEGREES);
}

var lineLength = 0;
var drawn = 0;
var drawingSpeed = 8;

function draw() {
    if(drawn < lineLength) {
        drawn = Math.min(lineLength, drawn + drawingSpeed);
        drawLine(drawn);
    } else {
        popInstruction();
    }
}

function drawLine(length) {
    // Apply every transform except the last one
    // (which we're currently drawing)
    applyTransforms(transforms.slice(0, -1));
    stroke(currentColor);
    line(0, 0, length, 0);
}

function popInstruction() {
    if(instructions.length == 0) {
        return;
    }
    var [command, value] = instructions.shift();
    switch(command) {
        case "color":
            currentColor = colors[value];
            break;
        case "down":
            penDown = true;
            break;
        case "up":
            penDown = false;
            break;
        case "rotate":
            transforms.push(["rotate", value]);
            break;
        case "forward":
            transforms.push(["translate", value + 1, 0]);
            if(penDown) {
                lineLength = value;
                drawn = 0;
            }
            break;
    }
}

function applyTransforms(transforms) {
    transforms.forEach(function(transform) {
        var transform = transform.slice();
        transformType = transform.shift();
        switch(transformType) {
            case "rotate":
                var [angle] = transform;
                rotate(angle);
                break;
            case "translate":
                var [x, y] = transform;
                translate(x, y);
                break;
        }
    });
}
