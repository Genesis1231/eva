from config import logger
import webbrowser
import os

class Window:
    """
    Window class to open a new window with HTML content or a URL.
    
    Methods:
    - launch_html: Open a new window with HTML content.
    - launch_url: Open a new window with a URL.
    
    """
    def __init__(self):
        self.browser = None
        self._window_width = 450
        self._window_height = 600
        
    def launch_html(self, html_content, new: bool = False)-> None:
        # Create a temporary file to store the HTML content
        temp_path = os.path.join(os.path.dirname(__file__), "temp", "window.html")
        window_index = 1 if new else 0
        
        with open(temp_path, 'w', encoding='utf-8') as file:
            html_content = html_content.replace("</title>", 
                f"</title><script type='text/javascript'>window.onload = window.resizeTo({self._window_width}, {self._window_height}); </script>")
            file.write(html_content)

        # Open the html in the default web browser
        if not self.browser:
            self.browser = webbrowser.get()
        self.browser.open(temp_path, new=window_index)

    def launch_url(self, url: str, new: bool = False)-> None:
        window_index = 1 if new else 0
        
        if not self.browser:
            self.browser = webbrowser.get() 
        
        self.browser.open(url, new=window_index)

        