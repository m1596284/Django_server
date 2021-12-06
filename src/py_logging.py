# -*- coding: utf-8 -*-
import logging
import time
import datetime
from pathlib import Path

def py_logger(write_mode="a", level="DEBUG", dir_path="with_py_logging.py", file_name="None"):
	if dir_path == "with_py_logging.py":
		dir_path = str(Path(__file__).parent)
	else:
		dir_path = dir_path
	Path(dir_path).mkdir(exist_ok=True)
	logger = logging.getLogger()
	level_mode =  logging.getLevelName(f"{level}")
	logger.setLevel(level_mode)
	formatter = logging.Formatter(
		'[%(levelname)1.1s %(asctime)s %(lineno)d] %(message)s',
		datefmt='%Y_%m%d %H:%M:%S')

	## this is for console
	consoleHandler = logging.StreamHandler()
	consoleHandler.setLevel(level_mode)
	consoleHandler.setFormatter(formatter)
	logger.addHandler(consoleHandler)

	## this is for log file
	log_date = datetime.datetime.now().strftime("%Y_%m%d")
	if file_name == "None":
		file_name = ""
	else:
		file_name = f"_{file_name}"
	fileHandler = logging.FileHandler(f"{dir_path}/{log_date}{file_name}.log",f"{write_mode}","utf-8")
	fileHandler.close()
	# fileHandler.setLevel(logging.DEBUG)
	fileHandler.setFormatter(formatter)
	logger.addHandler(fileHandler)
	return logger

def remove_old_log(dir_path="with_py_logging.py", file_name="None"):
	if dir_path == "with_py_logging.py":
		dir_path = str(Path(__file__).parent)
	else:
		dir_path = dir_path
	if file_name == "None":
		file_name = ""
	else:
		file_name = f"{file_name}"
	path_list = sorted(Path(dir_path).glob("*.log"))
	today_ts = time.mktime(time.strptime(str(datetime.date.today()),"%Y-%m-%d"))
	for log in path_list:
		log_name = Path(log).stem[10:]
		if log_name == file_name:
			log_date = Path(log).stem[0:9]
			log_ts = time.mktime(time.strptime(log_date,"%Y_%m%d"))
			if (today_ts - log_ts) > 60*60*24*3:
				Path(log).unlink()
				print("remove", Path(log).name)