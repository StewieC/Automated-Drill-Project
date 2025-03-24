// Pin definitions (unchanged)
const int limitSwitchPin = 2;
const int stepPin = 3;
const int dirPin = 4;
const int enPin = 9;
const int enA = 7;
const int in1 = 6;
const int in2 = 5;

// Motor control variables (unchanged)
int speed = 0;
bool motorEnabled = false;
bool checkstop = false;
int stepperDirection = 1;
unsigned long previousMillis = 0;
const long interval = 50;
int timebt = 0;

// Define states (unchanged)
enum State { IDLE, RUN_DC_MOTOR, RUN_STEPPER_MOTOR };
State currentState = IDLE;
unsigned long previousMillisDCMotor = 0;
unsigned long previousMillisStepperMotor = 0;

// Stepper motor feed rates (unchanged)
const int stepperDelayHigh = 1000;
const int stepperDelayLow = 5000;
int currentStepperDelay = stepperDelayLow;
int currentPosition = 0;

// DC motor speed levels (new)
const int dcSpeedHigh = 200;  // High feed rate speed
const int dcSpeedLow = 50;    // Low feed rate speed

void setup() { /* Unchanged */ }

void loop() { /* Unchanged */ }

void checkSerialForEmergencyStop() { /* Unchanged */ }

void handleCommand(String command) {
  if (command == "stopmachine") {
    emergencyStop();
    Serial.println("STOPPED");
  } else if (command.startsWith("setSpeed")) {
    int newSpeed = command.substring(8).toInt();
    if (newSpeed >= 0 && newSpeed <= 255) {
      speed = newSpeed;
      motorEnabled = true;
      timebt = 10;
      Serial.println("SPEED SET TO: " + String(speed));
    } else {
      Serial.println("Invalid speed. Please enter a value between 0 and 255.");
    }
  } else if (command == "slowdrill") {
    speed = 100;
    motorEnabled = true;
    timebt = 10;
    runDCMotor(speed);
    Serial.println("Slow drill mode activated");
  } else if (command == "fastdrill") {
    speed = 255;
    motorEnabled = true;
    timebt = 10;
    runDCMotor(speed);
    Serial.println("Fast drill mode activated");
  } else if (command == "highFeedRate") {
    currentStepperDelay = stepperDelayHigh; // Fast stepper
    speed = dcSpeedHigh;                    // High DC speed
    motorEnabled = true;
    runDCMotor(speed);
    Serial.println("High Feed Rate selected: Stepper Fast, DC Speed " + String(speed));
  } else if (command == "slowFeedRate") {
    currentStepperDelay = stepperDelayLow;  // Slow stepper
    speed = dcSpeedLow;                     // Low DC speed
    motorEnabled = true;
    runDCMotor(speed);
    Serial.println("Slow Feed Rate selected: Stepper Slow, DC Speed " + String(speed));
  }
}

void emergencyStop() { /* Unchanged */ }
void runDCMotor(int speed) { /* Unchanged */ }
void runStepperMotor(int steps) { /* Unchanged */ }
void handleLimitSwitch() { /* Unchanged */ }