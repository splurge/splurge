#!/bin/sh
wget -r --force-directories ftp://hfdata:DD4hackfest@splurge.scholarsportal.info/* 
rm -rf ./data
mv ./splurge.scholarsportal.info ./data