#!/bin/bash

PORT=

exec uvicorn --port $PORT --log-level $LOG_LEVEL "$APP_MODULE"