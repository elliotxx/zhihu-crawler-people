#!/bin/bash
ps -ef | grep "info_crawler" | grep -v grep | cut -c 10-15 | xargs kill -9
