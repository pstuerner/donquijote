#!/bin/bash

# Start both bots
python3 donquijote/bot/remindbot.py &
python3 donquijote/bot/conversationbot.py
  
# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?

