// Pin definitions for stepper motor
const int stepPin = 3;
const int dirPin = 4;
const int enPin = 9;

// Stepper control variables
int stepDelay = 1000;
bool isRunning = false;

void setup() {
    Serial.begin(9600);
    pinMode(stepPin, OUTPUT);
    pinMode(dirPin, OUTPUT);
    pinMode(enPin, OUTPUT);
    digitalWrite(enPin, LOW);
    digitalWrite(dirPin, LOW); // Fixed forward direction
    Serial.println("Stepper Motor Control Ready");
    Serial.println("Starting loop");
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        handleCommand(command);
    }
    if (isRunning) {
        runStepperMotor();
        Serial.println("RUNNING:1");  // Feedback to GUI
    } else {
        Serial.println("RUNNING:0");
    }
    delay(10);  // Reduce feedback rate
}

void handleCommand(String command) {
    if (command == "start") {
        isRunning = true;
        Serial.println("Motor started");
    } else if (command == "stop") {
        isRunning = false;
        Serial.println("Motor stopped");
    } else if (command.startsWith("speed ")) {
        int newSpeed = command.substring(6).toInt();
        if (newSpeed >= 500 && newSpeed <= 5000) {
            stepDelay = newSpeed;
            Serial.println("Step delay set to: " + String(stepDelay) + " us");
        } else {
            Serial.println("Invalid speed. Use 500-5000 us.");
        }
    }
}

void runStepperMotor() {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(stepDelay);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(stepDelay);
}