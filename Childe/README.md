# Childe
The voice frontend.
## Workflow
1. Keep recording the audio and analyzing the slide window to see if there is a wakeup phrase or not.
2. Once wakeup, proceeding sound will be considered commands and passed to Rex_Lapis.
3. Request to Rex_Lapis will return label or raw audio data for Childe to play audio response. When Childe is playing response audio, it doesn't record nor take in any input.
4. If there is no input for a period of time, the Childe will return dormant again.

## Issues
1. File config.py will read some of the shell env variables to update the configuration. But it is not completed.
2. The system performs calculation to detect wakeup word once per second. No idea whether it works well on Raspberry Pi 4B
3. The variable naming for authentication is not self-explain. Use a username & password manner to start a session when accessing `/wakeup`. Access to `/commands` required to under the setup session.