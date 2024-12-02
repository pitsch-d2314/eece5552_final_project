
// use TimerOne library in order to ensure a precise sampling frequency 
#include <TimerOne.h>

// Declare global variables
unsigned int clk=0; //initialize clock
unsigned int k=0; // initialize counter
int sample=0; //initialize acquired sample
int last_sample=512; // set last sample
int ds=0; //inizialize the difference between two successive samples
long int S=0; // initialize the sum of the Moving Average
unsigned int win_len=128; // window length for computing EMG -LE (power of 2) 
unsigned int EMG_level=0; // initialize EMG activity level
long ACC=0L; //initialize accumulator


// array of 20 elements to implement a Moving Average filter of 20 coefficients 
int MAv[20]={0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

/**************************************************************************************** 
 * Function "EMG_LE" for:
1) sampling the raw EMG signal provided by the EMG sensor (e.g., MyoWare Muscle Sensor);
2) applying the feed-forward comb (FFC) filter (for removing powerline interference and motion artifacts) 
3) computing the EMG-LE
The function is triggered by the timer interrupt. 
*****************************************************************************************/

void EMG_LE(){

  // read current EMG raw signal 
  sample=analogRead(A1);

  // compute the difference between two successive samples 
  ds=sample-last_sample;

  // update Moving Average summation 
  S=S-MAv[k];
  MAv[k]=ds;
  S=S+MAv[k];

  // update Moving Average counter 
  if (k<19)
  { 
    k=k+1; 
  }

  else 
  { 
    k=0; 
  }
  
  // update accumulator 
  ACC=ACC+abs(S); 

  // update last_sample 
  last_sample=sample; 

  // update clock
  clk=clk+1;
  /***************************************************************************************** 
   * EMG-LE is computed by applying a moving average with a window of 128 samples 
   * on the absolute value of the EMG filtered by the FFC filter.
  Division by 128 (2^7) is performed by shifting the bit string (representing the EMG_level variable) 
  7 positions to the right. 
  *****************************************************************************************/ 

  if (clk>=win_len)
  { 
    EMG_level=ACC>>7; //reset accumulator and clock 
    ACC=0;
    clk=0;
  }
  /***************************************************************************************** 
   * send on the serial port the EMG-LE signal to be used for Human Machine Interfaces control 
   * *****************************************************************************************/
   Serial.write(EMG_level);
} /***************************************************************************************** SETUP
* * * * **** **** ***** ***** **** ***** ***** **** ***** ***** **** **** ***** **/
void setup(){

  // initialize the serial port to 115200 bps 
  Serial.begin(115200);

  //connect RAW output of EMG sensor to the analog input - pin A1 
  pinMode(A1, INPUT);

  /***************************************************************************************** 
   * For removing 50Hz and higher armonics noise -> set the sampling frequency to 1000Hz 
   * -> DT=1ms -> activate interrupt on timer1 every 1000us
  For removing 60Hz and higher armonics noise -> set the sampling frequency to 1200Hz -> 
  DT=0.833ms -> activate interrupt on timer1 every 833us 
  *****************************************************************************************/ 

  Timer1.initialize(1200);

  // every time there is interrupt on timer1 call the function "EMG_LE"
  Timer1.attachInterrupt(EMG_LE);
} 


/***************************************************************************************** 
 * LOOP 
 * *****************************************************************************************/

void loop(){
  while (1) {}
};