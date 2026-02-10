import unittest
from unittest.mock import patch
from io import StringIO
from PIL import Image
from core.merchants import Merchant

class MerchantTestCase(unittest.TestCase):
    @patch("builtins.print")
    def test_show_portrait(self, mock_print):
        # Create a mock image object
        mock_image = Image.new("RGB", (200, 200), color="red")
        
        # Patch the Image.open() method to return the mock image
        with patch("PIL.Image.open", return_value=mock_image):
            # Create an instance of the Merchant class
            tomas = Merchant("Tomas", {"apple": 10, "banana": 5})
            
            # Call the show_portrait() method
            tomas.show_portrait()
            
            # Check if the portrait was displayed correctly
            expected_output = '<img src="data:image/png;base64,AAAA..."/>'
            mock_print.assert_called_with(expected_output)
            
            # Save the mock image to a temporary file
            temp_file = "temp_image.png"
            mock_image.save(temp_file)
            
            # Display the image in the terminal using an image viewer
            image_viewer_command = "display temp_image.png"
            subprocess.run(image_viewer_command, shell=True)
            
            # Clean up the temporary file
            os.remove(temp_file)

if __name__ == "__main__":
    unittest.main()