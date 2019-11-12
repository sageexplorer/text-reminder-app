#!/bin/bash

aws events put-rule --schedule-expression "cron(5 * * * ? *)" --name checkMessage
