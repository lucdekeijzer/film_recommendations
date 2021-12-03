## Orchestrator Component - GSN ##
import Interface_GUI
from subprocess import call

# Get AI model from server
# Navigate to pscp.exe location
cmd = "cd C:\Program Files\PuTTY"
call(cmd)
# Request trained chat model data from our SSH server using pscp
cmd = "pscp Administrator@DESKTOP-9M3DEH6:C:/Users/Administrator/Desktop/Moviebot/chat_model.h5 C:\Users\Ethel\Desktop\Moviebot"
call(cmd)

## GUI interface ## 
Interface_GUI.chatbox()

