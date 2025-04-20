import folderLoop
from logging_config import logger


def main() -> None:
    """Main function to start folder processing."""
    logger.info("Start!")
    try:
        # Calling the folder loop function
        folderLoop.loop_folder_function()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    else:
        logger.info("Folder processing completed successfully.")
    finally:
        logger.info("End!")


if __name__ == "__main__":
    main()
else:
    logger.info("Module imported. Run from import.")
