# -*- coding: utf-8 -*-
import logging
import datetime
from pathlib import Path

def py_logger(write_mode="a", level="DEBUG", dir_path="with_py_logging.py", file_name="None"):
	if dir_path == "with_py_logging.py":
		pyPath = Path(__file__).parent
	else:
		pyPath = dir_path
	Path(pyPath).mkdir(exist_ok=True)
	logger = logging.getLogger()
	level_mode =  logging.getLevelName(f"{level}")
	logger.setLevel(level_mode)
	formatter = logging.Formatter(
		'[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s',
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
	fileHandler = logging.FileHandler(f"{pyPath}/{log_date}{file_name}.log",f"{write_mode}","utf-8")
	# fileHandler.setLevel(logging.DEBUG)
	fileHandler.setFormatter(formatter)
	logger.addHandler(fileHandler)
	return logger