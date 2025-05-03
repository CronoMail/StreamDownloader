import os
import subprocess
import shutil
import logging
import re
import tempfile
from pathlib import Path
import tempfile
import re

logger = logging.getLogger("stream_merger")

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return result.returncode == 0
    except Exception:
        return False

def merge_ts_files(input_dir, output_file, ffmpeg_path="ffmpeg"):
    """Merge .ts fragment files into a single output file using FFmpeg"""
    try:
        # Find all fragment files and sort them numerically
        fragments = sorted(
            [f for f in os.listdir(input_dir) if f.startswith("fragment_") and f.endswith(".ts")],
            key=lambda x: int(x.split("_")[1].split(".")[0])
        )
        
        if not fragments:
            logger.error("No fragment files found to merge")
            return False
        
        # Create a temporary file list for FFmpeg
        file_list_path = os.path.join(input_dir, "filelist.txt")
        with open(file_list_path, "w") as f:
            for fragment in fragments:
                f.write(f"file '{os.path.join(input_dir, fragment)}'\n")
        
        # Build FFmpeg command
        cmd = [
            ffmpeg_path,
            "-f", "concat",
            "-safe", "0",
            "-i", file_list_path,
            "-c", "copy",
            "-y",  # Overwrite output file if it exists
            output_file
        ]
        
        logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
        
        # Run FFmpeg to merge the files
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Remove the temporary file list
        if os.path.exists(file_list_path):
            os.remove(file_list_path)
        
        if result.returncode == 0:
            logger.info(f"Successfully merged {len(fragments)} fragment files into {output_file}")
            return True
        else:
            logger.error(f"FFmpeg merge failed with exit code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error merging TS files: {str(e)}")
        return False

def add_metadata(input_file, output_file, metadata, ffmpeg_path="ffmpeg"):
    """Add metadata to a video file using FFmpeg"""
    try:
        # Build FFmpeg command with metadata
        cmd = [ffmpeg_path, "-i", input_file, "-c", "copy"]
        
        # Add metadata options
        for key, value in metadata.items():
            if value:  # Only add if value is not empty
                cmd.extend(["-metadata", f"{key}={value}"])
        
        cmd.extend(["-y", output_file])
        
        logger.info(f"Running FFmpeg metadata command: {' '.join(cmd)}")
        
        # Run FFmpeg to add metadata
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully added metadata to {output_file}")
            return True
        else:
            logger.error(f"FFmpeg metadata addition failed with exit code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error adding metadata: {str(e)}")
        return False

def embed_thumbnail(input_file, thumbnail_path, output_file, ffmpeg_path="ffmpeg"):
    """Embed a thumbnail into a video file using FFmpeg"""
    try:
        # Build FFmpeg command
        cmd = [
            ffmpeg_path,
            "-i", input_file,
            "-i", thumbnail_path,
            "-map", "0", "-map", "1",
            "-c", "copy",
            "-disposition:v:1", "attached_pic",
            "-y", output_file
        ]
        
        logger.info(f"Running FFmpeg thumbnail command: {' '.join(cmd)}")
        
        # Run FFmpeg to embed thumbnail
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully embedded thumbnail into {output_file}")
            return True
        else:
            logger.error(f"FFmpeg thumbnail embedding failed with exit code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error embedding thumbnail: {str(e)}")
        return False

def clean_up_fragments(directory, keep_fragments=False):
    """Clean up fragment files after merging"""
    if keep_fragments:
        logger.info("Keeping fragment files as requested")
        return True
    
    try:
        fragments = [f for f in os.listdir(directory) if f.startswith("fragment_") and f.endswith(".ts")]
        
        for fragment in fragments:
            os.remove(os.path.join(directory, fragment))
            
        progress_file = os.path.join(directory, "progress.json")
        if os.path.exists(progress_file):
            os.remove(progress_file)
            
        logger.info(f"Cleaned up {len(fragments)} fragment files")
        return True
        
    except Exception as e:
        logger.error(f"Error cleaning up fragments: {str(e)}")
        return False

