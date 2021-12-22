# Rex_Lapis
The center controller & web server.
## Interact with Childe
### Workflow
1. The Childe access `/wakeup` to start a session.
2. The Childe access `/commands` to pass raw audio data.
3. Access Baidu's API to do the Audio2Text task.
4. Pass the text to commands handler.
5. Commands handler search key words in text, map the text to a kill and extract arguments.
6. Corresponding skill is called, with extracted arguments.
7. Commands handler generates the HTTP response.

### Future work
1. Store more infos in the session, to take context into consideration.
2. Change the commands handler to be "datalog-based".