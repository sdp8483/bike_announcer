/* === Bike Annoucer ===
    - provides audio warning based on user input about intended passing
   by: Sam Perry
   July 2017

   === HARWARE ===
    - Teensy 3.1
    - Audio adapter board for Teensy 3.0-3.6
    - PAM8302 2.5W Class D Mono Audio Amplifier
    - 8ohm Speaker
    - capacitive buttons
    - RGB led for user interface

   === SOFTWARE ===
    - initial code based on WaveFilePlayer Teensy example
    - Audio files from http://shtooka.net/index.php

*/

#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>
#include <EEPROM.h>

/* GPIO defines */
#define LEFT_BUTTON   0
#define RIGHT_BUTTON  1
#define TONE_BUTTON  17
#define VOL_BUTTON   16
#define AMP_ENABLE   21
#define RED_LED       3
#define GREEN_LED     4
#define BLUE_LED      5

/* Touch Settings */
// adjust THRESHOLD_TRIGGER for touch sensitivity, lower number = more sensitive
#define THRESHOLD_SAMPLES       1000  // number of samples to average for threshold calculation
#define THRESHOLD_TRIGGER        300  // amount touch read should exced threshold to trigger
int left_threshold;                   //stores the average untouched readings plus the threshold for the left button
int right_threshold;                  //stores the average untouched readings plus the threshold for the right button
int tone_threshold;                   //stores the average untouched readings plus the threshold for the tone button
int vol_threshold;                    //stores the average untouched readings plus the threshold for the volume button

/* Line Out Volume Settings */
// controls the RGB LED fade behavior
int line_out_volume;
#define LINE_OUT_VOL_ADDR 0
const int red_fade[19]   = {255, 229, 203, 177, 151, 125, 99, 73, 47, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
const int green_fade[19] = {0, 48, 74, 100, 126, 152, 178, 204, 230, 255, 230, 204, 178, 152, 126, 100, 74, 48, 0};
const int blue_fade[19]  = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 47, 73, 99, 125, 151, 176, 203, 229, 255};

AudioSynthWaveformSine   sine1;          //xy=159,143
AudioSynthWaveformSine   sine2;          //xy=159,218
AudioMixer4              mixer1;         //xy=365,183
AudioPlaySdWav           playWav1;
AudioOutputI2S           audioOutput;
AudioConnection          patchCord1(playWav1, 0, audioOutput, 0);
AudioConnection          patchCord2(sine1, 0, mixer1, 0);
AudioConnection          patchCord3(sine2, 0, mixer1, 1);
AudioConnection          patchCord4(mixer1, 0, audioOutput, 0);
AudioControlSGTL5000     sgtl5000_1;

// Use these with the Teensy Audio Shield
#define SDCARD_CS_PIN    10
#define SDCARD_MOSI_PIN   7
#define SDCARD_SCK_PIN   14

