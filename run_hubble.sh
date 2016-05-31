#!/bin/bash
docker run -rm --name hubble1 -p 30000:30000 -p 30001:30001 -p 8000:8000 --ink arcus1:arcus -it goodahn/for_hubble
