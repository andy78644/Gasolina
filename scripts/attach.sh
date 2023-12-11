#!/bin/bash


case $1 in
	db)
	mysql --host 127.0.0.1 --port 3306 --user app -papp app
	;;
	*)
	echo "Options: db"
	;;
esac