void setup() {
  AdjustThouchThreshold(); // get the untouched + threshold readings for all buttons
  pinMode(AMP_ENABLE, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(BLUE_LED, OUTPUT);

  digitalWrite(AMP_ENABLE, LOW); // make sure the audio amp is off

  // Audio connections require memory to work.  For more
  // detailed information, see the MemoryAndCpuUsage example
  AudioMemory(8);

  sgtl5000_1.enable();

  // set line out volume and display to user
  EEPROM.get(LINE_OUT_VOL_ADDR, line_out_volume);
  sgtl5000_1.lineOutLevel(line_out_volume);
  VolumeDisplay();

  SPI.setMOSI(SDCARD_MOSI_PIN);
  SPI.setSCK(SDCARD_SCK_PIN);
  if (!(SD.begin(SDCARD_CS_PIN))) {
    // stop here, flash RED led
    analogWrite(RED_LED, 0);
    analogWrite(GREEN_LED, 0);
    analogWrite(BLUE_LED, 0);
    
    while (1) {
      for (int i=0; i<256; i++){
        analogWrite(RED_LED, i);
        delay(1);
      }
      for (int i=256; i>0 ; i--){
        analogWrite(RED_LED, i);
        delay(1);
      }
      analogWrite(RED_LED, 0);
      delay(500);
    } // end while
  } // end if

  // setup simple alert tone
  sine1.frequency(440);
  sine2.frequency(430);
  sine1.amplitude(0);
  sine2.amplitude(0);
} // end setup

void loop() {
  if (touchRead(LEFT_BUTTON) > left_threshold) {
    playFile("ONLEFT.WAV");
  } // end if

  if (touchRead(RIGHT_BUTTON) > left_threshold) {
    playFile("ONRIGHT.WAV");
  } // end if

  if (touchRead(TONE_BUTTON) > tone_threshold) {
    PlaySimpleAlertTone();
  } // end if

  // adjust line out volume
  if (touchRead(VOL_BUTTON) > vol_threshold) {
    /*13: 3.16 Volts p-p, 14: 2.98 Volts p-p, 15: 2.83 Volts p-p, 16: 2.67 Volts p-p, 17: 2.53 Volts p-p, 18: 2.39 Volts p-p
      19: 2.26 Volts p-p, 20: 2.14 Volts p-p, 21: 2.02 Volts p-p, 22: 1.91 Volts p-p, 23: 1.80 Volts p-p, 24: 1.71 Volts p-p
      25: 1.62 Volts p-p, 26: 1.53 Volts p-p, 27: 1.44 Volts p-p, 28: 1.37 Volts p-p, 29: 1.29 Volts p-p, 30: 1.22 Volts p-p, 31: 1.16 Volts p-p*/
    line_out_volume--;

    if (line_out_volume < 13) {
      line_out_volume = 31;
    }
    
    sgtl5000_1.lineOutLevel(line_out_volume); // set line out volume
    EEPROM.put(LINE_OUT_VOL_ADDR, line_out_volume); // save to eeprom
    VolumeDisplay(); // display to user

    // wait for user to lift finger
    while (touchRead(VOL_BUTTON) > vol_threshold) {
      delay(250);
    } // end while
  } // end if
} // end loop

void playFile(const char *filename)
{
  //PlaySimpleAlertTone(); // dont play this, it is annoying

  // turn on the amplifier, previous function shuts it off
  digitalWrite(AMP_ENABLE, HIGH);

  // Start playing the file.  This sketch continues to
  // run while the file plays.
  playWav1.play(filename);

  // A brief delay for the library read WAV info
  delay(5);

  // Simply wait for the file to finish playing.
  while (playWav1.isPlaying()) {
    // Stop Playback if tone button is pressed
    if (touchRead(TONE_BUTTON) > tone_threshold) {
      playWav1.stop();
      while (touchRead(TONE_BUTTON) > tone_threshold) {
        // wait for user to remove finger, prevents tone from playing
        delay(10);
      }// end while
    } // end if
  } // end while

  digitalWrite(AMP_ENABLE, LOW); // turn off amp
} // end playFile

void AdjustThouchThreshold() {
  int left_sum  = 0;
  int right_sum = 0;
  int tone_sum  = 0;
  int vol_sum   = 0;

  for (int i = 0; i < THRESHOLD_SAMPLES; i++) {
    left_sum  += touchRead(LEFT_BUTTON);
    right_sum += touchRead(RIGHT_BUTTON);
    tone_sum  += touchRead(TONE_BUTTON);
    vol_sum   += touchRead(VOL_BUTTON);
  } // end for

  left_threshold  = int((float(left_sum ) / float(THRESHOLD_SAMPLES)) + 0.5) + THRESHOLD_TRIGGER;
  right_threshold = int((float(right_sum) / float(THRESHOLD_SAMPLES)) + 0.5) + THRESHOLD_TRIGGER;
  tone_threshold  = int((float(tone_sum ) / float(THRESHOLD_SAMPLES)) + 0.5) + THRESHOLD_TRIGGER;
  vol_threshold   = int((float(vol_sum  ) / float(THRESHOLD_SAMPLES)) + 0.5) + THRESHOLD_TRIGGER;
} // end AdjustTouchThreshold

void PlaySimpleAlertTone() {
  digitalWrite(AMP_ENABLE, HIGH);
  // play simple alert tone
  sine1.amplitude(0.3);
  sine2.amplitude(0.3);
  delay(250);
  sine1.amplitude(0);
  sine2.amplitude(0);
  delay(100);
  digitalWrite(AMP_ENABLE, LOW);
}

void VolumeDisplay(){
    analogWrite(RED_LED, red_fade[line_out_volume - 13]);
    analogWrite(GREEN_LED, green_fade[line_out_volume - 13]);
    analogWrite(BLUE_LED, blue_fade[line_out_volume - 13]);
}

