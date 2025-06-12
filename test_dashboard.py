"""
Unit tests for the dashboard module.
This is a temporary test file that will be deleted after testing.
"""

import os
import unittest
from unittest.mock import patch, MagicMock, call
import tempfile
import shutil
from datetime import datetime
import pandas as pd
import numpy as np
from PIL import Image

# Import the module we want to test
from ui.dashboard import (
    render_header,
    render_session_metrics,
    render_latest_analysis,
    render_activity_timeline,
    render_screenshot_gallery,
    render_focus_suggestions,
    render_dashboard,
    capture_and_analyze_screen
)

class TestDashboard(unittest.TestCase):
    """Test cases for the dashboard module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test image
        self.test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        img.save(self.test_image_path)
        
        # Create sample analysis data
        self.sample_analysis = {
            "content": "The user is coding in Visual Studio Code",
            "timestamp": datetime.now().isoformat(),
            "image_path": self.test_image_path,
            "is_productive": True,
            "detected_apps": ["Visual Studio Code"],
            "detected_activities": ["coding"]
        }
        
        self.sample_analysis_history = [
            self.sample_analysis,
            {
                "content": "The user is browsing social media",
                "timestamp": datetime.now().isoformat(),
                "image_path": self.test_image_path,
                "is_productive": False,
                "detected_apps": ["Chrome"],
                "detected_activities": ["browsing"]
            }
        ]
        
        # Mock session tracker
        self.mock_session_tracker = MagicMock()
        self.mock_session_tracker.get_productivity_metrics.return_value = {
            "productivity_score": 75,
            "focus_percentage": 80.0,
            "duration_seconds": 3600
        }
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    @patch('streamlit.title')
    @patch('streamlit.write')
    def test_render_header(self, mock_write, mock_title):
        """Test rendering the dashboard header."""
        render_header()
        mock_title.assert_called_once()
        mock_write.assert_called_once()
    
    @patch('streamlit.header')
    @patch('streamlit.columns')
    def test_render_session_metrics(self, mock_columns, mock_header):
        """Test rendering session metrics."""
        # Create mock columns with context manager support
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col3 = MagicMock()
        
        # Setup the context manager for each column
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=None)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=None)
        mock_col3.__enter__ = MagicMock(return_value=mock_col3)
        mock_col3.__exit__ = MagicMock(return_value=None)
        
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Test with all parameters
        session_start_time = datetime.now()
        
        with patch('streamlit.metric') as mock_metric:
            render_session_metrics(
                session_tracker=self.mock_session_tracker,
                analysis_history=self.sample_analysis_history,
                session_start_time=session_start_time
            )
            
            # Check that header was called
            mock_header.assert_called_once()
            
            # Check that columns were created
            mock_columns.assert_called_once_with(3)
            
            # Check that metric was called at least 3 times (once per column)
            self.assertGreaterEqual(mock_metric.call_count, 3)
    
    @patch('streamlit.header')
    @patch('streamlit.columns')
    @patch('streamlit.write')
    @patch('streamlit.success')
    @patch('streamlit.warning')
    @patch('streamlit.info')
    def test_render_latest_analysis(self, mock_info, mock_warning, mock_success, 
                                   mock_write, mock_columns, mock_header):
        """Test rendering the latest analysis."""
        # Create mock columns with context manager support
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        
        # Setup the context manager for each column
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=None)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=None)
        
        mock_columns.return_value = [mock_col1, mock_col2]
        
        # Test with analysis
        render_latest_analysis(self.sample_analysis)
        
        # Check that header was called
        mock_header.assert_called_once()
        
        # Check that columns were created
        mock_columns.assert_called_once()
        
        # Check that success message was displayed (productive work)
        mock_success.assert_called_once()
        
        # Test with no analysis
        mock_header.reset_mock()
        mock_columns.reset_mock()
        mock_success.reset_mock()
        mock_info.reset_mock()
        
        render_latest_analysis(None)
        
        # Check that info message was displayed
        mock_info.assert_called_once()
    
    @patch('streamlit.header')
    @patch('streamlit.dataframe')
    @patch('streamlit.info')
    def test_render_activity_timeline(self, mock_info, mock_dataframe, mock_header):
        """Test rendering the activity timeline."""
        # Test with history
        render_activity_timeline(self.sample_analysis_history)
        
        # Check that header was called
        mock_header.assert_called_once()
        
        # Check that dataframe was created
        mock_dataframe.assert_called_once()
        
        # Test with no history
        mock_header.reset_mock()
        mock_dataframe.reset_mock()
        mock_info.reset_mock()
        
        render_activity_timeline(None)
        
        # Check that info message was displayed
        mock_info.assert_called_once()
    
    @patch('streamlit.header')
    @patch('streamlit.columns')
    @patch('streamlit.info')
    def test_render_screenshot_gallery(self, mock_info, mock_columns, mock_header):
        """Test rendering the screenshot gallery."""
        # Create mock columns with context manager support
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        
        # Setup the context manager for each column
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=None)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=None)
        
        mock_columns.return_value = [mock_col1, mock_col2]
        
        # Test with history
        with patch('streamlit.image'):
            render_screenshot_gallery(self.sample_analysis_history)
            
            # Check that header was called
            mock_header.assert_called_once()
            
            # Check that columns were created
            mock_columns.assert_called_once()
        
        # Test with no history
        mock_header.reset_mock()
        mock_columns.reset_mock()
        mock_info.reset_mock()
        
        render_screenshot_gallery(None)
        
        # Check that info message was displayed
        mock_info.assert_called_once()
    
    @patch('streamlit.header')
    @patch('streamlit.info')
    def test_render_focus_suggestions(self, mock_info, mock_header):
        """Test rendering focus suggestions."""
        # Test with history
        render_focus_suggestions(self.sample_analysis_history)
        
        # Check that header was called
        mock_header.assert_called_once()
        
        # Check that info was called at least once
        mock_info.assert_called()
        
        # Test with no history
        mock_header.reset_mock()
        mock_info.reset_mock()
        
        render_focus_suggestions(None)
        
        # Check that info message was displayed
        mock_info.assert_called_once()
    
    @patch('ui.dashboard.render_header')
    @patch('ui.dashboard.render_session_metrics')
    @patch('ui.dashboard.render_latest_analysis')
    @patch('ui.dashboard.render_screenshot_gallery')
    @patch('ui.dashboard.render_activity_timeline')
    @patch('ui.dashboard.render_focus_suggestions')
    @patch('streamlit.write')
    @patch('streamlit.header')
    @patch('streamlit.columns')
    def test_render_dashboard(self, mock_columns, mock_header, mock_write,
                             mock_render_focus_suggestions, mock_render_activity_timeline,
                             mock_render_screenshot_gallery, mock_render_latest_analysis,
                             mock_render_session_metrics, mock_render_header):
        """Test rendering the complete dashboard."""
        # Create mock columns with context manager support
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col3 = MagicMock()
        
        # Setup the context manager for each column
        mock_col1.__enter__ = MagicMock(return_value=mock_col1)
        mock_col1.__exit__ = MagicMock(return_value=None)
        mock_col2.__enter__ = MagicMock(return_value=mock_col2)
        mock_col2.__exit__ = MagicMock(return_value=None)
        mock_col3.__enter__ = MagicMock(return_value=mock_col3)
        mock_col3.__exit__ = MagicMock(return_value=None)
        
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Test with inactive session
        render_dashboard(session_active=False)
        
        # Check that header was rendered
        mock_render_header.assert_called_once()
        
        # Check that other components were not rendered
        mock_render_session_metrics.assert_not_called()
        mock_render_latest_analysis.assert_not_called()
        mock_render_screenshot_gallery.assert_not_called()
        mock_render_activity_timeline.assert_not_called()
        mock_render_focus_suggestions.assert_not_called()
        
        # Test with active session
        mock_render_header.reset_mock()
        
        render_dashboard(
            session_active=True,
            session_tracker=self.mock_session_tracker,
            analysis_history=self.sample_analysis_history,
            last_analysis=self.sample_analysis,
            session_start_time=datetime.now()
        )
        
        # Check that all components were rendered
        mock_render_header.assert_called_once()
        mock_render_session_metrics.assert_called_once()
        mock_render_latest_analysis.assert_called_once()
        mock_render_screenshot_gallery.assert_called_once()
        mock_render_activity_timeline.assert_called_once()
        mock_render_focus_suggestions.assert_called_once()
    
    @patch('ui.dashboard.ScreenCapture')
    @patch('ui.dashboard.VisionAnalyzer')
    def test_capture_and_analyze_screen(self, mock_vision_analyzer, mock_screen_capture):
        """Test capturing and analyzing the screen."""
        # Mock screen capture
        mock_screen_capture_instance = MagicMock()
        mock_screen_capture.return_value = mock_screen_capture_instance
        mock_screen_capture_instance.capture_screen.return_value = self.test_image_path
        
        # Mock vision analyzer
        mock_vision_analyzer_instance = MagicMock()
        mock_vision_analyzer.return_value = mock_vision_analyzer_instance
        mock_vision_analyzer_instance.analyze_image.return_value = self.sample_analysis
        
        # Call the function
        result = capture_and_analyze_screen()
        
        # Check that screen capture was called
        mock_screen_capture_instance.capture_screen.assert_called_once_with(force=True)
        
        # Check that vision analyzer was called
        mock_vision_analyzer_instance.analyze_image.assert_called_once_with(self.test_image_path)
        
        # Check the result
        self.assertEqual(result, self.sample_analysis)
        
        # Test with failed screen capture
        mock_screen_capture_instance.capture_screen.return_value = None
        
        result = capture_and_analyze_screen()
        
        # Check that vision analyzer was not called
        mock_vision_analyzer_instance.analyze_image.assert_called_once()
        
        # Check the result
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
