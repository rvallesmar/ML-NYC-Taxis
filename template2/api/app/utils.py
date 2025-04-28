import hashlib
import os


def allowed_file(filename):
    """
    Checks if the format for the file received is acceptable. For this
    particular case, we must accept only image files. This is, files with
    extension ".png", ".jpg", ".jpeg" or ".gif".

    Parameters
    ----------
    filename : str
        Filename from werkzeug.datastructures.FileStorage file.

    Returns
    -------
    bool
        True if the file is an image, False otherwise.
    """
    # Define the set of allowed file extensions
    ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}
    
    # Get the file extension by splitting the filename and taking the last part
    # Convert to lowercase to handle cases like .PNG, .JPG, etc.
    file_extension = os.path.splitext(filename)[1].lower()
    
    # Check if the extension is in our allowed set
    return file_extension in ALLOWED_EXTENSIONS


async def get_file_hash(file):
    """
    Returns a new filename based on the file content using MD5 hashing.
    It uses hashlib.md5() function from Python standard library to get
    the hash.

    Parameters
    ----------
    file : werkzeug.datastructures.FileStorage
        File sent by user.

    Returns
    -------
    str
        New filename based in md5 file hash.
    """
    # Create an MD5 hash object
    md5_hash = hashlib.md5()
    
    # Read the file content in chunks to handle large files efficiently
    chunk_size = 8192  # 8KB chunks
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        # Update the hash with the chunk
        md5_hash.update(chunk)
    
    # Get the hexadecimal representation of the hash
    file_hash = md5_hash.hexdigest()
    
    # Reset the file pointer to the beginning for future reads
    await file.seek(0)
    
    # Get the original file extension
    _, file_extension = os.path.splitext(file.filename)
    
    # Combine the hash with the original extension
    new_filename = f"{file_hash}{file_extension}"
    
    return new_filename