def process_stream_download(fragments_dir, output_file, options=None):
    """Process a completed stream download, merging fragments and adding metadata"""
    options = options or {}
    ffmpeg_path = options.get("ffmpeg_path", "ffmpeg")
    keep_fragments = options.get("keep_fragments", False)
    metadata = options.get("metadata", {})
    thumbnail_path = options.get("thumbnail_path", None)
    
    # Check if fragments directory exists
    if not os.path.exists(fragments_dir):
        logger.error(f"Fragments directory not found: {fragments_dir}")
        return False
    
    # Check if FFmpeg is available
    if not check_ffmpeg():
        logger.error("FFmpeg not found. Please install FFmpeg or specify the correct path.")
        return False
    
    # Create temporary file for intermediate steps
    temp_dir = os.path.dirname(output_file)
    temp_file = os.path.join(temp_dir, f"temp_{os.path.basename(output_file)}")
    
    # Step 1: Merge TS files
    logger.info(f"Merging fragment files from {fragments_dir} to {temp_file}")
    if not merge_ts_files(fragments_dir, temp_file, ffmpeg_path):
        return False
    
    # Step 2: Add metadata if needed
    if metadata:
        logger.info(f"Adding metadata to {temp_file}")
        metadata_file = os.path.join(temp_dir, f"meta_{os.path.basename(output_file)}")
        if not add_metadata(temp_file, metadata_file, metadata, ffmpeg_path):
            # If metadata addition fails, continue with the merged file
            shutil.copy(temp_file, metadata_file)
        os.remove(temp_file)
        temp_file = metadata_file
    
    # Step 3: Embed thumbnail if needed
    if thumbnail_path and os.path.exists(thumbnail_path):
        logger.info(f"Embedding thumbnail {thumbnail_path} into {temp_file}")
        if not embed_thumbnail(temp_file, thumbnail_path, output_file, ffmpeg_path):
            # If thumbnail embedding fails, use the file from the previous step
            shutil.copy(temp_file, output_file)
        os.remove(temp_file)
    else:
        # No thumbnail, just rename the temp file
        shutil.move(temp_file, output_file)
    
    # Step 4: Clean up fragments if not keeping them
    if not keep_fragments:
        clean_up_fragments(fragments_dir, keep_fragments)
    
    logger.info(f"Stream processing complete. Output file: {output_file}")
    return True

# Function for the CLI to use
def merge_stream_fragments(fragments_dir, output_file, metadata=None, thumbnail=None, callback=None):
    """
    Merge downloaded stream fragments into a single file
    
    Args:
        fragments_dir: Directory containing fragment files
        output_file: Path to the output file
        metadata: Dictionary of metadata to embed
        thumbnail: Path to thumbnail image
        callback: Function to call with progress updates
    
    Returns:
        Path to the merged file
    """
    if callback:
        callback("info", 0, "Merging stream fragments...")
    
    # Find TS fragments
    fragments = sorted([
        os.path.join(fragments_dir, f) for f in os.listdir(fragments_dir)
        if f.startswith("fragment_") and f.endswith(".ts")
    ], key=lambda x: int(os.path.basename(x).split("_")[1].split(".")[0]))
    
    if not fragments:
        if callback:
            callback("error", 0, "No fragments found to merge")
        raise ValueError("No fragments found to merge")
    
    # Create a temporary file for the list of fragments
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        for fragment in fragments:
            temp_file.write(f"file '{fragment}'\n")
        temp_file_path = temp_file.name
    
    try:
        # Basic FFmpeg command to concatenate files
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', temp_file_path,
            '-c', 'copy'
        ]
        
        # Add thumbnail if provided
        if thumbnail and os.path.exists(thumbnail):
            ffmpeg_cmd.extend([
                '-i', thumbnail,
                '-map', '0', '-map', '1',
                '-c', 'copy',
                '-disposition:v:1', 'attached_pic'
            ])
        
        # Add metadata if provided
        if metadata:
            for key, value in metadata.items():
                if value:
                    ffmpeg_cmd.extend(['-metadata', f'{key}={value}'])
        
        # Output file
        ffmpeg_cmd.append(output_file)
        
        # Execute FFmpeg
        if callback:
            callback("progress", 50, "Running FFmpeg to merge fragments...")
        
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Monitor progress
        duration_match = None
        progress = 0
        
        for line in process.stderr:
            # Try to extract progress information
            time_match = re.search(r'time=(\d+:\d+:\d+.\d+)', line)
            if time_match and duration_match:
                time_str = time_match.group(1)
                h, m, s = map(float, time_str.split(':'))
                current_seconds = h * 3600 + m * 60 + s
                total_seconds = duration_match
                progress = min(95, (current_seconds / total_seconds) * 100)
                
                if callback:
                    callback("progress", progress, f"Merging: {progress:.1f}%")
        
        # Wait for process to finish
        process.wait()
        
        # Check if successful
        if process.returncode != 0:
            if callback:
                callback("error", 0, "FFmpeg failed to merge fragments")
            raise RuntimeError(f"FFmpeg failed with return code {process.returncode}")
        
        if callback:
            callback("progress", 100, "Merge completed successfully")
        
        return output_file
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
