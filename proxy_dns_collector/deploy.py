#!/usr/bin/python3
import os
import shutil
import logging
import sys

# Configuration variables
DEST_DIR = "/root/bin/proxy_dns_collector"
CHMOD_PERMISSIONS = 0o755
CHOWN_UID = None  # Set to desired UID if needed
CHOWN_GID = None  # Set to desired GID if needed
EXCLUDED_FILES = {"deploy.py", ".gitignore", ".git", "README", "LICENSE"}


def configure_logging():
    logger = logging.getLogger("deploy_logger")
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter(fmt="%(message)s")
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)
    return logger


def set_permissions_and_owner(directory, logger):
    try:
        for root, dirs, files in os.walk(directory):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                os.chmod(dir_path, CHMOD_PERMISSIONS)
                if CHOWN_UID is not None and CHOWN_GID is not None:
                    os.chown(dir_path, CHOWN_UID, CHOWN_GID)
                logger.info(
                    "Set permissions and owner on directory: {0}\n".format(dir_path))
            for file_name in files:
                file_path = os.path.join(root, file_name)
                os.chmod(file_path, CHMOD_PERMISSIONS)
                if CHOWN_UID is not None and CHOWN_GID is not None:
                    os.chown(file_path, CHOWN_UID, CHOWN_GID)
                logger.info(
                    "Set permissions and owner on file: {0}\n".format(file_path))
    except Exception as err:
        logger.error("Error setting permissions and owner in directory {0}. {1}".format(
            directory, err))


def prepare_destination_directory(directory, logger):
    if os.path.exists(directory):
        if any(os.listdir(directory)):
            logger.warning(
                "The destination directory {} - exists and is not empty. Files will be overwritten.".format(directory))
            while True:
                response = input(
                    "Continue with deployment? [y/n]: ").strip().lower()
                if response == "y" or response == "д":
                    break
                elif response == "n" or response == "н":
                    logger.info("Deployment aborted by user.")
                    sys.exit(1)
                else:
                    logger.warning("Invalid input. Please enter 'y' or 'n'.")
    else:
        os.makedirs(directory)
        logger.info("Created destination directory: {0}".format(directory))


def copy_config_files(source_dir, dest_dir, logger):
    config_source = os.path.join(source_dir, "config")
    config_dest = os.path.join(dest_dir, "config")

    if os.path.exists(config_source):
        if os.path.exists(config_dest):
            pass
        else:
            shutil.copytree(config_source, config_dest)
            logger.info("Copied 'config' directory from {0} to {1}\n".format(
                config_source, config_dest))
            return True

    config_ini_source = os.path.join(source_dir, "config", "config.ini")
    config_ini_dest = os.path.join(dest_dir, "config", "config.ini")

    if os.path.exists(config_ini_source):
        if os.path.exists(config_ini_dest):
            while True:
                response = input(
                    "The 'config.ini' file already exists in the destination. Overwritte? [y/n]: ").strip().lower()
                if response == "y" or response == "д":
                    shutil.copy2(config_ini_source, config_ini_dest)
                    logger.info("Copied 'config.ini' file from {0} to {1}\n".format(
                        config_ini_source, config_ini_dest))
                    break
                elif response == "n" or response == "н":
                    logger.warning("It will not be overwritten.\n")
                    break
                else:
                    logger.warning("Invalid input. Please enter 'y' or 'n'.")
        else:
            shutil.copy2(config_ini_source, config_ini_dest)
            logger.info("Copied 'config.ini' from {0} to {1}\n".format(
                config_ini_source, config_ini_dest))

    for item in os.listdir(os.path.join(source_dir, "config")):
        if item != "config.ini":
            source_path = os.path.join(source_dir, "config", item)
            destination_path = os.path.join(dest_dir, "config", item)
            if os.path.isdir(source_path):
                shutil.copytree(source_path, destination_path,
                                dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, destination_path)
            logger.info("Copied {0} to {1}\n".format(
                source_path, destination_path))


def main():
    # Configure logging
    logger = configure_logging()
    try:
        # Determine the current directory as PROJECT_DIR
        PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
        # Prepare the destination directory
        prepare_destination_directory(DEST_DIR, logger)
        # Copy all project files to the destination directory, excluding specified files
        for item in os.listdir(PROJECT_DIR):
            if item in EXCLUDED_FILES or item == "config":
                logger.info("Excluded from copying: {0}\n".format(item))
                continue
            source_path = os.path.join(PROJECT_DIR, item)
            destination_path = os.path.join(DEST_DIR, item)
            if os.path.isdir(source_path):
                shutil.copytree(source_path, destination_path,
                                dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, destination_path)
            logger.info("Copied {0} to {1}\n".format(
                source_path, destination_path))
        # Copy config files separately
        copy_config_files(PROJECT_DIR, DEST_DIR, logger)
        # Set permissions and owner for all files and directories in DEST_DIR
        set_permissions_and_owner(DEST_DIR, logger)
        # Output completion message
        logger.info("Project successfully deployed!")
    except KeyboardInterrupt:
        logger.info("\nDeployment interrupted by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
