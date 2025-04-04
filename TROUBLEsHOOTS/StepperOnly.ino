// Pin definitions for stepper motor
const int stepPin = 3;  // Step signal
const int dirPin = 4;   // Direction signal
const int enPin = 9;    // Enable pin (LOW to enable)

// Stepper control variables
int stepsPerCommand = 200;  // Default steps per command
int stepDelay = 1000;       // Delay in microseconds between steps (speed control)

void setup() {
    Serial.begin(9600);
    pinMode(stepPin, OUTPUT);
    pinMode(dirPin, OUTPUT);
    pinMode(enPin, OUTPUT);
    digitalWrite(enPin, LOW);  // Enable stepper driver
    digitalWrite(dirPin, LOW); // Default direction (e.g., forward)
    Serial.println("Stepper Motor Control Ready");
    Serial.println("Commands: 'forward', 'reverse', 'stop', 'speed X' (X = 500-5000 us), 'steps X' (X = number of steps)");
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        handleCommand(command);
    }
}

void handleCommand(String command) {
    Serial.println("Received: " + command);
    if (command == "forward") {
        runStepperMotor(stepsPerCommand, LOW);  // LOW = forward
        Serial.println("Running forward " + String(stepsPerCommand) + " steps");
    } else if (command == "reverse") {
        runStepperMotor(stepsPerCommand, HIGH); // HIGH = reverse
        Serial.println("Running reverse " + String(stepsPerCommand) + " steps");
    } else if (command == "stop") {
        Serial.println("Stepper stopped (no action, just idle)");
    } else if (command.startsWith("speed ")) {
        int newSpeed = command.substring(6).toInt();
        if (newSpeed >= 500 && newSpeed <= 5000) {
            stepDelay = newSpeed;
            Serial.println("Step delay set to: " + String(stepDelay) + " us");
        } else {
            Serial.println("Invalid speed. Use 500-5000 us.");
        }
    } else if (command.startsWith("steps ")) {
        int newSteps = command.substring(6).toInt();
        if (newSteps > 0) {
            stepsPerCommand = newSteps;
            Serial.println("Steps per command set to: " + String(stepsPerCommand));
        } else {
            Serial.println("Invalid steps. Use a positive number.");
        }
    } else {
        Serial.println("Unknown command. Use 'forward', 'reverse', 'stop', 'speed X', 'steps X'");
    }
}

void runStepperMotor(int steps, int direction) {
    digitalWrite(dirPin, direction);  // Set direction
    for (int i = 0; i < steps; i++) {
        digitalWrite(stepPin, HIGH);
        delayMicroseconds(stepDelay);
        digitalWrite(stepPin, LOW);
        delayMicroseconds(stepDelay);
    }
}