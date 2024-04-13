# import logging
# import logging.handlers

# # Configure logger
# logger = logging.getLogger('CandidateLogger')
# logger.setLevel(logging.DEBUG)  # Set to debug to catch all messages

# # File handler - to log info and above messages
# file_handler = logging.FileHandler('candidate_import.log')
# file_handler.setLevel(logging.INFO)
# file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(file_formatter)

# # Console handler - to log error and above messages
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.ERROR)
# console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# console_handler.setFormatter(console_formatter)

# # Add handlers to the logger
# logger.addHandler(file_handler)
# logger.addHandler(console_handler)
