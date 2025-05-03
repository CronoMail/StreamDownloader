import os
import json
import time
import requests
import logging
import re
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs, urlparse

class StreamDownloader:
    """Handles the downloading of stream fragments"""
    
    def __init__(self, user_agent=None, max_retries=10, retry_delay=2):
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.headers = {"User-Agent": self.user_agent}
        self.logger = logging.getLogger("stream_downloader")
    
    def download_data(self, url, cookies=None):
        """Download data from a URL with retries"""
        for attempt in range(self.max_retries):
            try:
                session = requests.Session()
                response = session.get(url, headers=self.headers, cookies=cookies, timeout=15)
                response.raise_for_status()
                return response.content
            except (requests.RequestException, ConnectionError) as e:
                self.logger.warning(f"Download attempt {attempt+1}/{self.max_retries} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"Failed to download {url} after {self.max_retries} attempts")
                    raise
    
    def download_fragment(self, url, output_path, cookies=None):
        """Download a single stream fragment to a file"""
        try:
            data = self.download_data(url, cookies)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(data)
                
            return len(data)
        except Exception as e:
            self.logger.error(f"Failed to download fragment {url}: {str(e)}")
            return 0
    
    def parse_dash_manifest(self, manifest_data):
        """Parse a DASH manifest to get fragment URLs"""
        try:
            root = ET.fromstring(manifest_data)
            namespace = {'ns': 'urn:mpeg:dash:schema:mpd:2011'}
            
            representations = []
            
            for period in root.findall('.//ns:Period', namespace):
                for adapt_set in period.findall('.//ns:AdaptationSet', namespace):
                    for rep in adapt_set.findall('.//ns:Representation', namespace):
                        rep_id = rep.get('id')
                        mime_type = adapt_set.get('mimeType')
                        
                        # Check for either initialization or segment templates
                        init_template = None
                        segment_template = None
                        
                        for template in rep.findall('.//ns:SegmentTemplate', namespace):
                            if 'initialization' in template.attrib:
                                init_template = template.get('initialization')
                            if 'media' in template.attrib:
                                segment_template = template.get('media')
                                
                        base_url = None
                        for url in rep.findall('.//ns:BaseURL', namespace):
                            base_url = url.text
                        
                        representations.append({
                            'id': rep_id,
                            'mime_type': mime_type,
                            'initialization': init_template,
                            'media': segment_template,
                            'base_url': base_url
                        })
            
            return representations
            
        except Exception as e:
            self.logger.error(f"Failed to parse DASH manifest: {str(e)}")
            return []
    
    def parse_m3u8_playlist(self, playlist_data, base_url=None):
        """Parse an HLS (.m3u8) playlist to get fragment URLs"""
        try:
            lines = playlist_data.decode('utf-8').splitlines()
            
            fragments = []
            media_sequence = 0
            
            for i, line in enumerate(lines):
                if line.startswith('#EXT-X-MEDIA-SEQUENCE:'):
                    media_sequence = int(line.split(':')[1])
                
                elif not line.startswith('#') and line.strip():
                    # This is a fragment URL
                    url = line
                    
                    # Make relative URLs absolute
                    if base_url and not url.startswith(('http://', 'https://')):
                        url = base_url + ('/' if not base_url.endswith('/') and not url.startswith('/') else '') + url
                    
                    fragments.append({
                        'url': url,
                        'sequence': media_sequence
                    })
                    
                    media_sequence += 1
            
            return fragments
            
        except Exception as e:
            self.logger.error(f"Failed to parse M3U8 playlist: {str(e)}")
            return []
    
    def get_stream_info(self, url, cookies=None):
        """Get information about a stream URL"""
        try:
            # Different handling for different services
            if 'twitch.tv' in url:
                return self.get_twitch_stream_info(url, cookies)
            elif 'youtube.com' in url or 'youtu.be' in url:
                return self.get_youtube_stream_info(url, cookies)
            else:
                self.logger.error(f"Unsupported URL: {url}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to get stream info: {str(e)}")
            return None
    
    def get_twitch_stream_info(self, url, cookies=None):
        """Get stream information for a Twitch URL"""
        self.logger.info(f"Getting Twitch stream info for: {url}")
        
        # This is simplified - a real implementation would need to use Twitch APIs
        channel = re.search(r'twitch\.tv/([^/]+)', url).group(1)
        
        return {
            'platform': 'twitch',
            'channel': channel,
            'title': f"Twitch stream from {channel}",
            'is_live': True,
            'formats': [
                {'quality': 'best', 'format_id': '1080p60'},
                {'quality': '720p60', 'format_id': '720p60'},
                {'quality': '720p', 'format_id': '720p'},
                {'quality': '480p', 'format_id': '480p'},
                {'quality': '360p', 'format_id': '360p'},
                {'quality': 'audio_only', 'format_id': 'audio_only'}
            ]
        }
    
    def get_youtube_stream_info(self, url, cookies=None):
        """Get stream information for a YouTube URL"""
        self.logger.info(f"Getting YouTube stream info for: {url}")
        
        # Extract video ID
        if 'youtu.be' in url:
            video_id = url.split('/')[-1]
        else:
            query = parse_qs(urlparse(url).query)
            video_id = query.get('v', [None])[0]
        
        if not video_id:
            self.logger.error("Could not extract video ID from YouTube URL")
            return None
        
        return {
            'platform': 'youtube',
            'video_id': video_id,
            'title': f"YouTube stream {video_id}",
            'is_live': True,
            'formats': [
                {'quality': 'best', 'format_id': '1080p'},
                {'quality': '720p', 'format_id': '720p'},
                {'quality': '480p', 'format_id': '480p'},
                {'quality': '360p', 'format_id': '360p'},
                {'quality': 'worst', 'format_id': 'worst'}
            ]
        }
    
    def download_stream_fragments(self, manifest_url, output_dir, quality='best', max_fragments=None, cookies=None):
        """Download stream fragments from a manifest URL"""
        self.logger.info(f"Downloading stream fragments from: {manifest_url}")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Determine manifest type
        if manifest_url.endswith('.mpd'):
            # DASH manifest
            manifest_data = self.download_data(manifest_url, cookies)
            representations = self.parse_dash_manifest(manifest_data)
            
            # Select representation based on quality
            selected_rep = None
            for rep in representations:
                if quality in rep.get('id', ''):
                    selected_rep = rep
                    break
            
            if not selected_rep and representations:
                # If requested quality not found, use first one
                selected_rep = representations[0]
            
            if not selected_rep:
                self.logger.error("No suitable representation found in DASH manifest")
                return False
            
            # TODO: Implement DASH fragment downloading
            self.logger.error("DASH fragment downloading not fully implemented")
            return False
            
        elif manifest_url.endswith('.m3u8'):
            # HLS manifest
            manifest_data = self.download_data(manifest_url, cookies)
            base_url = '/'.join(manifest_url.split('/')[:-1])
            fragments = self.parse_m3u8_playlist(manifest_data, base_url)
            
            if not fragments:
                self.logger.error("No fragments found in HLS playlist")
                return False
            
            # Limit the number of fragments if needed
            if max_fragments:
                fragments = fragments[:max_fragments]
            
            # Download fragments
            for i, fragment in enumerate(fragments):
                fragment_url = fragment['url']
                fragment_path = os.path.join(output_dir, f"fragment_{i:05d}.ts")
                
                bytes_downloaded = self.download_fragment(fragment_url, fragment_path, cookies)
                self.logger.info(f"Downloaded fragment {i+1}/{len(fragments)}: {bytes_downloaded} bytes")
                
                # Save progress
                progress = {
                    'fragments_total': len(fragments),
                    'fragments_downloaded': i + 1,
                    'last_fragment': fragment['sequence'],
                    'last_url': fragment_url
                }
                
                with open(os.path.join(output_dir, 'progress.json'), 'w') as f:
                    json.dump(progress, f)
            
            return True
        else:
            self.logger.error(f"Unsupported manifest type: {manifest_url}")
            return False
